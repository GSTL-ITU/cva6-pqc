#include <stddef.h>
#include <stdint.h>
#include "../falcon.h"
#include "test_print.h"

#ifndef FALCON_LOGN
#define FALCON_LOGN 9 // Default to FN-512
#endif

#define NTESTS 1
#define MSG_LEN 33

// Constants for Falcon reference implementation
#ifndef FALCON_SIG_COMPRESSED
#define FALCON_SIG_COMPRESSED 1
#endif

// Bare-metal friendly memory comparison
static int custom_memcmp(const void *s1, const void *s2, size_t n) {
    const unsigned char *p1 = s1;
    const unsigned char *p2 = s2;
    for (size_t i = 0; i < n; i++) {
        if (p1[i] != p2[i]) {
            return p1[i] - p2[i];
        }
    }
    return 0;
}

void *memmove(void *dest, const void *src, size_t n) {
    unsigned char *d = (unsigned char *)dest;
    const unsigned char *s = (const unsigned char *)src;
    if (d == s || n == 0) return dest;
    if (d < s) {
        while (n--) *d++ = *s++;
    } else {
        d += n;
        s += n;
        while (n--) *(--d) = *(--s);
    }
    return dest;
}

// Find the maximum temporary buffer size needed by Falcon operations
static size_t get_max_tmp_size(void) {
    size_t max_sz = FALCON_TMPSIZE_KEYGEN(FALCON_LOGN);
    if (FALCON_TMPSIZE_SIGNDYN(FALCON_LOGN) > max_sz) {
        max_sz = FALCON_TMPSIZE_SIGNDYN(FALCON_LOGN);
    }
    if (FALCON_TMPSIZE_VERIFY(FALCON_LOGN) > max_sz) {
        max_sz = FALCON_TMPSIZE_VERIFY(FALCON_LOGN);
    }
    return max_sz;
}

static int test_sign_verify(void)
{
    shake256_context rng;
    shake256_init_prng_from_system(&rng);

    size_t tmp_size = get_max_tmp_size();
    // Force 8-byte alignment for RISC-V floating-point emulation buffers
    __attribute__((aligned(8))) uint8_t tmp[tmp_size];
    
    uint8_t privkey[FALCON_PRIVKEY_SIZE(FALCON_LOGN)];
    uint8_t pubkey[FALCON_PUBKEY_SIZE(FALCON_LOGN)];
    uint8_t sig[FALCON_SIG_COMPRESSED_MAXSIZE(FALCON_LOGN)];
    size_t sig_len = 0;
    
    uint8_t msg[MSG_LEN];
    for (int i = 0; i < MSG_LEN; i++) {
        msg[i] = i ^ 0x55; // Dummy message
    }

#ifdef PRINT_CYCLES
    uint32_t start_cycles;
    uint32_t end_cycles;
#endif

    print_str("Generating keypair...\n");
#ifdef PRINT_CYCLES
    start_cycles = get_cycles();
#endif
    int res = falcon_keygen_make(&rng, FALCON_LOGN, privkey, sizeof(privkey), pubkey, sizeof(pubkey), tmp, tmp_size);
#ifdef PRINT_CYCLES
    end_cycles = get_cycles();
    print_str("Keypair generation cycle count: ");
    print_int(end_cycles - start_cycles);
    print_str("\n");
#endif
    if (res != 0) {
        print_str("ERROR: Keygen failed!\n");
        return 1;
    }

    print_str("Signing message...\n");
#ifdef PRINT_CYCLES
    start_cycles = get_cycles();
#endif
    res = falcon_sign_dyn(&rng, sig, &sig_len, FALCON_SIG_COMPRESSED, privkey, sizeof(privkey), msg, MSG_LEN, tmp, tmp_size);
#ifdef PRINT_CYCLES
    end_cycles = get_cycles();
    print_str("Signature generation cycle count: ");
    print_int(end_cycles - start_cycles);
    print_str("\n");
#endif
    if (res != 0) {
        print_str("ERROR: Signing failed!\n");
        return 1;
    }

    print_str("Verifying signature...\n");
#ifdef PRINT_CYCLES
    start_cycles = get_cycles();
#endif
    res = falcon_verify(sig, sig_len, FALCON_SIG_COMPRESSED, pubkey, sizeof(pubkey), msg, MSG_LEN, tmp, tmp_size);
#ifdef PRINT_CYCLES
    end_cycles = get_cycles();
    print_str("Signature verification cycle count: ");
    print_int(end_cycles - start_cycles);
    print_str("\n");
#endif
    if (res != 0) {
        print_str("ERROR: Verification failed on valid signature!\n");
        return 1;
    }

    print_str("Signature verified successfully.\n");
    return 0;
}

static int test_invalid_signature(void)
{
    shake256_context rng;
    shake256_init_prng_from_system(&rng);
    
    size_t tmp_size = get_max_tmp_size();
    __attribute__((aligned(8))) uint8_t tmp[tmp_size];
    
    uint8_t privkey[FALCON_PRIVKEY_SIZE(FALCON_LOGN)];
    uint8_t pubkey[FALCON_PUBKEY_SIZE(FALCON_LOGN)];
    uint8_t sig[FALCON_SIG_COMPRESSED_MAXSIZE(FALCON_LOGN)];
    size_t sig_len = 0;
    
    uint8_t msg[MSG_LEN] = {0xAA};

    falcon_keygen_make(&rng, FALCON_LOGN, privkey, sizeof(privkey), pubkey, sizeof(pubkey), tmp, tmp_size);
    falcon_sign_dyn(&rng, sig, &sig_len, FALCON_SIG_COMPRESSED, privkey, sizeof(privkey), msg, MSG_LEN, tmp, tmp_size);

    // Corrupt the signature by flipping a bit
    if (sig_len > 10) {
        sig[sig_len / 2] ^= 0x01;
    }

    int res = falcon_verify(sig, sig_len, FALCON_SIG_COMPRESSED, pubkey, sizeof(pubkey), msg, MSG_LEN, tmp, tmp_size);
    
    // If verification SUCCEEDS despite a corrupted signature, it's a failure
    if (res == 0) {
        print_str("ERROR: Verification succeeded with corrupted signature!\n");
        return 1;
    }

    print_str("Invalid signature rejected correctly.\n");
    return 0;
}

int main(void)
{
    unsigned int i;
    int r = 0;

    print_str("Falcon Signature Test Started...\n");

    for (i = 0; i < NTESTS; i++) {
        print_str("\n--- Running Test Iteration ");
        print_int(i + 1);
        print_str(" ---\n");

        r |= test_sign_verify();
        r |= test_invalid_signature();
        
        if (r) {
            print_str("\nTEST FAILED\n");
            return -1;
        }
    }

    print_str("\nALL TESTS PASSED\n");

    print_str("FALCON_LOGN = ");
    print_int(FALCON_LOGN);
    print_str("\nFALCON_PRIVKEY_SIZE = ");
    print_int(FALCON_PRIVKEY_SIZE(FALCON_LOGN));
    print_str("\nFALCON_PUBKEY_SIZE = ");
    print_int(FALCON_PUBKEY_SIZE(FALCON_LOGN));
    print_str("\nFALCON_SIG_COMPRESSED_MAXSIZE = ");
    print_int(FALCON_SIG_COMPRESSED_MAXSIZE(FALCON_LOGN));
    print_str("\n");

    return 0;
}
#include <stddef.h>
#include <stdint.h>
#include "../kem.h"
#include "../randombytes.h"
#include "test_print.h"

#define NTESTS 1

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

static int test_keys(void)
{
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
  uint8_t key_a[CRYPTO_BYTES];
  uint8_t key_b[CRYPTO_BYTES];

  print_str("Generating keypair...\n");
  crypto_kem_keypair(pk, sk);

  print_str("Encapsulating secret...\n");
  crypto_kem_enc(ct, key_b, pk);

  print_str("Decapsulating secret...\n");
  crypto_kem_dec(key_a, ct, sk);

  if(custom_memcmp(key_a, key_b, CRYPTO_BYTES) != 0) {
    print_str("ERROR: Shared secrets do not match!\n");
    return 1; 
  }
  
  print_str("Shared secrets match.\n");
  return 0; 
}

static int test_invalid_sk_a(void)
{
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
  uint8_t key_a[CRYPTO_BYTES];
  uint8_t key_b[CRYPTO_BYTES];

  crypto_kem_keypair(pk, sk);
  crypto_kem_enc(ct, key_b, pk);

  // Replace secret key with random values
  randombytes(sk, CRYPTO_SECRETKEYBYTES);
  crypto_kem_dec(key_a, ct, sk);

  // If the shared secrets MATCH despite a corrupted secret key, it's a failure
  if(custom_memcmp(key_a, key_b, CRYPTO_BYTES) == 0) {
    print_str("ERROR: Decapsulation succeeded with invalid secret key!\n");
    return 1;
  }

  print_str("Invalid secret key rejected correctly.\n");
  return 0;
}

static int test_invalid_ciphertext(void)
{
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];
  uint8_t ct[CRYPTO_CIPHERTEXTBYTES];
  uint8_t key_a[CRYPTO_BYTES];
  uint8_t key_b[CRYPTO_BYTES];
  uint8_t b;
  size_t pos;

  do {
    randombytes(&b, sizeof(uint8_t));
  } while(!b);
  randombytes((uint8_t *)&pos, sizeof(size_t));

  crypto_kem_keypair(pk, sk);
  crypto_kem_enc(ct, key_b, pk);

  // Change a byte in the ciphertext
  ct[pos % CRYPTO_CIPHERTEXTBYTES] ^= b;
  crypto_kem_dec(key_a, ct, sk);

  // If the shared secrets MATCH despite a corrupted ciphertext, it's a failure
  if(custom_memcmp(key_a, key_b, CRYPTO_BYTES) == 0) {
    print_str("ERROR: Decapsulation succeeded with corrupted ciphertext!\n");
    return 1;
  }

  print_str("Invalid ciphertext rejected correctly.\n");
  return 0;
}

int main(void)
{
  unsigned int i;
  int r = 0;

  print_str("Kyber KEM Test Started...\n");

  for(i = 0; i < NTESTS; i++) {
    print_str("\n--- Running Test Iteration ");
    print_int(i + 1);
    print_str(" ---\n");

    r |= test_keys();
    r |= test_invalid_sk_a();
    r |= test_invalid_ciphertext();
    
    if(r) {
      print_str("\nTEST FAILED\n");
      return -1;
    }
  }

  print_str("\nALL TESTS PASSED\n");

  print_str("CRYPTO_PUBLICKEYBYTES = ");
  print_int(CRYPTO_PUBLICKEYBYTES);
  print_str("\nCRYPTO_SECRETKEYBYTES = ");
  print_int(CRYPTO_SECRETKEYBYTES);
  print_str("\nCRYPTO_CIPHERTEXTBYTES = ");
  print_int(CRYPTO_CIPHERTEXTBYTES);
  print_str("\nCRYPTO_BYTES = ");
  print_int(CRYPTO_BYTES);
  print_str("\n");

  return 0;
}
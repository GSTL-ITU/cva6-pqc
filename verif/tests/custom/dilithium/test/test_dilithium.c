#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include "../randombytes.h"
#include "../sign.h"
#include "test_print.h"

#define MLEN 59
#define CTXLEN 14
#define NTESTS 1

int main(void)
{
  size_t i, j;
  int ret;
  size_t mlen, smlen;
  uint8_t b;
  uint8_t ctx[CTXLEN] = {0};
  uint8_t m[MLEN + CRYPTO_BYTES];
  uint8_t m2[MLEN + CRYPTO_BYTES];
  uint8_t sm[MLEN + CRYPTO_BYTES];
  uint8_t pk[CRYPTO_PUBLICKEYBYTES];
  uint8_t sk[CRYPTO_SECRETKEYBYTES];

#ifdef PRINT_CYCLES
  uint32_t start_cycles;
  uint32_t end_cycles;
#endif
  print_str("Initial message, test started...\n");

  for(i = 0; i < NTESTS; ++i) {
    print_str("Generating random message (MLEN=");
    print_int(MLEN);
    print_str(")...\n");
    randombytes(m, MLEN);

    print_str("Generating keypair...\n");
#ifdef PRINT_CYCLES
    start_cycles = get_cycles();
#endif
    crypto_sign_keypair(pk, sk);
#ifdef PRINT_CYCLES
    end_cycles = get_cycles();
    print_str("Keypair generation cycle count: ");
    print_int(end_cycles - start_cycles);
#endif

    print_str("\nSigning message...\n");
#ifdef PRINT_CYCLES
    start_cycles = get_cycles();
#endif
    crypto_sign(sm, &smlen, m, MLEN, ctx, CTXLEN, sk);
#ifdef PRINT_CYCLES
    end_cycles = get_cycles();
    print_str("Signature generation cycle count: ");
    print_int(end_cycles - start_cycles);
#endif
    
    print_str("\nVerifying message...\n");
#ifdef PRINT_CYCLES
    start_cycles = get_cycles();
#endif
    ret = crypto_sign_open(m2, &mlen, sm, smlen, ctx, CTXLEN, pk);
#ifdef PRINT_CYCLES
    end_cycles = get_cycles();
    print_str("Signature verification cycle count: ");
    print_int(end_cycles - start_cycles);
    print_str("\n");
#endif

    if(ret) {
      print_str("Verification failed\n");
      return -1;
    }
    print_str("Verification passed\n");
    
    if(smlen != MLEN + CRYPTO_BYTES) {
      print_str("Signed message lengths wrong\n");
      return -1;
    }
    print_str("Signed message lengths correct\n");

    if(mlen != MLEN) {
      print_str("Message lengths wrong\n");
      return -1;
    }
    print_str("Message lengths correct\n");
    
    for(j = 0; j < MLEN; ++j) {
      if(m2[j] != m[j]) {
        print_str("Messages don't match\n");
        return -1;
      }
    }
    print_str("Messages match\n");

    randombytes((uint8_t *)&j, sizeof(j));
    do {
      randombytes(&b, 1);
    } while(!b);
    sm[j % (MLEN + CRYPTO_BYTES)] += b;
    ret = crypto_sign_open(m2, &mlen, sm, smlen, ctx, CTXLEN, pk);
    if(!ret) {
      print_str("Trivial forgeries possible\n");
      return -1;
    }
  }

  print_str("CRYPTO_PUBLICKEYBYTES =");
  print_int(CRYPTO_PUBLICKEYBYTES);
  print_str("\nCRYPTO_SECRETKEYBYTES =");
  print_int(CRYPTO_SECRETKEYBYTES);
  print_str("\nCRYPTO_BYTES =");
  print_int(CRYPTO_BYTES);
  print_str("\n");

  return 0;
}

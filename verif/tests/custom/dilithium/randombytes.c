#include "randombytes.h"
#include <stdint.h>
#include <stddef.h>

// The internal state variable. 
// Note: It must be initialized to a non-zero value.
static uint32_t prng_state = 123456789; 

// Simple Xorshift32 algorithm to generate a 32-bit pseudo-random integer
static uint32_t xorshift32(void) {
    uint32_t x = prng_state;
    x ^= x << 13;
    x ^= x >> 17;
    x ^= x << 5;
    prng_state = x;
    return x;
}

void randombytes(uint8_t *out, size_t outlen) {
    while (outlen > 0) {
        // Generate 4 bytes of pseudo-random data
        uint32_t rnd = xorshift32();
        
        // Extract bytes from the 32-bit integer and copy them to the buffer
        for (int i = 0; i < 4 && outlen > 0; i++) {
            *out++ = (uint8_t)(rnd >> (i * 8));
            outlen--;
        }
    }
}
#ifndef RANDOMBYTES_H
#define RANDOMBYTES_H

#include <stddef.h>
#include <stdint.h>

static uint32_t xorshift32(void);
void randombytes(uint8_t *out, size_t outlen);

#endif

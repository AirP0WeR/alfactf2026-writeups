#ifndef BACKPACK_CRYPTO_H
#define BACKPACK_CRYPTO_H

#include "common.h"
#include "buffer.h"

int aes_encrypt_cbc(const unsigned char *plaintext, size_t plaintext_len, Buffer *output);

int aes_decrypt_cbc(const unsigned char *input, size_t input_len, Buffer *output);

int decrypt_first_two_blocks(const unsigned char *input, size_t input_len,
                             unsigned char plaintext[GZIP_PEEK_SIZE]);

#endif

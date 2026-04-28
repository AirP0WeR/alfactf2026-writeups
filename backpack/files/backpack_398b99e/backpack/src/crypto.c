#include "crypto.h"
#include <openssl/evp.h>
#include <openssl/rand.h>
#include <stdio.h>
#include <string.h>

unsigned char g_session_key[AES_KEY_SIZE] = {0};

int init_session_key(void) {
    if (RAND_bytes(g_session_key, AES_KEY_SIZE) != 1) {
        fprintf(stderr, "failed to generate session key\n");
        return 0;
    }
    return 1;
}

static void print_openssl_error(const char *message) {
    fprintf(stderr, "%s\n", message);
}

int aes_encrypt_cbc(const unsigned char *plaintext, size_t plaintext_len, Buffer *output) {
    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (ctx == NULL) {
        print_openssl_error("failed to create encryption context");
        return 0;
    }

    unsigned char iv[AES_BLOCK_SIZE];
    if (RAND_bytes(iv, sizeof(iv)) != 1) {
        print_openssl_error("failed to generate IV");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    size_t max_len = AES_BLOCK_SIZE + plaintext_len + AES_BLOCK_SIZE;
    if (!buffer_reserve(output, max_len)) {
        fprintf(stderr, "memory allocation failed\n");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    memcpy(output->data, iv, sizeof(iv));

    if (EVP_EncryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, g_session_key, iv) != 1) {
        print_openssl_error("failed to initialize AES-CBC encryption");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    int produced = 0;
    int final_len = 0;
    if (EVP_EncryptUpdate(ctx, output->data + AES_BLOCK_SIZE, &produced, plaintext, (int)plaintext_len) != 1) {
        print_openssl_error("failed during AES-CBC encryption");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    if (EVP_EncryptFinal_ex(ctx, output->data + AES_BLOCK_SIZE + produced, &final_len) != 1) {
        print_openssl_error("failed to finalize AES-CBC encryption");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    output->len = AES_BLOCK_SIZE + (size_t)produced + (size_t)final_len;
    EVP_CIPHER_CTX_free(ctx);
    return 1;
}

int aes_decrypt_cbc(const unsigned char *input, size_t input_len, Buffer *output) {
    if (input_len <= AES_BLOCK_SIZE || ((input_len - AES_BLOCK_SIZE) % AES_BLOCK_SIZE) != 0) {
        fprintf(stderr, "ciphertext has invalid length\n");
        return 0;
    }

    const unsigned char *iv = input;
    const unsigned char *ciphertext = input + AES_BLOCK_SIZE;
    size_t ciphertext_len = input_len - AES_BLOCK_SIZE;

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (ctx == NULL) {
        print_openssl_error("failed to create decryption context");
        return 0;
    }

    if (!buffer_reserve(output, ciphertext_len)) {
        fprintf(stderr, "memory allocation failed\n");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    if (EVP_DecryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, g_session_key, iv) != 1) {
        print_openssl_error("failed to initialize AES-CBC decryption");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    int produced = 0;
    int final_len = 0;
    if (EVP_DecryptUpdate(ctx, output->data, &produced, ciphertext, (int)ciphertext_len) != 1) {
        print_openssl_error("failed during AES-CBC decryption");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    if (EVP_DecryptFinal_ex(ctx, output->data + produced, &final_len) != 1) {
        fprintf(stderr, "ciphertext decryption failed\n");
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    output->len = (size_t)produced + (size_t)final_len;
    EVP_CIPHER_CTX_free(ctx);
    return 1;
}

int decrypt_first_two_blocks(const unsigned char *input, size_t input_len,
                             unsigned char plaintext[GZIP_PEEK_SIZE]) {
    if (input_len < AES_BLOCK_SIZE + AES_BLOCK_SIZE) {
        return 0;
    }

    size_t ciphertext_len = input_len - AES_BLOCK_SIZE;
    size_t decrypt_len = ciphertext_len < GZIP_PEEK_SIZE ? ciphertext_len : GZIP_PEEK_SIZE;
    
    decrypt_len = (decrypt_len / AES_BLOCK_SIZE) * AES_BLOCK_SIZE;
    if (decrypt_len == 0) {
        return 0;
    }

    EVP_CIPHER_CTX *ctx = EVP_CIPHER_CTX_new();
    if (ctx == NULL) {
        return 0;
    }

    if (EVP_DecryptInit_ex(ctx, EVP_aes_128_cbc(), NULL, g_session_key, input) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }
    if (EVP_CIPHER_CTX_set_padding(ctx, 0) != 1) {
        EVP_CIPHER_CTX_free(ctx);
        return 0;
    }

    memset(plaintext, 0, GZIP_PEEK_SIZE);

    int out_len = 0;
    int final_len = 0;
    int ok = EVP_DecryptUpdate(ctx, plaintext, &out_len, input + AES_BLOCK_SIZE, (int)decrypt_len) == 1 &&
             EVP_DecryptFinal_ex(ctx, plaintext + out_len, &final_len) == 1 &&
             (out_len + final_len) == (int)decrypt_len;
    EVP_CIPHER_CTX_free(ctx);
    return ok;
}

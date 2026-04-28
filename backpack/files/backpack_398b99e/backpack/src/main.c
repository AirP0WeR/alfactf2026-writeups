#include "common.h"
#include "server.h"

#include <openssl/evp.h>
#include <stdio.h>
#include <string.h>



static const char *storage_dir_or_default(const char *value) {
    return value != NULL ? value : "storage";
}

int main(int argc, char **argv) {

    OpenSSL_add_all_algorithms();

    return handle_serve(storage_dir_or_default(argc == 2 ? argv[1] : NULL));
}

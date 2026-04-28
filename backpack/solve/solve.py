#!/usr/bin/env python3
"""
CBC padding-oracle attack on the Digital Backpack server.

The server stores the flag with AES-128-CBC (no gzip wrapping). The session
key is freshly generated on every TCP connection -- so the entire attack
must run within ONE connection.

Oracle: `get <name>` runs full PKCS#7 CBC decryption.
    bad PKCS#7  -> "ciphertext decryption failed\n"
    good PKCS#7 -> proceeds to gzip-header check; messages don't contain
                   "ciphertext decryption failed".

Per-query workflow (one connection, flag stays present):
    1. put-raw IV'||C  (fresh blob, 32 bytes, random id)
    2. determine which of "unknown_file_1" / "unknown_file_2" is OUR blob
       (the flag is 96 bytes, ours is 32 bytes)
    3. get OUR_NAME    => oracle answer
    4. rm OUR_NAME

Files are listed sorted by random id, so flag/blob names swap arbitrarily.
We disambiguate via get-raw size.
"""

import argparse
import os
import sys
import time

from pwn import remote, context

context.log_level = 'error'

BLOCK = 16


UNZIP_CODE = b'6D5LCc1QprneFFb5adiPOQ'


class Backpack:
    def __init__(self, host, port, unzip_code=UNZIP_CODE):
        self.r = remote(host, port)
        # Real server gates with "Unzip the backpack: " prompt; local docker
        # build does not. Detect by reading the first chunk and acting on it.
        first = self.r.recvuntil((b'Unzip the backpack: ', b'backpack> '), timeout=5)
        if b'Unzip the backpack:' in first:
            self.r.sendline(unzip_code)
            self.r.recvuntil(b'backpack> ')
        # else we already ate up to "backpack> "

    def close(self):
        try:
            self.r.close()
        except Exception:
            pass

    def cmd(self, line):
        self.r.sendline(line.encode() if isinstance(line, str) else line)
        return self.r.recvuntil(b'backpack> ').decode(errors='replace')

    def ls(self):
        out = self.cmd('ls')
        names = []
        for line in out.splitlines():
            s = line.strip()
            if not s or s.startswith('backpack>'):
                continue
            parts = s.split()
            if len(parts) >= 3:
                names.append(parts[-1])
        return names

    def put_raw(self, payload):
        self.r.sendline(f'put-raw {len(payload)}'.encode())
        self.r.send(payload)
        return self.r.recvuntil(b'backpack> ').decode(errors='replace')

    def get_raw(self, name):
        self.r.sendline(f'get-raw {name}'.encode())
        line = self.r.recvline().decode()
        if not line.startswith('OK '):
            self.r.recvuntil(b'backpack> ')
            return None
        sz = int(line.split()[1])
        data = self.r.recvn(sz) if sz else b''
        self.r.recvuntil(b'backpack> ')
        return data

    def get_size(self, name):
        """Return blob size via get-raw, without consuming data unnecessarily."""
        self.r.sendline(f'get-raw {name}'.encode())
        line = self.r.recvline().decode()
        if not line.startswith('OK '):
            self.r.recvuntil(b'backpack> ')
            return None
        sz = int(line.split()[1])
        if sz:
            self.r.recvn(sz)
        self.r.recvuntil(b'backpack> ')
        return sz

    def get_padding_oracle(self, name):
        """Return True iff PKCS#7 padding decoded successfully."""
        self.r.sendline(f'get {name}'.encode())
        out = self.r.recvuntil(b'backpack> ').decode(errors='replace')
        return ('ciphertext decryption failed' not in out
                and 'failed to decrypt' not in out)

    def rm(self, name):
        return self.cmd(f'rm {name}')


def find_blob_name(b: Backpack, target_size: int) -> str:
    """Among current files, return the one whose blob size equals target_size."""
    names = b.ls()
    for n in names:
        sz = b.get_size(n)
        if sz == target_size:
            return n
    raise RuntimeError(f'no blob of size {target_size} among {names}')


def query(b: Backpack, prev_iv: bytes, target_ct: bytes, our_size: int) -> bool:
    """One padding oracle query."""
    payload = bytes(prev_iv) + bytes(target_ct)
    assert len(payload) == our_size, (len(payload), our_size)
    b.put_raw(payload)
    our_name = find_blob_name(b, our_size)
    ok = b.get_padding_oracle(our_name)
    b.rm(our_name)
    return ok


def attack_one_block(b: Backpack, prev_ct: bytes, target_ct: bytes, our_size: int,
                     verbose=True):
    intermediate = bytearray(BLOCK)
    plaintext = bytearray(BLOCK)

    for pad_byte in range(1, BLOCK + 1):
        idx = BLOCK - pad_byte
        base_iv = bytearray(BLOCK)
        for j in range(idx + 1, BLOCK):
            base_iv[j] = intermediate[j] ^ pad_byte

        found = None
        for guess in range(256):
            iv = bytearray(base_iv)
            iv[idx] = guess
            ok = query(b, bytes(iv), target_ct, our_size)
            if not ok:
                continue
            if pad_byte == 1:
                # Disambiguation against accidental high-padding hits.
                # Flip iv[idx-1]; if still OK, this is the real \x01-byte case.
                iv2 = bytearray(iv)
                if idx >= 1:
                    iv2[idx - 1] ^= 0xFF
                else:
                    # idx == 0, only one byte to test; cannot disambiguate
                    pass
                if idx >= 1 and not query(b, bytes(iv2), target_ct, our_size):
                    continue
            found = guess
            break

        if found is None:
            raise RuntimeError(f'no valid byte at pad={pad_byte} idx={idx}')

        intermediate[idx] = found ^ pad_byte
        plaintext[idx] = intermediate[idx] ^ prev_ct[idx]
        if verbose:
            ch = chr(plaintext[idx]) if 32 <= plaintext[idx] < 127 else '?'
            print(f'    [{idx:2d}] int={intermediate[idx]:02x} pt={plaintext[idx]:02x} ({ch})',
                  flush=True)

    return bytes(plaintext)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='127.0.0.1')
    ap.add_argument('--port', type=int, default=30034)
    ap.add_argument('--block', type=int, default=None,
                    help='attack only this 1-indexed block (debug)')
    ap.add_argument('--from-block', type=int, default=1)
    ap.add_argument('--save', default=None,
                    help='save partial plaintext here as we recover bytes')
    args = ap.parse_args()

    b = Backpack(args.host, args.port)
    files = b.ls()
    print(f'[+] Files at start: {files}')
    flag_name = files[0]  # must be a single file
    flag_ct = b.get_raw(flag_name)
    print(f'[+] Flag ct: {len(flag_ct)} bytes  hex={flag_ct.hex()}')

    flag_size = len(flag_ct)
    our_size = 32  # IV(16) + 1 ct block(16)

    iv = flag_ct[:BLOCK]
    blocks = [flag_ct[i:i + BLOCK] for i in range(BLOCK, flag_size, BLOCK)]
    print(f'[+] {len(blocks)} ciphertext blocks')

    full_pt = b''
    targets = ([args.block - 1] if args.block is not None
               else list(range(args.from_block - 1, len(blocks))))

    try:
        for i in targets:
            prev = iv if i == 0 else blocks[i - 1]
            target = blocks[i]
            t0 = time.time()
            print(f'[*] Block {i+1}/{len(blocks)}', flush=True)
            pt = attack_one_block(b, prev, target, our_size)
            full_pt += pt
            print(f'[+] Block {i+1}: {pt!r}  ({time.time()-t0:.1f}s)', flush=True)
            if args.save:
                with open(args.save, 'ab') as f:
                    f.write(pt)
    finally:
        b.close()

    print('=' * 60)
    print(f'Full plaintext: {full_pt!r}')
    if full_pt:
        pad = full_pt[-1]
        if 1 <= pad <= 16 and full_pt[-pad:] == bytes([pad]) * pad:
            print(f'Unpadded: {full_pt[:-pad]!r}')


if __name__ == '__main__':
    main()

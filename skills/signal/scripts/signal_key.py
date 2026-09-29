#!/usr/bin/env python3
"""Derive the Signal Desktop SQLCipher key from the macOS Keychain.

Prints the 64-char hex key and caches it to /tmp/.sigkey.

Usage:
    python3 signal_key.py

Then:
    K=$(cat /tmp/.sigkey)
    sqlcipher "$HOME/Library/Application Support/Signal/sql/db.sqlite" <<EOF
    PRAGMA key = "x'${K}'";
    PRAGMA cipher_compatibility = 4;
    SELECT COUNT(*) FROM messages;
    EOF
"""
import hashlib
import json
import os
import subprocess
import sys

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes

CONFIG = os.path.expanduser("~/Library/Application Support/Signal/config.json")
CACHE = "/tmp/.sigkey"


def derive_key():
    password = subprocess.check_output(
        ["security", "find-generic-password", "-s", "Signal Safe Storage", "-w"],
        text=True,
    ).strip()

    with open(CONFIG) as f:
        encrypted_key = bytes.fromhex(json.load(f)["encryptedKey"])

    # Chromium os_crypt: PBKDF2-SHA1, salt "saltysalt", 1003 iterations, 16-byte key
    derived = hashlib.pbkdf2_hmac("sha1", password.encode(), b"saltysalt", 1003, dklen=16)

    # AES-128-CBC, IV is 16 spaces, "v10" prefix skipped
    decryptor = Cipher(
        algorithms.AES(derived), modes.CBC(b" " * 16), backend=default_backend()
    ).decryptor()
    plaintext = decryptor.update(encrypted_key[3:]) + decryptor.finalize()

    pad = plaintext[-1]
    if pad <= 16:
        plaintext = plaintext[:-pad]

    # Plaintext is already the ASCII hex key. Do not .hex() it again.
    key = plaintext.decode("utf-8")
    if len(key) != 64:
        raise ValueError(f"expected 64 hex chars, got {len(key)}: {key!r}")
    return key


if __name__ == "__main__":
    try:
        key = derive_key()
    except Exception as exc:
        print(f"failed to derive Signal key: {exc}", file=sys.stderr)
        sys.exit(1)

    with open(CACHE, "w") as f:
        f.write(key)
    os.chmod(CACHE, 0o600)
    print(key)

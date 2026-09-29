---
name: signal
description: This skill should be used when the user asks to "read my Signal messages", "find my Signal conversation", "check Signal", "read my messages on Signal", or mentions Signal messenger. Provides the complete method for decrypting and reading the local Signal Desktop database.
tools: Bash, Read
---

# Signal Message Reader

Read Signal Desktop messages by decrypting the local SQLCipher database.

## Prerequisites

SQLCipher must be installed:

```bash
brew install sqlcipher
```

The `cryptography` Python package is also needed:

```bash
pip3 install cryptography
```

## Decrypting the database

Signal Desktop encrypts its database using a key derived from the macOS Keychain. The full decryption process:

```python
import subprocess, json, hashlib
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

# Step 1: Get keychain password
keychain_password = subprocess.check_output(
    ['security', 'find-generic-password', '-s', 'Signal Safe Storage', '-w'],
    text=True
).strip()

# Step 2: Read encrypted key from config
with open('~/Library/Application Support/Signal/config.json') as f:
    encrypted_key_hex = json.load(f)['encryptedKey']

encrypted_key = bytes.fromhex(encrypted_key_hex)

# Step 3: Derive AES key using PBKDF2 (Chromium os_crypt approach)
derived_key = hashlib.pbkdf2_hmac(
    'sha1',
    keychain_password.encode('utf-8'),
    b'saltysalt',
    1003,
    dklen=16
)

# Step 4: Decrypt with AES-128-CBC
ciphertext = encrypted_key[3:]  # Skip 'v10' prefix
cipher = Cipher(algorithms.AES(derived_key), modes.CBC(b' ' * 16), backend=default_backend())
decryptor = cipher.decryptor()
decrypted = decryptor.update(ciphertext) + decryptor.finalize()

# Remove PKCS7 padding
pad_len = decrypted[-1]
if pad_len <= 16:
    decrypted = decrypted[:-pad_len]

# IMPORTANT: the decrypted bytes are ASCII text already containing the
# 64-char hex key. Decode them, do NOT call .hex() (that double-encodes
# to 128 chars and sqlcipher fails with "file is not a database").
DB_KEY = decrypted.decode('utf-8')
assert len(DB_KEY) == 64, f"expected 64 hex chars, got {len(DB_KEY)}"
print(f"DB key: {DB_KEY}")
```

Or just run the helper, which prints the key and caches it to `/tmp/.sigkey`:

```bash
python3 ~/.claude/skills/signal/scripts/signal_key.py
```

## Querying messages with sqlcipher

Once the DB_KEY is obtained, query with sqlcipher:

```bash
DB_KEY="<hex key from above>"

sqlcipher "~/Library/Application Support/Signal/sql/db.sqlite" << EOF
PRAGMA key = "x'${DB_KEY}'";
PRAGMA cipher_compatibility = 4;

-- List all conversations
SELECT id, name, profileFullName, e164 FROM conversations;
EOF
```

## Reading a specific conversation

```bash
sqlcipher "~/Library/Application Support/Signal/sql/db.sqlite" << EOF
PRAGMA key = "x'${DB_KEY}'";
PRAGMA cipher_compatibility = 4;

SELECT
  datetime(sent_at/1000, 'unixepoch', 'localtime') as date,
  CASE WHEN type = 'outgoing' THEN 'Me' ELSE 'Them' END as sender,
  body
FROM messages
WHERE conversationId = 'CONVERSATION_ID_HERE'
ORDER BY sent_at;
EOF
```

## Finding a contact

```sql
SELECT id, name, profileFullName, e164
FROM conversations
WHERE profileFullName LIKE '%NAME%'
   OR name LIKE '%NAME%'
   OR e164 LIKE '%PHONE%';
```

## Key facts

- Database: `~/Library/Application Support/Signal/sql/db.sqlite`
- Config: `~/Library/Application Support/Signal/config.json`
- Keychain entry: "Signal Safe Storage"
- Encryption: SQLCipher 4, key derived via Chromium os_crypt (PBKDF2-SHA1, salt "saltysalt", 1003 iterations)
- `encryptedKey` in config.json has a 3-byte "v10" prefix to skip
- IV for AES-CBC decryption: 16 space characters
- Signal timestamps are milliseconds (divide by 1000 for unixepoch)
- Message types: 'outgoing' (sent) vs other (received)
- **Signal must not be open** while querying (database lock)

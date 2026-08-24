"""
ColdProof v3.6 — hashing / lightweight encryption utilities
Used only for CPVault obfuscation. Not cryptographically secure.
"""

def simple_xor(data: bytes, key: bytes) -> bytes:
    """
    Very small reversible XOR cipher.
    Symmetric: encrypt = decrypt.
    """
    key_len = len(key)
    return bytes([data[i] ^ key[i % key_len] for i in range(len(data))])

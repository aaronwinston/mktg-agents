"""Key encryption and hashing for runtime credentials."""

import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from config import settings

class KeyVault:
    """Encrypt/decrypt runtime API keys using AES-256-GCM."""
    
    def __init__(self, secret_key: str = None):
        """Initialize with encryption key from env or parameter."""
        key = secret_key or os.getenv('LLM_KEY_ENCRYPTION_SECRET', '')
        
        if not key:
            # For development, use a default (INSECURE for production)
            key = base64.b64encode(os.urandom(32)).decode()
        
        # Decode from base64 if needed
        if isinstance(key, str):
            try:
                self.key = base64.b64decode(key)
            except Exception:
                # Assume it's raw bytes, encode to base64 then decode
                self.key = base64.b64encode(key.encode()).decode()
                self.key = base64.b64decode(self.key)
        else:
            self.key = key
        
        # Ensure 32 bytes (256 bits)
        if len(self.key) != 32:
            raise ValueError(f"Encryption key must be 32 bytes, got {len(self.key)}")
    
    def encrypt_key(self, plaintext_key: str) -> str:
        """
        Encrypt a runtime API key using AES-256-GCM.
        Returns: base64(nonce + ciphertext + tag)
        """
        import os
        nonce = os.urandom(12)  # 96-bit nonce for GCM
        cipher = AESGCM(self.key)
        ciphertext = cipher.encrypt(nonce, plaintext_key.encode(), None)
        
        # Combine nonce + ciphertext (includes auth tag)
        encrypted = nonce + ciphertext
        return base64.b64encode(encrypted).decode()
    
    def decrypt_key(self, encrypted_key: str) -> str:
        """
        Decrypt a runtime API key.
        Raises ValueError if authentication fails.
        """
        try:
            encrypted = base64.b64decode(encrypted_key)
            nonce = encrypted[:12]
            ciphertext = encrypted[12:]
            
            cipher = AESGCM(self.key)
            plaintext = cipher.decrypt(nonce, ciphertext, None)
            return plaintext.decode()
        except Exception as e:
            raise ValueError(f"Key decryption failed: {str(e)}")
    
    def hash_key(self, plaintext_key: str) -> str:
        """
        Hash a key for comparison/lookups without decrypting.
        Returns hex-encoded SHA256 hash.
        """
        return hashlib.sha256(plaintext_key.encode()).hexdigest()

# Global instance
_vault = None

def get_vault() -> KeyVault:
    """Get or create the global KeyVault instance."""
    global _vault
    if _vault is None:
        _vault = KeyVault()
    return _vault

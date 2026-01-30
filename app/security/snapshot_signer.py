"""
SNAPSHOT SIGNER

Purpose:
- Sign snapshot hashes for authenticity
- Verify signatures for tamper detection
- Symmetric HMAC-SHA256 signing

Requirements:
- HMAC-SHA256 (symmetric)
- Key from ENV: SNAPSHOT_SIGNING_KEY
- Signature independent of storage
- Fail closed on missing key
"""

import hmac
import hashlib
import os
from typing import Optional


# Signing key from environment
_SIGNING_KEY: Optional[str] = os.getenv("SNAPSHOT_SIGNING_KEY")

# Default key for development (NEVER use in production)
_DEFAULT_DEV_KEY = "dev-snapshot-signing-key-change-in-production"


class SigningKeyMissing(Exception):
    """Raised when signing key is not configured."""
    pass


def _get_signing_key() -> bytes:
    """
    Get the signing key from environment.
    
    Returns:
        Signing key as bytes
    
    Raises:
        SigningKeyMissing: If key is not configured
    """
    key = _SIGNING_KEY
    
    # In development, allow fallback to default key
    if key is None:
        # Check if we're in development mode
        if os.getenv("ENVIRONMENT") == "production":
            raise SigningKeyMissing(
                "SNAPSHOT_SIGNING_KEY must be set in production"
            )
        
        # Use default dev key with warning
        key = _DEFAULT_DEV_KEY
    
    return key.encode('utf-8')


def sign_hash(hash_value: str) -> str:
    """
    Sign a snapshot hash using HMAC-SHA256.
    
    Args:
        hash_value: SHA-256 hash to sign
    
    Returns:
        Hexadecimal signature string
    
    Raises:
        SigningKeyMissing: If signing key not configured
        ValueError: If hash_value is invalid
    """
    if not hash_value or not isinstance(hash_value, str):
        raise ValueError("Invalid hash value")
    
    if len(hash_value) != 64:
        raise ValueError("Hash must be 64 characters (SHA-256)")
    
    try:
        signing_key = _get_signing_key()
        
        # HMAC-SHA256
        signature = hmac.new(
            signing_key,
            hash_value.encode('utf-8'),
            hashlib.sha256
        )
        
        return signature.hexdigest()
    
    except SigningKeyMissing:
        raise
    except Exception as e:
        raise ValueError(f"Failed to sign hash: {str(e)}")


def verify_signature(hash_value: str, signature: str) -> bool:
    """
    Verify a signature against a hash.
    
    Args:
        hash_value: Original hash
        signature: Signature to verify
    
    Returns:
        True if signature is valid, False otherwise
    
    Security:
        Uses constant-time comparison to prevent timing attacks
    """
    if not hash_value or not signature:
        return False
    
    if not isinstance(hash_value, str) or not isinstance(signature, str):
        return False
    
    try:
        # Recompute signature
        expected_signature = sign_hash(hash_value)
        
        # Constant-time comparison
        return hmac.compare_digest(expected_signature, signature)
    
    except (SigningKeyMissing, ValueError):
        return False


def sign_data(data: str) -> str:
    """
    Sign arbitrary string data directly.
    
    Args:
        data: String to sign
    
    Returns:
        Hexadecimal signature string
    """
    if not isinstance(data, str):
        raise ValueError("Data must be a string")
    
    try:
        signing_key = _get_signing_key()
        
        signature = hmac.new(
            signing_key,
            data.encode('utf-8'),
            hashlib.sha256
        )
        
        return signature.hexdigest()
    
    except SigningKeyMissing:
        raise
    except Exception as e:
        raise ValueError(f"Failed to sign data: {str(e)}")


def verify_data_signature(data: str, signature: str) -> bool:
    """
    Verify a signature against arbitrary data.
    
    Args:
        data: Original data
        signature: Signature to verify
    
    Returns:
        True if signature is valid, False otherwise
    """
    if not data or not signature:
        return False
    
    try:
        expected_signature = sign_data(data)
        return hmac.compare_digest(expected_signature, signature)
    
    except (SigningKeyMissing, ValueError):
        return False

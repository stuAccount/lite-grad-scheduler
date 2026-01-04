"""Unit tests for security utilities."""

import pytest
from datetime import timedelta


class TestPasswordHashing:
    """Test password hashing functions."""

    def test_hash_password_returns_string(self):
        """hash_password returns a hashed string."""
        from scheduler.services.security import hash_password
        
        result = hash_password("secret123")
        
        assert isinstance(result, str)
        assert result != "secret123"  # Should be hashed

    def test_verify_password_correct(self):
        """verify_password returns True for correct password."""
        from scheduler.services.security import hash_password, verify_password
        
        hashed = hash_password("secret123")
        
        assert verify_password("secret123", hashed) is True

    def test_verify_password_incorrect(self):
        """verify_password returns False for wrong password."""
        from scheduler.services.security import hash_password, verify_password
        
        hashed = hash_password("secret123")
        
        assert verify_password("wrongpassword", hashed) is False


class TestJWTTokens:
    """Test JWT token functions."""

    def test_create_access_token(self):
        """create_access_token returns a token string."""
        from scheduler.services.security import create_access_token
        
        token = create_access_token({"sub": "user-123"})
        
        assert isinstance(token, str)
        assert len(token) > 0

    def test_decode_token_valid(self):
        """decode_token returns payload for valid token."""
        from scheduler.services.security import create_access_token, decode_token
        
        token = create_access_token({"sub": "user-123", "role": "admin"})
        payload = decode_token(token)
        
        assert payload is not None
        assert payload["sub"] == "user-123"
        assert payload["role"] == "admin"

    def test_decode_token_invalid(self):
        """decode_token returns None for invalid token."""
        from scheduler.services.security import decode_token
        
        result = decode_token("invalid.token.here")
        
        assert result is None

    def test_decode_token_expired(self):
        """decode_token returns None for expired token."""
        from scheduler.services.security import create_access_token, decode_token
        
        # Create token that expires immediately
        token = create_access_token({"sub": "user-123"}, expires_delta=timedelta(seconds=-1))
        result = decode_token(token)
        
        assert result is None

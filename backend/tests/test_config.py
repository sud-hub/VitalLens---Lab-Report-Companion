"""
Property-based tests for configuration loading.

This module tests that configuration is properly loaded from environment variables
and that validation fails fast when critical settings are missing.
"""

import os
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck
from pydantic import ValidationError
from unittest.mock import patch

from app.core.config import Settings


class TestConfigurationProperties:
    """Property-based tests for configuration loading."""

    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        database_url=st.text(
            min_size=1, 
            max_size=200,
            alphabet=st.characters(blacklist_characters='\x00\r\n')
        ),
        jwt_secret=st.text(
            min_size=1, 
            max_size=100,
            alphabet=st.characters(blacklist_characters='\x00\r\n')
        ),
        jwt_algorithm=st.sampled_from(["HS256", "HS384", "HS512", "RS256"]),
        expire_minutes=st.integers(min_value=1, max_value=1440)
    )
    def test_property_42_configuration_loads_from_environment(
        self, database_url, jwt_secret, jwt_algorithm, expire_minutes
    ):
        """
        Feature: lab-report-companion, Property 42: Configuration loads from environment
        
        For any required configuration setting (DATABASE_URL, JWT_SECRET_KEY, 
        JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES), when the system starts, 
        it should load the value from the corresponding environment variable 
        or use a documented default.
        
        Validates: Requirements 18.1, 18.2, 18.3, 18.4
        """
        # Use patch to set environment variables
        env_vars = {
            "DATABASE_URL": database_url,
            "JWT_SECRET_KEY": jwt_secret,
            "JWT_ALGORITHM": jwt_algorithm,
            "ACCESS_TOKEN_EXPIRE_MINUTES": str(expire_minutes)
        }
        
        with patch.dict(os.environ, env_vars, clear=False):
            # Create settings instance
            config = Settings()
            
            # Verify all values are loaded from environment
            assert config.DATABASE_URL == database_url
            assert config.JWT_SECRET_KEY == jwt_secret
            assert config.JWT_ALGORITHM == jwt_algorithm
            assert config.ACCESS_TOKEN_EXPIRE_MINUTES == expire_minutes

    def test_property_42_configuration_uses_defaults_when_env_not_set(self, monkeypatch):
        """
        Feature: lab-report-companion, Property 42: Configuration loads from environment
        
        Test that documented defaults are used when environment variables are not set.
        
        Validates: Requirements 18.1, 18.2, 18.3, 18.4
        """
        # Clear all relevant environment variables
        for key in ["DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
            monkeypatch.delenv(key, raising=False)
        
        # Create settings instance
        config = Settings()
        
        # Verify defaults are used
        assert config.DATABASE_URL == "sqlite:///./lab_companion.db"
        assert config.JWT_SECRET_KEY == "dev-secret-key-change-in-production"
        assert config.JWT_ALGORITHM == "HS256"
        assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        database_url=st.text(
            min_size=1, 
            max_size=200,
            alphabet=st.characters(blacklist_characters='\x00\r\n')
        )
    )
    def test_property_42_partial_environment_override(self, database_url):
        """
        Feature: lab-report-companion, Property 42: Configuration loads from environment
        
        Test that some settings can be overridden while others use defaults.
        
        Validates: Requirements 18.1, 18.2, 18.3, 18.4
        """
        # Set only DATABASE_URL, clear others
        env_vars = {"DATABASE_URL": database_url}
        
        # Clear the other keys if they exist
        env_to_clear = {
            key: None 
            for key in ["JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]
            if key in os.environ
        }
        
        with patch.dict(os.environ, {**env_to_clear, **env_vars}, clear=False):
            # Create settings instance
            config = Settings()
            
            # Verify DATABASE_URL is from environment, others are defaults
            assert config.DATABASE_URL == database_url
            assert config.JWT_SECRET_KEY == "dev-secret-key-change-in-production"
            assert config.JWT_ALGORITHM == "HS256"
            assert config.ACCESS_TOKEN_EXPIRE_MINUTES == 30

    def test_property_43_configuration_validation_fails_fast_for_invalid_types(self, monkeypatch):
        """
        Feature: lab-report-companion, Property 43: Configuration validation fails fast
        
        For any critical configuration setting that has an invalid type,
        the system should fail to start and report the validation error.
        
        Validates: Requirements 18.5
        """
        # Clear environment variables
        for key in ["DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
            monkeypatch.delenv(key, raising=False)
        
        # Set ACCESS_TOKEN_EXPIRE_MINUTES to invalid type (non-integer string)
        monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", "not-a-number")
        
        # Attempt to create settings should raise validation error
        with pytest.raises(ValidationError) as exc_info:
            Settings()
        
        # Verify the error is about the invalid field
        error_dict = exc_info.value.errors()
        assert any(
            error['loc'] == ('ACCESS_TOKEN_EXPIRE_MINUTES',) 
            for error in error_dict
        )

    @settings(max_examples=100, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @given(
        invalid_value=st.text(min_size=1, max_size=50).filter(
            lambda x: (
                # Filter out values that can be coerced to integers by Pydantic
                # Pydantic will strip whitespace and try to parse, so '0 ', ' 123' are valid
                not x.strip().isdigit() and 
                not x.strip().lstrip('-').isdigit() and
                '\x00' not in x  # Filter out null characters that can't be in env vars
            )
        )
    )
    def test_property_43_integer_fields_reject_non_integers(self, invalid_value):
        """
        Feature: lab-report-companion, Property 43: Configuration validation fails fast
        
        For any non-integer value provided for ACCESS_TOKEN_EXPIRE_MINUTES,
        the system should fail validation. Note that Pydantic performs type coercion,
        so strings like '0 ' or ' 123' that can be stripped and parsed as integers
        are considered valid.
        
        Validates: Requirements 18.5
        """
        # Set ACCESS_TOKEN_EXPIRE_MINUTES to invalid value
        env_vars = {"ACCESS_TOKEN_EXPIRE_MINUTES": invalid_value}
        
        with patch.dict(os.environ, env_vars, clear=False):
            # Should raise validation error
            with pytest.raises(ValidationError):
                Settings()

    def test_property_43_empty_strings_handled_appropriately(self, monkeypatch):
        """
        Feature: lab-report-companion, Property 43: Configuration validation fails fast
        
        Test that empty strings in environment variables are handled appropriately.
        For string fields with defaults, empty strings should either use the default
        or be accepted if valid.
        
        Validates: Requirements 18.5
        """
        # Clear environment variables
        for key in ["DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
            monkeypatch.delenv(key, raising=False)
        
        # Set DATABASE_URL to empty string
        monkeypatch.setenv("DATABASE_URL", "")
        
        # Create settings - should either use default or accept empty string
        config = Settings()
        
        # Verify configuration was created (doesn't crash)
        assert hasattr(config, 'DATABASE_URL')
        assert hasattr(config, 'JWT_SECRET_KEY')
        assert hasattr(config, 'JWT_ALGORITHM')
        assert hasattr(config, 'ACCESS_TOKEN_EXPIRE_MINUTES')

    def test_configuration_can_be_instantiated_multiple_times(self, monkeypatch):
        """
        Test that Settings can be instantiated multiple times with different
        environment variables, which is important for testing.
        """
        # First instance with defaults
        for key in ["DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
            monkeypatch.delenv(key, raising=False)
        
        config1 = Settings()
        assert config1.DATABASE_URL == "sqlite:///./lab_companion.db"
        
        # Second instance with custom DATABASE_URL
        monkeypatch.setenv("DATABASE_URL", "postgresql://test:test@localhost/testdb")
        config2 = Settings()
        assert config2.DATABASE_URL == "postgresql://test:test@localhost/testdb"
        
        # Verify they are independent
        assert config1.DATABASE_URL != config2.DATABASE_URL

    def test_jwt_algorithm_accepts_valid_algorithms(self, monkeypatch):
        """
        Test that JWT_ALGORITHM accepts standard JWT algorithms.
        """
        valid_algorithms = ["HS256", "HS384", "HS512", "RS256", "RS384", "RS512"]
        
        for algorithm in valid_algorithms:
            # Clear environment
            for key in ["DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
                monkeypatch.delenv(key, raising=False)
            
            monkeypatch.setenv("JWT_ALGORITHM", algorithm)
            config = Settings()
            assert config.JWT_ALGORITHM == algorithm

    def test_access_token_expire_minutes_accepts_positive_integers(self, monkeypatch):
        """
        Test that ACCESS_TOKEN_EXPIRE_MINUTES accepts positive integers.
        """
        valid_values = [1, 15, 30, 60, 120, 1440]
        
        for value in valid_values:
            # Clear environment
            for key in ["DATABASE_URL", "JWT_SECRET_KEY", "JWT_ALGORITHM", "ACCESS_TOKEN_EXPIRE_MINUTES"]:
                monkeypatch.delenv(key, raising=False)
            
            monkeypatch.setenv("ACCESS_TOKEN_EXPIRE_MINUTES", str(value))
            config = Settings()
            assert config.ACCESS_TOKEN_EXPIRE_MINUTES == value

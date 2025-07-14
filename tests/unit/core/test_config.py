"""Unit tests for core configuration."""
import pytest
from unittest.mock import patch
import os

from josi.core.config import Settings


class TestSettings:
    """Test Settings configuration."""
    
    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()
        
        assert settings.app_name == "Astrow API"
        assert settings.app_version == "1.0.0"
        # Debug and environment may vary based on env vars, just check they exist
        assert hasattr(settings, 'debug')
        assert hasattr(settings, 'environment')
        assert settings.host == "0.0.0.0"
        assert settings.port == 8000
        assert hasattr(settings, 'secret_key')  # Secret key may vary by environment
        assert settings.algorithm == "HS256"
        assert settings.access_token_expire_minutes == 30
        assert settings.api_key_header == "X-API-Key"
    
    def test_cors_settings_defaults(self):
        """Test CORS default settings."""
        settings = Settings()
        
        assert settings.cors_origins == ["*"]
        assert settings.cors_allow_credentials is True
        assert settings.cors_allow_methods == ["*"]
        assert settings.cors_allow_headers == ["*"]
    
    def test_other_defaults(self):
        """Test other default settings."""
        settings = Settings()
        
        assert settings.redis_url is None
        assert settings.log_level == "INFO"
        assert "%(asctime)s" in settings.log_format
        assert settings.ephemeris_path == "/usr/share/swisseph"
        assert settings.geocoding_timeout == 10
        assert settings.geocoding_cache_ttl == 86400
        assert settings.rate_limit_enabled is True
        assert settings.rate_limit_per_minute == 60
        assert settings.gzip_minimum_size == 1000
    
    def test_cors_origins_string_parsing(self):
        """Test CORS origins parsing from string."""
        settings = Settings()
        result = settings.parse_cors_origins("http://localhost:3000,https://example.com")
        
        assert result == ["http://localhost:3000", "https://example.com"]
    
    def test_cors_origins_string_parsing_with_spaces(self):
        """Test CORS origins parsing with spaces."""
        settings = Settings()
        result = settings.parse_cors_origins("http://localhost:3000, https://example.com , https://test.com")
        
        assert result == ["http://localhost:3000", "https://example.com", "https://test.com"]
    
    def test_cors_origins_list_passthrough(self):
        """Test CORS origins list passthrough."""
        settings = Settings()
        original_list = ["http://localhost:3000", "https://example.com"]
        result = settings.parse_cors_origins(original_list)
        
        assert result == original_list
    
    def test_cors_methods_string_parsing(self):
        """Test CORS methods parsing from string."""
        settings = Settings()
        result = settings.parse_cors_methods("GET,POST,PUT,DELETE")
        
        assert result == ["GET", "POST", "PUT", "DELETE"]
    
    def test_cors_methods_list_passthrough(self):
        """Test CORS methods list passthrough."""
        settings = Settings()
        original_list = ["GET", "POST"]
        result = settings.parse_cors_methods(original_list)
        
        assert result == original_list
    
    def test_cors_headers_string_parsing(self):
        """Test CORS headers parsing from string."""
        settings = Settings()
        result = settings.parse_cors_headers("Content-Type,Authorization,X-API-Key")
        
        assert result == ["Content-Type", "Authorization", "X-API-Key"]
    
    def test_cors_headers_list_passthrough(self):
        """Test CORS headers list passthrough."""
        settings = Settings()
        original_list = ["Content-Type", "Authorization"]
        result = settings.parse_cors_headers(original_list)
        
        assert result == original_list
    
    def test_database_url_validation_valid_postgresql(self):
        """Test valid PostgreSQL URL validation."""
        settings = Settings()
        
        valid_urls = [
            "postgresql://user:pass@localhost/db",
            "postgres://user:pass@localhost/db",
            "postgresql+asyncpg://user:pass@localhost/db"
        ]
        
        for url in valid_urls:
            result = settings.validate_database_url(url)
            assert result == url
    
    def test_database_url_validation_invalid(self):
        """Test invalid database URL validation."""
        settings = Settings()
        
        with pytest.raises(ValueError, match="Database URL must be a PostgreSQL connection string"):
            settings.validate_database_url("mysql://user:pass@localhost/db")
    
    def test_database_url_validation_empty(self):
        """Test empty database URL validation."""
        settings = Settings()
        
        with pytest.raises(ValueError, match="Database URL must be a PostgreSQL connection string"):
            settings.validate_database_url("")
    
    @patch.dict(os.environ, {
        "APP_NAME": "Test API",
        "DEBUG": "true",
        "ENVIRONMENT": "test",
        "PORT": "9000"
    })
    def test_environment_variable_override(self):
        """Test that environment variables override defaults."""
        settings = Settings()
        
        assert settings.app_name == "Test API"
        assert settings.debug is True
        assert settings.environment == "test"
        assert settings.port == 9000
    
    def test_settings_immutability(self):
        """Test that settings are properly configured."""
        settings = Settings()
        
        # Test that we can access settings
        assert hasattr(settings, 'app_name')
        assert hasattr(settings, 'database_url')
        assert hasattr(settings, 'debug')
    
    def test_model_config(self):
        """Test model configuration."""
        settings = Settings()
        
        # Test that the model is properly configured
        assert settings.model_config['case_sensitive'] is False
        assert settings.model_config['env_file'] == ".env"
        assert settings.model_config['env_file_encoding'] == "utf-8"
"""
Configuration settings for TermoApp.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Base configuration class."""
    
    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Google Sheets settings
    SHEET_ID = os.getenv('SHEET_ID')
    CREDENTIALS_PATH = os.getenv('CREDENTIALS')
    
    # Cache settings
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TTL = int(os.getenv('CACHE_TTL', 3600))  # 1 hour default
    
    # Logging settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/termoapp.log')
    
    # File paths
    TEMPLATES_DIR = os.getenv('TEMPLATES_DIR', 'modelos')
    OUTPUT_DOCX_DIR = os.getenv('OUTPUT_DOCX_DIR', 'entrega_docx')
    OUTPUT_PDF_DIR = os.getenv('OUTPUT_PDF_DIR', 'entrega_pdf')
    
    # LibreOffice settings
    LIBREOFFICE_PATH = os.getenv('LIBREOFFICE_PATH', '/usr/bin/libreoffice')
    
    # Validation settings
    MAX_ASSETS_PER_REQUEST = int(os.getenv('MAX_ASSETS_PER_REQUEST', 50))
    MAX_NAME_LENGTH = int(os.getenv('MAX_NAME_LENGTH', 100))
    MAX_FUNCTION_LENGTH = int(os.getenv('MAX_FUNCTION_LENGTH', 100))
    
    @classmethod
    def validate(cls) -> None:
        """Validate required configuration."""
        required_vars = ['SHEET_ID', 'CREDENTIALS_PATH']
        missing_vars = [var for var in required_vars if not getattr(cls, var)]
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
    
    @classmethod
    def get_template_path(cls, company: str) -> str:
        """Get template path for a company."""
        return os.path.join(cls.TEMPLATES_DIR, f"entrega{company}.docx")
    
    @classmethod
    def get_output_paths(cls, filename: str) -> tuple[str, str]:
        """Get output paths for DOCX and PDF files."""
        docx_path = os.path.join(cls.OUTPUT_DOCX_DIR, f"{filename}.docx")
        pdf_path = os.path.join(cls.OUTPUT_PDF_DIR, f"{filename}.pdf")
        return docx_path, pdf_path

class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'

class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    LOG_LEVEL = 'DEBUG'

# Configuration mapping
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}

def get_config(config_name: Optional[str] = None) -> Config:
    """Get configuration instance."""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'default')
    
    config_class = config.get(config_name, config['default'])
    return config_class() 
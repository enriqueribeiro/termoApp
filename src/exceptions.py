from typing import Optional, Dict, Any

"""
Custom exceptions for the TermoApp application.
"""

class TermoAppException(Exception):
    """Base exception for all TermoApp errors."""
    
    def __init__(self, message: str, error_code, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class DocumentGenerationError(TermoAppException):
    """Raised when document generation fails."""
    
    def __init__(self, message: str, template_path, user_data):
        super().__init__(message, "DOC_GEN_ERROR")
        self.template_path = template_path
        self.user_data = user_data or {}

class GoogleSheetsError(TermoAppException):
    """Raised when Google Sheets operations fail."""
    
    def __init__(self, message: str, sheet_id, operation):
        super().__init__(message, "GOOGLE_SHEETS_ERROR")
        self.sheet_id = sheet_id
        self.operation = operation

class FileOperationError(TermoAppException):
    """Raised when file operations fail."""
    
    def __init__(self, message: str, file_path, operation):
        super().__init__(message, "FILE_OPERATION_ERROR")
        self.file_path = file_path
        self.operation = operation

class ValidationError(TermoAppException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Optional[str] = None):
        super().__init__(message, "VALIDATION_ERROR")
        self.field = field
        self.value = value

class ConfigurationError(TermoAppException):
    """Raised when configuration is invalid or missing."""
    
    def __init__(self, message: str, config_key):
        super().__init__(message, "CONFIG_ERROR")
        self.config_key = config_key

class PDFConversionError(TermoAppException):
    """Raised when PDF conversion fails."""
    
    def __init__(self, message: str, docx_path, libreoffice_error):
        super().__init__(message, "PDF_CONVERSION_ERROR")
        self.docx_path = docx_path
        self.libreoffice_error = libreoffice_error

class AssetNotFoundError(TermoAppException):
    """Raised when an asset is not found in Google Sheets."""
    
    def __init__(self, message: str, asset_id, sheet_names):
        super().__init__(message, "ASSET_NOT_FOUND")
        self.asset_id = asset_id
        self.sheet_names = sheet_names or []

class TemplateNotFoundError(TermoAppException):
    """Raised when a document template is not found."""
    
    def __init__(self, message: str, template_name, available_templates):
        super().__init__(message, "TEMPLATE_NOT_FOUND")
        self.template_name = template_name
        self.available_templates = available_templates or [] 
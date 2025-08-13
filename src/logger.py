import logging
import json
import sys
from datetime import datetime
from typing import Any, Dict, Optional
import os
from pathlib import Path

class StructuredFormatter(logging.Formatter):
    """Custom formatter for structured JSON logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra_fields'):
            log_entry.update(record.extra_fields)
        
        return json.dumps(log_entry, ensure_ascii=False)

class RequestFormatter(StructuredFormatter):
    """Formatter that includes request-specific information."""
    
    def format(self, record: logging.LogRecord) -> str:
        # Get base log entry
        log_entry = json.loads(super().format(record))
        
        # Add request-specific fields if available
        if hasattr(record, 'request_id'):
            log_entry['request_id'] = record.request_id
        if hasattr(record, 'user_agent'):
            log_entry['user_agent'] = record.user_agent
        if hasattr(record, 'ip_address'):
            log_entry['ip_address'] = record.ip_address
        if hasattr(record, 'endpoint'):
            log_entry['endpoint'] = record.endpoint
        if hasattr(record, 'method'):
            log_entry['method'] = record.method
        if hasattr(record, 'response_time'):
            log_entry['response_time'] = record.response_time
        
        return json.dumps(log_entry, ensure_ascii=False)

def setup_logger(
    name: str = "termoapp",
    level: str = "INFO",
    log_file: Optional[str] = None,
    include_request_info: bool = True
) -> logging.Logger:
    """
    Setup structured logger with proper configuration.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path for logging
        include_request_info: Whether to include request-specific formatter
    
    Returns:
        Configured logger instance
    """
    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Create formatter
    if include_request_info:
        formatter = RequestFormatter()
    else:
        formatter = StructuredFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (if specified)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

def log_with_context(logger: logging.Logger, level: str, message: str, **kwargs):
    """
    Log message with additional context fields.
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **kwargs: Additional context fields
    """
    extra_fields = kwargs
    log_method = getattr(logger, level.lower())
    
    # Create a custom log record with extra fields
    record = logger.makeRecord(
        logger.name, getattr(logging, level.upper()), 
        "", 0, message, (), None
    )
    record.extra_fields = extra_fields
    log_method(message, extra={'extra_fields': extra_fields})

# Create default logger instance
logger = setup_logger()

# Convenience functions for common logging patterns
def log_request_start(request_id: str, method: str, endpoint: str, ip_address: str, user_agent: str):
    """Log the start of a request."""
    log_with_context(
        logger, "INFO", "Request started",
        request_id=request_id,
        method=method,
        endpoint=endpoint,
        ip_address=ip_address,
        user_agent=user_agent
    )

def log_request_end(request_id: str, response_time: float, status_code: int):
    """Log the end of a request."""
    log_with_context(
        logger, "INFO", "Request completed",
        request_id=request_id,
        response_time=response_time,
        status_code=status_code
    )

def log_document_generation(user_name: str, company: str, asset_count: int, request_id: str):
    """Log document generation event."""
    log_with_context(
        logger, "INFO", "Document generation started",
        user_name=user_name,
        company=company,
        asset_count=asset_count,
        request_id=request_id
    )

def log_google_sheets_operation(operation: str, sheet_name: str, success: bool, error: str = None):
    """Log Google Sheets operations."""
    log_with_context(
        logger, "INFO" if success else "ERROR", f"Google Sheets {operation}",
        operation=operation,
        sheet_name=sheet_name,
        success=success,
        error=error
    )

def log_file_operation(operation: str, file_path: str, success: bool, error: str = None):
    """Log file operations."""
    log_with_context(
        logger, "INFO" if success else "ERROR", f"File {operation}",
        operation=operation,
        file_path=file_path,
        success=success,
        error=error
    ) 
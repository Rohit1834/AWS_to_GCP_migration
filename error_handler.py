#!/usr/bin/env python3
"""
Error Handler Module
Comprehensive error handling and logging for AWS Billing Data Extractor
"""

import logging
import traceback
import functools
from typing import Any, Callable, Optional
from pathlib import Path
import os
from datetime import datetime

from config import LOGGING_CONFIG, LOGS_DIR, ERROR_MESSAGES

class ErrorHandler:
    """Centralized error handling and logging"""
    
    def __init__(self):
        """Initialize error handler"""
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
    
    def setup_logging(self):
        """Setup logging configuration"""
        try:
            # Ensure logs directory exists
            LOGS_DIR.mkdir(exist_ok=True)
            
            # Create log filename with timestamp
            log_filename = f"aws_extractor_{datetime.now().strftime('%Y%m%d')}.log"
            log_path = LOGS_DIR / log_filename
            
            # Configure logging
            logging.basicConfig(
                level=getattr(logging, LOGGING_CONFIG["level"]),
                format=LOGGING_CONFIG["format"],
                handlers=[
                    logging.FileHandler(log_path),
                    logging.StreamHandler()
                ] if LOGGING_CONFIG["console_handler"] else [
                    logging.FileHandler(log_path)
                ]
            )
            
        except Exception as e:
            print(f"Failed to setup logging: {e}")
    
    def log_error(self, error: Exception, context: str = "", 
                  include_traceback: bool = True) -> str:
        """
        Log error with context and traceback
        
        Args:
            error: Exception object
            context: Additional context information
            include_traceback: Whether to include full traceback
            
        Returns:
            Formatted error message
        """
        error_msg = f"{context}: {str(error)}" if context else str(error)
        
        if include_traceback:
            self.logger.error(f"{error_msg}\n{traceback.format_exc()}")
        else:
            self.logger.error(error_msg)
        
        return error_msg
    
    def log_warning(self, message: str, context: str = ""):
        """Log warning message"""
        warning_msg = f"{context}: {message}" if context else message
        self.logger.warning(warning_msg)
    
    def log_info(self, message: str, context: str = ""):
        """Log info message"""
        info_msg = f"{context}: {message}" if context else message
        self.logger.info(info_msg)
    
    def get_user_friendly_error(self, error: Exception, 
                               operation: str = "") -> str:
        """
        Get user-friendly error message
        
        Args:
            error: Exception object
            operation: Operation that failed
            
        Returns:
            User-friendly error message
        """
        error_type = type(error).__name__
        error_str = str(error).lower()
        
        # Map common errors to user-friendly messages
        if "connection" in error_str or "network" in error_str:
            return "Network connection error. Please check your internet connection."
        
        elif "permission" in error_str or "access" in error_str:
            return "Permission denied. Please check file permissions."
        
        elif "not found" in error_str or "no such file" in error_str:
            return "File not found. Please check the file path."
        
        elif "memory" in error_str or "out of memory" in error_str:
            return "Insufficient memory. Please try with smaller files."
        
        elif "timeout" in error_str:
            return "Operation timed out. Please try again."
        
        elif "json" in error_str or "parse" in error_str:
            return "Data parsing error. The file format may be corrupted."
        
        elif "credentials" in error_str or "authentication" in error_str:
            return "Authentication error. Please check your credentials."
        
        else:
            # Return generic error message with operation context
            if operation:
                return f"Error during {operation}: {str(error)}"
            else:
                return f"An unexpected error occurred: {str(error)}"

def handle_errors(operation: str = "", 
                 return_value: Any = None,
                 raise_on_error: bool = False):
    """
    Decorator for handling errors in functions
    
    Args:
        operation: Description of the operation
        return_value: Value to return on error
        raise_on_error: Whether to re-raise the exception
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            error_handler = ErrorHandler()
            
            try:
                return func(*args, **kwargs)
                
            except Exception as e:
                # Log the error
                context = operation or f"Function {func.__name__}"
                error_handler.log_error(e, context)
                
                # Re-raise if requested
                if raise_on_error:
                    raise
                
                # Return default value
                return return_value
        
        return wrapper
    return decorator

def safe_execute(func: Callable, *args, 
                default_return: Any = None, 
                context: str = "", **kwargs) -> tuple[bool, Any]:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        default_return: Default return value on error
        context: Context for error logging
        **kwargs: Function keyword arguments
        
    Returns:
        Tuple of (success: bool, result: Any)
    """
    error_handler = ErrorHandler()
    
    try:
        result = func(*args, **kwargs)
        return True, result
        
    except Exception as e:
        error_handler.log_error(e, context or f"Function {func.__name__}")
        return False, default_return

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

class ProcessingError(Exception):
    """Custom exception for processing errors"""
    pass

class ConfigurationError(Exception):
    """Custom exception for configuration errors"""
    pass

def validate_file_size(file_path: str, max_size_mb: int = 50) -> bool:
    """
    Validate file size
    
    Args:
        file_path: Path to file
        max_size_mb: Maximum size in MB
        
    Returns:
        True if valid, False otherwise
        
    Raises:
        ValidationError: If file is too large
    """
    try:
        file_size = os.path.getsize(file_path)
        max_size_bytes = max_size_mb * 1024 * 1024
        
        if file_size > max_size_bytes:
            raise ValidationError(
                f"File size ({file_size / 1024 / 1024:.2f} MB) "
                f"exceeds maximum limit ({max_size_mb} MB)"
            )
        
        return True
        
    except OSError as e:
        raise ValidationError(f"Cannot access file: {e}")

def validate_pdf_file(file_path: str) -> bool:
    """
    Validate PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        True if valid PDF
        
    Raises:
        ValidationError: If file is invalid
    """
    if not os.path.exists(file_path):
        raise ValidationError(f"File does not exist: {file_path}")
    
    if not file_path.lower().endswith('.pdf'):
        raise ValidationError(f"File is not a PDF: {file_path}")
    
    # Validate file size
    validate_file_size(file_path)
    
    return True

# Global error handler instance
error_handler = ErrorHandler()

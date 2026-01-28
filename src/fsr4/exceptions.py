#!/usr/bin/env python3
"""FSR4 Exception Classes

Version: 0.3.5d+patch9
"""


class FSR4Exception(Exception):
    """Base FSR4 exception
    
    All FSR4 exceptions inherit from this class.
    """
    pass


class FSR4InitializationError(FSR4Exception):
    """FSR4 initialization failed
    
    Raised when SDK initialization fails.
    """
    pass


class FSR4ContextError(FSR4Exception):
    """FSR4 context error
    
    Raised when context creation or operation fails.
    """
    pass


class FSR4ProcessingError(FSR4Exception):
    """FSR4 processing error
    
    Raised when upscaling or frame generation fails.
    """
    pass


class FSR4InvalidParameterError(FSR4Exception):
    """Invalid parameter
    
    Raised when invalid parameters are provided.
    """
    pass


class FSR4OutOfMemoryError(FSR4Exception):
    """Out of memory
    
    Raised when memory allocation fails.
    """
    pass


class FSR4DeviceNotFoundError(FSR4Exception):
    """Device not found
    
    Raised when rendering device is not available.
    """
    pass


class FSR4UnsupportedFormatError(FSR4Exception):
    """Unsupported format
    
    Raised when frame format is not supported.
    """
    pass

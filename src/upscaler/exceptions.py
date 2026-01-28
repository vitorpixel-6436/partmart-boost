#!/usr/bin/env python3
"""Upscaler Exceptions

Version: 0.4.0-alpha
"""


class UpscalerException(Exception):
    """Base upscaler exception"""
    pass


class UpscalerInitializationError(UpscalerException):
    """Initialization failed"""
    pass


class UpscalerBackendError(UpscalerException):
    """Backend error"""
    pass


class UpscalerDLLNotFoundError(UpscalerException):
    """DLL/SO not found"""
    pass

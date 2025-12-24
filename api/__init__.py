"""
API package for MinLens application.

This package contains all API endpoints and related functionality.
"""

from .endpoints import router as api_router

__all__ = ['api_router']

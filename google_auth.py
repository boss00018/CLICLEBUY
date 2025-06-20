from fastapi import Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import os

# Dummy functions for when Google OAuth is not configured
oauth = None
def extract_domain(email):
    """Extract domain from email address"""
    try:
        return email.split('@')[1]
    except (IndexError, AttributeError):
        return None

def create_google_user(db, user_data):
    """Create a new user from Google data - dummy implementation"""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google authentication is not configured. Please use regular login."
    )
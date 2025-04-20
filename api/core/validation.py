"""
Validation utilities for the Songs API.
"""

import re
from typing import Tuple

def validate_bucket_name(bucket: str) -> Tuple[bool, str]:
    """
    Validate S3 bucket name format.
    Returns (is_valid, error_message)
    """
    if not bucket:
        return False, "Bucket name cannot be empty"
    
    # Bucket name rules:
    # - 3 to 63 characters long
    # - Can contain lowercase letters, numbers, dots, and hyphens
    # - Must start and end with a letter or number
    # - Cannot contain two adjacent dots
    # - Cannot be formatted as an IP address
    if len(bucket) < 3 or len(bucket) > 63:
        return False, "Bucket name must be between 3 and 63 characters long"
    
    if not re.match(r'^[a-z0-9][a-z0-9.-]*[a-z0-9]$', bucket):
        return False, "Bucket name can only contain lowercase letters, numbers, dots, and hyphens, and must start and end with a letter or number"
    
    if '..' in bucket:
        return False, "Bucket name cannot contain two adjacent dots"
    
    # Check if it looks like an IP address
    if re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', bucket):
        return False, "Bucket name cannot be formatted as an IP address"
    
    return True, ""

def validate_object_key(key: str) -> Tuple[bool, str]:
    """
    Validate S3 object key format.
    Returns (is_valid, error_message)
    """
    if not key:
        return False, "Object key cannot be empty"
    
    # Key rules:
    # - Maximum 1024 characters
    # - Cannot contain control characters
    # - Cannot contain consecutive slashes
    if len(key) > 1024:
        return False, "Object key cannot exceed 1024 characters"
    
    if re.search(r'[\x00-\x1F\x7F]', key):
        return False, "Object key cannot contain control characters"
    
    if '//' in key:
        return False, "Object key cannot contain consecutive slashes"
    
    return True, "" 
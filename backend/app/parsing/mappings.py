"""
Test name mapping module

This module provides functionality to map raw test names from OCR output
to canonical TestType records using the TestAlias table.
"""

from sqlalchemy.orm import Session
from app.db.models import TestAlias, TestType


def map_test_name_to_type(
    db: Session, 
    raw_name: str
) -> TestType | None:
    """
    Look up raw test name in TestAlias table and return canonical TestType.
    
    This function performs case-insensitive alias lookup to handle variations
    in lab report formatting. If no match is found, returns None.
    
    Args:
        db: SQLAlchemy database session
        raw_name: Raw test name extracted from OCR output
        
    Returns:
        TestType object if alias found, None otherwise
        
    Examples:
        >>> test_type = map_test_name_to_type(db, "White Blood Cells")
        >>> test_type.key
        'WBC'
        
        >>> test_type = map_test_name_to_type(db, "wbc")
        >>> test_type.key
        'WBC'
        
        >>> result = map_test_name_to_type(db, "unknown_test")
        >>> result is None
        True
    """
    # Normalize raw_name: lowercase and strip whitespace
    normalized = raw_name.strip().lower()
    
    # Handle empty string case
    if not normalized:
        return None
    
    # Query TestAlias table with case-insensitive lookup
    alias = db.query(TestAlias).filter(
        TestAlias.alias == normalized
    ).first()
    
    # Return the associated TestType if alias found, None otherwise
    if alias:
        return alias.test_type
    return None

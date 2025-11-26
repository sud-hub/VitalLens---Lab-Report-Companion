from sqlalchemy.orm import Session
from app.db.models import TestResult, TestType, Panel, Report
from datetime import datetime


def create_test_result(
    db: Session,
    report_id: int,
    test_type_id: int,
    value: float,
    unit: str,
    status: str,
    confidence: float | None = None
) -> TestResult:
    """
    Create a new test result record.
    
    Args:
        db: Database session
        report_id: ID of the report this result belongs to
        test_type_id: ID of the test type
        value: Numeric test value
        unit: Unit of measurement
        status: Status (LOW, NORMAL, HIGH, etc.)
        confidence: Optional OCR confidence score
        
    Returns:
        Newly created TestResult object
        
    Validates: Requirements 8.1, 8.2
    """
    db_test_result = TestResult(
        report_id=report_id,
        test_type_id=test_type_id,
        value=value,
        unit=unit,
        status=status,
        confidence=confidence
    )
    db.add(db_test_result)
    db.commit()
    db.refresh(db_test_result)
    return db_test_result


def get_test_history(
    db: Session,
    user_id: int,
    test_key: str
) -> list[TestResult]:
    """
    Get all test results for a specific user and test type, ordered chronologically.
    
    Args:
        db: Database session
        user_id: ID of the user
        test_key: Key of the test type (e.g., 'WBC', 'GLUCOSE')
        
    Returns:
        List of TestResult objects ordered by timestamp (oldest to newest)
        
    Validates: Requirements 11.1, 11.2
    """
    return (
        db.query(TestResult)
        .join(TestResult.report)
        .join(TestResult.test_type)
        .filter(Report.user_id == user_id)
        .filter(TestType.key == test_key)
        .order_by(TestResult.created_at.asc())
        .all()
    )


def get_latest_test_result(
    db: Session,
    user_id: int,
    test_key: str
) -> TestResult | None:
    """
    Get the most recent test result for a specific user and test type.
    
    Args:
        db: Database session
        user_id: ID of the user
        test_key: Key of the test type (e.g., 'WBC', 'GLUCOSE')
        
    Returns:
        Most recent TestResult object, or None if no results exist
        
    Validates: Requirements 12.1
    """
    return (
        db.query(TestResult)
        .join(TestResult.report)
        .join(TestResult.test_type)
        .filter(Report.user_id == user_id)
        .filter(TestType.key == test_key)
        .order_by(TestResult.created_at.desc())
        .first()
    )


def get_previous_test_result(
    db: Session,
    user_id: int,
    test_key: str,
    before_timestamp: datetime
) -> TestResult | None:
    """
    Get the test result immediately before a given timestamp.
    
    Args:
        db: Database session
        user_id: ID of the user
        test_key: Key of the test type
        before_timestamp: Get result before this timestamp
        
    Returns:
        Previous TestResult object, or None if no earlier results exist
        
    Validates: Requirements 12.2
    """
    return (
        db.query(TestResult)
        .join(TestResult.report)
        .join(TestResult.test_type)
        .filter(Report.user_id == user_id)
        .filter(TestType.key == test_key)
        .filter(TestResult.created_at < before_timestamp)
        .order_by(TestResult.created_at.desc())
        .first()
    )


def get_test_type_by_key(db: Session, test_key: str) -> TestType | None:
    """
    Get a test type by its key.
    
    Args:
        db: Database session
        test_key: Key of the test type (e.g., 'WBC', 'GLUCOSE')
        
    Returns:
        TestType object, or None if not found
    """
    from sqlalchemy.orm import joinedload
    return db.query(TestType).options(joinedload(TestType.panel)).filter(TestType.key == test_key).first()

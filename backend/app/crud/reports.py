from sqlalchemy.orm import Session
from app.db.models import Report
from datetime import datetime


def create_report(db: Session, user_id: int, filename: str) -> Report:
    """
    Create a new report record.
    
    Args:
        db: Database session
        user_id: ID of the user uploading the report
        filename: Original filename of the uploaded file
        
    Returns:
        Newly created Report object
        
    Validates: Requirements 3.1, 3.4, 3.5
    """
    db_report = Report(
        user_id=user_id,
        original_filename=filename,
        parsed_success=False
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report


def update_report_ocr(
    db: Session, 
    report_id: int, 
    raw_text: str, 
    success: bool,
    notes: str | None = None,
    patient_gender: str | None = None,
    patient_age: int | None = None
) -> Report:
    """
    Update a report with OCR results, parsing status, and patient demographics.
    
    Args:
        db: Database session
        report_id: ID of the report to update
        raw_text: Raw text extracted from OCR
        success: Whether parsing was successful
        notes: Optional notes about the processing
        patient_gender: Patient gender ('M' or 'F')
        patient_age: Patient age in years
        
    Returns:
        Updated Report object
        
    Validates: Requirements 4.3, 8.3, 8.4
    """
    db_report = db.query(Report).filter(Report.id == report_id).first()
    
    if db_report is None:
        raise ValueError(f"Report with id {report_id} not found")
    
    db_report.raw_ocr_text = raw_text
    db_report.parsed_success = success
    
    if notes is not None:
        db_report.notes = notes
    
    # Save patient demographics if provided
    if patient_gender is not None:
        db_report.patient_gender = patient_gender
    if patient_age is not None:
        db_report.patient_age = patient_age
    
    db.commit()
    db.refresh(db_report)
    return db_report


def get_report_by_id(db: Session, report_id: int) -> Report | None:
    """
    Retrieve a report by ID.
    
    Args:
        db: Database session
        report_id: ID of the report to retrieve
        
    Returns:
        Report object if found, None otherwise
    """
    return db.query(Report).filter(Report.id == report_id).first()


def get_user_reports(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[Report]:
    """
    Retrieve all reports for a specific user.
    
    Args:
        db: Database session
        user_id: ID of the user
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of Report objects
    """
    return (
        db.query(Report)
        .filter(Report.user_id == user_id)
        .order_by(Report.uploaded_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

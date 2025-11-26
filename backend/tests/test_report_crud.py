"""
Tests for report CRUD operations.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.db.models import User, Report
from app.crud.reports import (
    create_report,
    update_report_ocr,
    get_report_by_id,
    get_user_reports
)
from app.core.security import get_password_hash


# Create in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    """Create a test user"""
    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def test_create_report(db, test_user):
    """Test creating a new report"""
    report = create_report(
        db=db,
        user_id=test_user.id,
        filename="test_report.pdf"
    )
    
    assert report.id is not None
    assert report.user_id == test_user.id
    assert report.original_filename == "test_report.pdf"
    assert report.parsed_success is False
    assert report.raw_ocr_text is None
    assert report.uploaded_at is not None


def test_update_report_ocr_success(db, test_user):
    """Test updating a report with successful OCR results"""
    # Create a report
    report = create_report(
        db=db,
        user_id=test_user.id,
        filename="test_report.pdf"
    )
    
    # Update with OCR results
    ocr_text = "WBC: 7.2 10^3/uL\nRBC: 4.8 10^6/uL"
    updated_report = update_report_ocr(
        db=db,
        report_id=report.id,
        raw_text=ocr_text,
        success=True,
        notes="Successfully parsed 2 tests"
    )
    
    assert updated_report.id == report.id
    assert updated_report.raw_ocr_text == ocr_text
    assert updated_report.parsed_success is True
    assert updated_report.notes == "Successfully parsed 2 tests"


def test_update_report_ocr_failure(db, test_user):
    """Test updating a report with failed OCR results"""
    # Create a report
    report = create_report(
        db=db,
        user_id=test_user.id,
        filename="test_report.pdf"
    )
    
    # Update with failed OCR
    updated_report = update_report_ocr(
        db=db,
        report_id=report.id,
        raw_text="",
        success=False,
        notes="No text extracted"
    )
    
    assert updated_report.id == report.id
    assert updated_report.raw_ocr_text == ""
    assert updated_report.parsed_success is False
    assert updated_report.notes == "No text extracted"


def test_update_report_ocr_nonexistent(db):
    """Test updating a non-existent report raises error"""
    with pytest.raises(ValueError, match="Report with id 999 not found"):
        update_report_ocr(
            db=db,
            report_id=999,
            raw_text="test",
            success=False
        )


def test_get_report_by_id(db, test_user):
    """Test retrieving a report by ID"""
    # Create a report
    report = create_report(
        db=db,
        user_id=test_user.id,
        filename="test_report.pdf"
    )
    
    # Retrieve it
    retrieved = get_report_by_id(db=db, report_id=report.id)
    
    assert retrieved is not None
    assert retrieved.id == report.id
    assert retrieved.original_filename == "test_report.pdf"


def test_get_report_by_id_nonexistent(db):
    """Test retrieving a non-existent report returns None"""
    retrieved = get_report_by_id(db=db, report_id=999)
    assert retrieved is None


def test_get_user_reports(db, test_user):
    """Test retrieving all reports for a user"""
    # Create multiple reports
    report1 = create_report(db=db, user_id=test_user.id, filename="report1.pdf")
    report2 = create_report(db=db, user_id=test_user.id, filename="report2.pdf")
    report3 = create_report(db=db, user_id=test_user.id, filename="report3.pdf")
    
    # Retrieve all reports
    reports = get_user_reports(db=db, user_id=test_user.id)
    
    assert len(reports) == 3
    # Verify all reports are present (order may vary due to timestamp precision)
    report_ids = {r.id for r in reports}
    assert report1.id in report_ids
    assert report2.id in report_ids
    assert report3.id in report_ids


def test_get_user_reports_pagination(db, test_user):
    """Test pagination of user reports"""
    # Create multiple reports
    for i in range(5):
        create_report(db=db, user_id=test_user.id, filename=f"report{i}.pdf")
    
    # Get first 2 reports
    reports_page1 = get_user_reports(db=db, user_id=test_user.id, skip=0, limit=2)
    assert len(reports_page1) == 2
    
    # Get next 2 reports
    reports_page2 = get_user_reports(db=db, user_id=test_user.id, skip=2, limit=2)
    assert len(reports_page2) == 2
    
    # Ensure they're different
    assert reports_page1[0].id != reports_page2[0].id


def test_get_user_reports_empty(db, test_user):
    """Test retrieving reports for user with no reports"""
    reports = get_user_reports(db=db, user_id=test_user.id)
    assert len(reports) == 0


def test_report_user_relationship(db, test_user):
    """Test that report is properly linked to user"""
    report = create_report(
        db=db,
        user_id=test_user.id,
        filename="test_report.pdf"
    )
    
    # Access user through relationship
    assert report.user.id == test_user.id
    assert report.user.email == test_user.email
    
    # Access reports through user relationship
    assert len(test_user.reports) == 1
    assert test_user.reports[0].id == report.id

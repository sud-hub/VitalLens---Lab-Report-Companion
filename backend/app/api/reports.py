"""
Reports API router

This module provides endpoints for uploading and managing lab reports.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.db.models import User
from app.schemas.reports import ReportSummary
from app.crud import reports as report_crud
from app.crud import tests as test_crud
from app.ocr.engine import run_ocr_on_image_bytes
from app.parsing.lab_parser import parse_lab_report
from app.parsing.mappings import map_test_name_to_type
from app.rules.reference_ranges import compute_status


router = APIRouter(prefix="/reports", tags=["reports"])


# Supported file types
SUPPORTED_IMAGE_TYPES = {"image/jpeg", "image/jpg", "image/png"}
SUPPORTED_PDF_TYPE = "application/pdf"
SUPPORTED_FILE_TYPES = SUPPORTED_IMAGE_TYPES | {SUPPORTED_PDF_TYPE}

# Maximum file size: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB in bytes


@router.post("/upload", response_model=ReportSummary, status_code=status.HTTP_201_CREATED)
async def upload_report(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload a lab report image or PDF for processing.
    
    This endpoint:
    1. Validates file type and size
    2. Creates a Report record
    3. Runs OCR on the uploaded file
    4. Parses OCR results to extract test values
    5. Maps test names to TestTypes using aliases
    6. Computes status for each test based on reference ranges
    7. Saves TestResult records
    8. Marks Report as successful or failed
    
    Args:
        file: Uploaded file (JPEG, PNG, or PDF)
        current_user: Authenticated user (from JWT token)
        db: Database session
        
    Returns:
        ReportSummary with upload details and test count
        
    Raises:
        HTTPException 400: If file type is unsupported or file is too large
        HTTPException 500: If OCR or parsing fails
        
    Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.3, 4.4,
               5.1, 5.2, 5.3, 5.4, 5.5, 6.1, 6.2, 6.3,
               7.1, 7.2, 7.3, 7.5, 8.1, 8.2, 8.3, 8.4
    """
    
    # Requirement 3.3: Validate file type
    if file.content_type not in SUPPORTED_FILE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file.content_type}. "
                   f"Supported types: JPEG, PNG, PDF"
        )
    
    # Read file bytes
    file_bytes = await file.read()
    
    # Requirement 3.2: Validate file size (10MB limit)
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large: {len(file_bytes)} bytes. "
                   f"Maximum size: {MAX_FILE_SIZE} bytes (10MB)"
        )
    
    # Requirement 3.1, 3.4, 3.5: Create Report record
    report = report_crud.create_report(
        db=db,
        user_id=current_user.id,
        filename=file.filename or "unknown"
    )
    
    try:
        # Requirement 4.1: Run OCR on uploaded file
        is_pdf = file.content_type == SUPPORTED_PDF_TYPE
        ocr_result = run_ocr_on_image_bytes(file_bytes, is_pdf=is_pdf)
        
        # Requirement 4.3: Store raw OCR text
        raw_text = ocr_result.get("raw_text", "")
        
        # Requirement 4.4: Handle OCR failure
        if not raw_text:
            report_crud.update_report_ocr(
                db=db,
                report_id=report.id,
                raw_text="",
                success=False,
                notes="OCR extraction failed: no text extracted"
            )
            return ReportSummary(
                id=report.id,
                original_filename=report.original_filename,
                uploaded_at=report.uploaded_at,
                parsed_success=False,
                test_count=0
            )
        
        # Requirements 5.1, 5.2, 5.3, 5.4, 5.5: Parse OCR results
        parsed_tests = parse_lab_report(ocr_result)
        
        # Track successfully saved test results
        saved_count = 0
        skipped_tests = []
        
        # Process each parsed test
        for test_data in parsed_tests:
            test_name_raw = test_data.get("test_name_raw")
            value = test_data.get("value")
            unit = test_data.get("unit", "")
            
            # Requirements 6.1, 6.2: Map test name to TestType using aliases
            test_type = map_test_name_to_type(db, test_name_raw)
            
            # Requirement 6.3: Skip unknown test names
            if test_type is None:
                skipped_tests.append(test_name_raw)
                continue
            
            # Requirements 7.1, 7.2, 7.3: Compute status based on reference ranges
            test_status = compute_status(test_type, value)
            
            # Requirements 8.1, 8.2: Save TestResult record
            test_crud.create_test_result(
                db=db,
                report_id=report.id,
                test_type_id=test_type.id,
                value=value,
                unit=unit,
                status=test_status,
                confidence=ocr_result.get("confidence")
            )
            
            saved_count += 1
        
        # Requirement 8.3: Mark Report as successful if tests were saved
        success = saved_count > 0
        notes = None
        if skipped_tests:
            notes = f"Skipped {len(skipped_tests)} unknown tests: {', '.join(skipped_tests[:5])}"
            if len(skipped_tests) > 5:
                notes += f" and {len(skipped_tests) - 5} more"
        
        # Requirement 8.4: Update report with final status
        report = report_crud.update_report_ocr(
            db=db,
            report_id=report.id,
            raw_text=raw_text,
            success=success,
            notes=notes
        )
        
        return ReportSummary(
            id=report.id,
            original_filename=report.original_filename,
            uploaded_at=report.uploaded_at,
            parsed_success=report.parsed_success,
            test_count=saved_count
        )
        
    except Exception as e:
        # Handle any processing errors
        report_crud.update_report_ocr(
            db=db,
            report_id=report.id,
            raw_text="",
            success=False,
            notes=f"Processing error: {str(e)}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process report: {str(e)}"
        )

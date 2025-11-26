from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_db, get_current_user
from app.db.models import User
from app.crud.panels import get_all_panels, get_panel_by_key, get_panel_tests
from app.crud.tests import get_test_history, get_test_type_by_key, get_latest_test_result, get_previous_test_result
from app.schemas.panels import PanelResponse, TestTypeResponse
from app.schemas.tests import (
    TestHistoryResponse, 
    TestHistoryMetadata, 
    TestHistoryDataPoint,
    LatestInsightResponse,
    LatestTestResult,
    GuidanceData
)
from app.rules.guidance_engine import generate_guidance

router = APIRouter(tags=["tests"])


@router.get("/panels", response_model=list[PanelResponse])
def get_panels(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all supported lab panels.
    
    Requirements:
    - 9.1: Return all three panel records (CBC, METABOLIC, LIPID)
    - 9.2: Include panel key and display name
    - 9.3: Require authentication (401 if not authenticated)
    - 9.5: Return results in consistent order
    """
    panels = get_all_panels(db)
    return panels


@router.get("/panels/{panel_key}/tests", response_model=list[TestTypeResponse])
def get_panel_tests_endpoint(
    panel_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all test types for a specific panel.
    
    Requirements:
    - 10.1: Return all TestType records associated with panel
    - 10.2: Include test key, display name, unit, and reference ranges
    - 10.3: Return 404 for non-existent panel
    - 10.4: Return empty list if panel has no tests
    - 10.5: Require authentication (401 if not authenticated)
    """
    # Check if panel exists
    panel = get_panel_by_key(db, panel_key)
    if not panel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Panel with key '{panel_key}' not found"
        )
    
    # Get tests for the panel
    tests = get_panel_tests(db, panel_key)
    return tests


@router.get("/tests/{test_key}/history", response_model=TestHistoryResponse)
def get_test_history_endpoint(
    test_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get historical test results for a specific test type.
    
    Requirements:
    - 11.1: Return all TestResult records for user and test type ordered by timestamp
    - 11.2: Include timestamp, value, unit, and status for each result
    - 11.3: Return empty data array if user has no results
    - 11.4: Return 404 for non-existent test key
    - 11.5: Include panel key, test key, display name, and unit metadata
    """
    # Check if test type exists
    test_type = get_test_type_by_key(db, test_key)
    if not test_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with key '{test_key}' not found"
        )
    
    # Get test history for the user
    test_results = get_test_history(db, current_user.id, test_key)
    
    # Build metadata
    metadata = TestHistoryMetadata(
        panel_key=test_type.panel.key,
        test_key=test_type.key,
        display_name=test_type.display_name,
        unit=test_type.unit,
        ref_low=test_type.ref_low,
        ref_high=test_type.ref_high
    )
    
    # Build data points
    data = [
        TestHistoryDataPoint(
            timestamp=result.created_at,
            value=result.value,
            unit=result.unit,
            status=result.status
        )
        for result in test_results
    ]
    
    return TestHistoryResponse(metadata=metadata, data=data)


@router.get("/tests/{test_key}/latest-insight", response_model=LatestInsightResponse)
def get_latest_insight(
    test_key: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get the latest test result with educational insights and trend information.
    
    Requirements:
    - 12.1: Return the most recent TestResult for user and test type
    - 12.2: Include previous result for comparison when available
    - 12.3: Provide general educational message about the test result
    - 12.4: Compute trend indicator (improving, worsening, stable)
    - 12.5: Include prominent disclaimer stating information is not a medical diagnosis
    """
    # Check if test type exists
    test_type = get_test_type_by_key(db, test_key)
    if not test_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Test with key '{test_key}' not found"
        )
    
    # Requirement 12.1: Get latest test result
    latest_result = get_latest_test_result(db, current_user.id, test_key)
    if not latest_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No test results found for test '{test_key}'"
        )
    
    # Requirement 12.2: Get previous result for comparison
    previous_result = get_previous_test_result(
        db, 
        current_user.id, 
        test_key, 
        latest_result.created_at
    )
    
    # Requirements 12.3, 12.4, 12.5: Generate guidance with trend and disclaimer
    guidance_data = generate_guidance(
        test_type=test_type,
        value=latest_result.value,
        status=latest_result.status,
        previous_value=previous_result.value if previous_result else None
    )
    
    # Build response
    latest = LatestTestResult(
        timestamp=latest_result.created_at,
        value=latest_result.value,
        unit=latest_result.unit,
        status=latest_result.status
    )
    
    previous = None
    if previous_result:
        previous = LatestTestResult(
            timestamp=previous_result.created_at,
            value=previous_result.value,
            unit=previous_result.unit,
            status=previous_result.status
        )
    
    guidance = GuidanceData(
        message=guidance_data["message"],
        trend=guidance_data["trend"],
        suggestions=guidance_data["suggestions"],
        disclaimer=guidance_data["disclaimer"]
    )
    
    return LatestInsightResponse(
        latest=latest,
        previous=previous,
        guidance=guidance
    )

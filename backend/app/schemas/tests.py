from pydantic import BaseModel, Field
from datetime import datetime


class TestResultBase(BaseModel):
    """Base schema for TestResult"""
    value: float
    unit: str
    status: str


class TestResultCreate(BaseModel):
    """Schema for creating a test result"""
    report_id: int
    test_type_id: int
    value: float
    unit: str
    status: str
    confidence: float | None = None


class TestResultResponse(TestResultBase):
    """Schema for test result response"""
    id: int
    report_id: int
    test_type_id: int
    confidence: float | None = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class TestHistoryDataPoint(BaseModel):
    """Schema for a single data point in test history"""
    timestamp: datetime = Field(description="When the test was taken")
    value: float = Field(description="Test value")
    unit: str = Field(description="Unit of measurement")
    status: str = Field(description="Status: LOW, NORMAL, HIGH, etc.")
    
    class Config:
        from_attributes = True


class TestHistoryMetadata(BaseModel):
    """Schema for test metadata"""
    panel_key: str = Field(description="Panel key (CBC, METABOLIC, LIPID)")
    test_key: str = Field(description="Test key (WBC, GLUCOSE, etc.)")
    display_name: str = Field(description="Human-readable test name")
    unit: str = Field(description="Unit of measurement")
    ref_low: float | None = Field(description="Reference range low value")
    ref_high: float | None = Field(description="Reference range high value")


class TestHistoryResponse(BaseModel):
    """Schema for test history response"""
    metadata: TestHistoryMetadata
    data: list[TestHistoryDataPoint] = Field(description="Historical test results")
    
    class Config:
        from_attributes = True


class LatestTestResult(BaseModel):
    """Schema for latest test result"""
    timestamp: datetime
    value: float
    unit: str
    status: str
    
    class Config:
        from_attributes = True


class GuidanceData(BaseModel):
    """Schema for guidance information"""
    message: str = Field(description="Educational message about the test result")
    trend: str | None = Field(description="Trend indicator: improving, worsening, stable, or None")
    suggestions: list[str] = Field(description="List of general suggestions")
    disclaimer: str = Field(description="Medical disclaimer")


class LatestInsightResponse(BaseModel):
    """Schema for latest insight response"""
    latest: LatestTestResult
    previous: LatestTestResult | None = Field(
        description="Previous test result for comparison, if available"
    )
    guidance: GuidanceData = Field(description="Educational guidance and insights")
    
    class Config:
        from_attributes = True

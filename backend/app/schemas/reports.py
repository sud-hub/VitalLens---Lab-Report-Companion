from pydantic import BaseModel, Field
from datetime import datetime


class ReportBase(BaseModel):
    """Base schema for Report"""
    original_filename: str


class ReportCreate(BaseModel):
    """Schema for creating a report"""
    original_filename: str
    user_id: int


class ReportUpdate(BaseModel):
    """Schema for updating a report with OCR results"""
    raw_ocr_text: str | None = None
    parsed_success: bool = False
    notes: str | None = None


class ReportResponse(ReportBase):
    """Schema for report response"""
    id: int
    user_id: int
    uploaded_at: datetime
    raw_ocr_text: str | None = None
    parsed_success: bool
    notes: str | None = None
    
    class Config:
        from_attributes = True


class ReportSummary(BaseModel):
    """Schema for report summary after upload"""
    id: int
    original_filename: str
    uploaded_at: datetime
    parsed_success: bool
    test_count: int = Field(description="Number of test results extracted")
    
    class Config:
        from_attributes = True

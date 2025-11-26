from pydantic import BaseModel


class PanelBase(BaseModel):
    """Base schema for Panel"""
    key: str
    display_name: str


class PanelResponse(PanelBase):
    """Response schema for Panel"""
    id: int
    
    class Config:
        from_attributes = True


class TestTypeBase(BaseModel):
    """Base schema for TestType"""
    key: str
    display_name: str
    unit: str
    ref_low: float | None = None
    ref_high: float | None = None


class TestTypeResponse(TestTypeBase):
    """Response schema for TestType"""
    id: int
    panel_id: int
    
    class Config:
        from_attributes = True

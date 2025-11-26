from sqlalchemy.orm import Session
from app.db.models import Panel, TestType


def get_all_panels(db: Session) -> list[Panel]:
    """
    Get all lab panels.
    
    Requirements:
    - 9.1: Return all three panel records (CBC, METABOLIC, LIPID)
    - 9.5: Return results in consistent order
    """
    return db.query(Panel).order_by(Panel.id).all()


def get_panel_by_key(db: Session, panel_key: str) -> Panel | None:
    """
    Get a panel by its key.
    
    Requirements:
    - 10.3: Handle non-existent panel requests
    """
    return db.query(Panel).filter(Panel.key == panel_key.upper()).first()


def get_panel_tests(db: Session, panel_key: str) -> list[TestType]:
    """
    Get all test types for a specific panel.
    
    Requirements:
    - 10.1: Return all TestType records associated with panel
    - 10.4: Return empty list if panel has no tests
    """
    panel = get_panel_by_key(db, panel_key)
    if not panel:
        return []
    
    return db.query(TestType).filter(
        TestType.panel_id == panel.id
    ).order_by(TestType.id).all()

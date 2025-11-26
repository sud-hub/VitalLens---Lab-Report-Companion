"""Verify seed data was created correctly"""

from app.db.session import SessionLocal
from app.db.models import Panel, TestType, TestAlias

db = SessionLocal()

try:
    # Check panels
    panels = db.query(Panel).all()
    print(f"Panels: {len(panels)}")
    for p in panels:
        print(f"  - {p.key}: {p.display_name}")
    
    # Check test types by panel
    print(f"\nTest Types: {db.query(TestType).count()}")
    for panel in panels:
        tests = db.query(TestType).filter(TestType.panel_id == panel.id).all()
        print(f"  {panel.key}: {len(tests)} tests")
        for test in tests:
            print(f"    - {test.key}: {test.display_name} ({test.unit})")
            print(f"      Range: {test.ref_low} - {test.ref_high}")
    
    # Check aliases
    aliases = db.query(TestAlias).all()
    print(f"\nTotal Aliases: {len(aliases)}")
    
    # Sample some aliases
    print("\nSample aliases:")
    for test_key in ["WBC", "GLUCOSE", "LDL"]:
        test_type = db.query(TestType).filter(TestType.key == test_key).first()
        if test_type:
            test_aliases = db.query(TestAlias).filter(TestAlias.test_type_id == test_type.id).all()
            print(f"  {test_key}: {[a.alias for a in test_aliases[:5]]}")
    
finally:
    db.close()

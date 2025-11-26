"""
Database seed script for Lab Report Companion

This script populates the database with:
- Panel records (CBC, METABOLIC, LIPID)
- TestType records with reference ranges
- TestAlias records for common test name variations

Run this script after running migrations:
    python seed_data.py
"""

import os
from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, Session, relationship, declarative_base
from sqlalchemy.sql import func
from pydantic_settings import BaseSettings

# Load settings
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./lab_companion.db"
    
    class Config:
        env_file = ".env"

settings = Settings()

# Create base and models inline to avoid circular imports
Base = declarative_base()


class Panel(Base):
    __tablename__ = "panels"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    
    test_types = relationship("TestType", back_populates="panel")


class TestType(Base):
    __tablename__ = "test_types"
    
    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(Integer, ForeignKey("panels.id"), nullable=False)
    key = Column(String, unique=True, nullable=False)
    display_name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    ref_low = Column(Float, nullable=True)
    ref_high = Column(Float, nullable=True)
    
    panel = relationship("Panel", back_populates="test_types")
    aliases = relationship("TestAlias", back_populates="test_type")


class TestAlias(Base):
    __tablename__ = "test_aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, unique=True, nullable=False)
    test_type_id = Column(Integer, ForeignKey("test_types.id"), nullable=False)
    
    test_type = relationship("TestType", back_populates="aliases")


# Create engine and session
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def seed_panels(db: Session):
    """Create the three supported lab panels"""
    panels_data = [
        {"key": "CBC", "display_name": "Complete Blood Count"},
        {"key": "METABOLIC", "display_name": "Metabolic Panel"},
        {"key": "LIPID", "display_name": "Lipid Panel"},
    ]
    
    panels = {}
    for panel_data in panels_data:
        # Check if panel already exists
        existing = db.query(Panel).filter(Panel.key == panel_data["key"]).first()
        if existing:
            panels[panel_data["key"]] = existing
            print(f"Panel {panel_data['key']} already exists, skipping...")
        else:
            panel = Panel(**panel_data)
            db.add(panel)
            db.flush()  # Get the ID
            panels[panel_data["key"]] = panel
            print(f"Created panel: {panel_data['display_name']}")
    
    db.commit()
    return panels


def seed_cbc_tests(db: Session, panel: Panel):
    """Create CBC test types with reference ranges"""
    cbc_tests = [
        {
            "key": "WBC",
            "display_name": "White Blood Cells",
            "unit": "10^3/µL",
            "ref_low": 4.5,
            "ref_high": 11.0,
        },
        {
            "key": "RBC",
            "display_name": "Red Blood Cells",
            "unit": "10^6/µL",
            "ref_low": 4.5,
            "ref_high": 5.9,
        },
        {
            "key": "HGB",
            "display_name": "Hemoglobin",
            "unit": "g/dL",
            "ref_low": 13.5,
            "ref_high": 17.5,
        },
        {
            "key": "HCT",
            "display_name": "Hematocrit",
            "unit": "%",
            "ref_low": 38.8,
            "ref_high": 50.0,
        },
        {
            "key": "PLT",
            "display_name": "Platelets",
            "unit": "10^3/µL",
            "ref_low": 150.0,
            "ref_high": 400.0,
        },
        {
            "key": "MCV",
            "display_name": "Mean Corpuscular Volume",
            "unit": "fL",
            "ref_low": 80.0,
            "ref_high": 100.0,
        },
    ]
    
    test_types = {}
    for test_data in cbc_tests:
        existing = db.query(TestType).filter(TestType.key == test_data["key"]).first()
        if existing:
            test_types[test_data["key"]] = existing
            print(f"  Test {test_data['key']} already exists, skipping...")
        else:
            test_type = TestType(panel_id=panel.id, **test_data)
            db.add(test_type)
            db.flush()
            test_types[test_data["key"]] = test_type
            print(f"  Created test: {test_data['display_name']}")
    
    db.commit()
    return test_types


def seed_metabolic_tests(db: Session, panel: Panel):
    """Create Metabolic Panel test types with reference ranges"""
    metabolic_tests = [
        {
            "key": "GLUCOSE",
            "display_name": "Glucose",
            "unit": "mg/dL",
            "ref_low": 70.0,
            "ref_high": 100.0,
        },
        {
            "key": "BUN",
            "display_name": "Blood Urea Nitrogen",
            "unit": "mg/dL",
            "ref_low": 7.0,
            "ref_high": 20.0,
        },
        {
            "key": "CREATININE",
            "display_name": "Creatinine",
            "unit": "mg/dL",
            "ref_low": 0.7,
            "ref_high": 1.3,
        },
        {
            "key": "SODIUM",
            "display_name": "Sodium",
            "unit": "mmol/L",
            "ref_low": 136.0,
            "ref_high": 145.0,
        },
        {
            "key": "POTASSIUM",
            "display_name": "Potassium",
            "unit": "mmol/L",
            "ref_low": 3.5,
            "ref_high": 5.0,
        },
        {
            "key": "CHLORIDE",
            "display_name": "Chloride",
            "unit": "mmol/L",
            "ref_low": 98.0,
            "ref_high": 107.0,
        },
        {
            "key": "CO2",
            "display_name": "Carbon Dioxide",
            "unit": "mmol/L",
            "ref_low": 23.0,
            "ref_high": 29.0,
        },
        {
            "key": "CALCIUM",
            "display_name": "Calcium",
            "unit": "mg/dL",
            "ref_low": 8.5,
            "ref_high": 10.5,
        },
    ]
    
    test_types = {}
    for test_data in metabolic_tests:
        existing = db.query(TestType).filter(TestType.key == test_data["key"]).first()
        if existing:
            test_types[test_data["key"]] = existing
            print(f"  Test {test_data['key']} already exists, skipping...")
        else:
            test_type = TestType(panel_id=panel.id, **test_data)
            db.add(test_type)
            db.flush()
            test_types[test_data["key"]] = test_type
            print(f"  Created test: {test_data['display_name']}")
    
    db.commit()
    return test_types


def seed_lipid_tests(db: Session, panel: Panel):
    """Create Lipid Panel test types with reference ranges"""
    lipid_tests = [
        {
            "key": "TC",
            "display_name": "Total Cholesterol",
            "unit": "mg/dL",
            "ref_low": 0.0,
            "ref_high": 200.0,
        },
        {
            "key": "LDL",
            "display_name": "LDL Cholesterol",
            "unit": "mg/dL",
            "ref_low": 0.0,
            "ref_high": 100.0,
        },
        {
            "key": "HDL",
            "display_name": "HDL Cholesterol",
            "unit": "mg/dL",
            "ref_low": 40.0,
            "ref_high": 999.0,
        },
        {
            "key": "TRIG",
            "display_name": "Triglycerides",
            "unit": "mg/dL",
            "ref_low": 0.0,
            "ref_high": 150.0,
        },
    ]
    
    test_types = {}
    for test_data in lipid_tests:
        existing = db.query(TestType).filter(TestType.key == test_data["key"]).first()
        if existing:
            test_types[test_data["key"]] = existing
            print(f"  Test {test_data['key']} already exists, skipping...")
        else:
            test_type = TestType(panel_id=panel.id, **test_data)
            db.add(test_type)
            db.flush()
            test_types[test_data["key"]] = test_type
            print(f"  Created test: {test_data['display_name']}")
    
    db.commit()
    return test_types


def seed_test_aliases(db: Session, test_types: dict):
    """Create common test name variations as aliases"""
    aliases_data = [
        # CBC aliases
        ("WBC", ["wbc", "white blood cell", "white blood cells", "leukocytes", "leukocyte count"]),
        ("RBC", ["rbc", "red blood cell", "red blood cells", "erythrocytes", "erythrocyte count"]),
        ("HGB", ["hgb", "hemoglobin", "hb", "haemoglobin"]),
        ("HCT", ["hct", "hematocrit", "haematocrit", "hct%"]),
        ("PLT", ["plt", "platelet", "platelets", "platelet count", "thrombocytes"]),
        ("MCV", ["mcv", "mean corpuscular volume", "mean cell volume"]),
        
        # Metabolic Panel aliases
        ("GLUCOSE", ["glucose", "glu", "blood glucose", "blood sugar", "fasting glucose"]),
        ("BUN", ["bun", "blood urea nitrogen", "urea nitrogen", "urea"]),
        ("CREATININE", ["creatinine", "creat", "cr", "serum creatinine"]),
        ("SODIUM", ["sodium", "na", "na+", "serum sodium"]),
        ("POTASSIUM", ["potassium", "k", "k+", "serum potassium"]),
        ("CHLORIDE", ["chloride", "cl", "cl-", "serum chloride"]),
        ("CO2", ["co2", "carbon dioxide", "bicarbonate", "hco3", "total co2"]),
        ("CALCIUM", ["calcium", "ca", "ca++", "serum calcium", "total calcium"]),
        
        # Lipid Panel aliases
        ("TC", ["tc", "total cholesterol", "cholesterol", "chol", "total chol"]),
        ("LDL", ["ldl", "ldl cholesterol", "ldl-c", "low density lipoprotein", "bad cholesterol"]),
        ("HDL", ["hdl", "hdl cholesterol", "hdl-c", "high density lipoprotein", "good cholesterol"]),
        ("TRIG", ["trig", "triglycerides", "triglyceride", "trigs", "tg"]),
    ]
    
    alias_count = 0
    for test_key, aliases in aliases_data:
        if test_key not in test_types:
            print(f"  Warning: Test type {test_key} not found, skipping aliases")
            continue
        
        test_type = test_types[test_key]
        for alias_text in aliases:
            # Check if alias already exists
            existing = db.query(TestAlias).filter(TestAlias.alias == alias_text.lower()).first()
            if existing:
                continue
            
            alias = TestAlias(
                alias=alias_text.lower(),
                test_type_id=test_type.id
            )
            db.add(alias)
            alias_count += 1
    
    db.commit()
    print(f"Created {alias_count} test aliases")


def main():
    """Main seed function"""
    print("Starting database seed...")
    print("=" * 60)
    
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed panels
        print("\n1. Seeding Panels...")
        panels = seed_panels(db)
        
        # Seed test types
        print("\n2. Seeding CBC Tests...")
        cbc_tests = seed_cbc_tests(db, panels["CBC"])
        
        print("\n3. Seeding Metabolic Panel Tests...")
        metabolic_tests = seed_metabolic_tests(db, panels["METABOLIC"])
        
        print("\n4. Seeding Lipid Panel Tests...")
        lipid_tests = seed_lipid_tests(db, panels["LIPID"])
        
        # Combine all test types for alias seeding
        all_test_types = {**cbc_tests, **metabolic_tests, **lipid_tests}
        
        # Seed aliases
        print("\n5. Seeding Test Aliases...")
        seed_test_aliases(db, all_test_types)
        
        print("\n" + "=" * 60)
        print("Database seed completed successfully!")
        print(f"  - {len(panels)} panels")
        print(f"  - {len(all_test_types)} test types")
        print(f"  - Test aliases created")
        
    except Exception as e:
        print(f"\nError during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

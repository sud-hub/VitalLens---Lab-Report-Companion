from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    reports = relationship("Report", back_populates="user")


class Panel(Base):
    __tablename__ = "panels"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, nullable=False)  # CBC, METABOLIC, LIPID
    display_name = Column(String, nullable=False)
    
    test_types = relationship("TestType", back_populates="panel")


class TestType(Base):
    __tablename__ = "test_types"
    
    id = Column(Integer, primary_key=True, index=True)
    panel_id = Column(Integer, ForeignKey("panels.id"), nullable=False)
    key = Column(String, unique=True, nullable=False)  # WBC, GLUCOSE, LDL, etc.
    display_name = Column(String, nullable=False)
    unit = Column(String, nullable=False)
    ref_low = Column(Float, nullable=True)
    ref_high = Column(Float, nullable=True)
    
    panel = relationship("Panel", back_populates="test_types")
    aliases = relationship("TestAlias", back_populates="test_type")
    test_results = relationship("TestResult", back_populates="test_type")


class TestAlias(Base):
    __tablename__ = "test_aliases"
    
    id = Column(Integer, primary_key=True, index=True)
    alias = Column(String, unique=True, nullable=False)  # Variations like "WBC", "White Blood Cells"
    test_type_id = Column(Integer, ForeignKey("test_types.id"), nullable=False)
    
    test_type = relationship("TestType", back_populates="aliases")


class Report(Base):
    __tablename__ = "reports"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    original_filename = Column(String, nullable=False)
    raw_ocr_text = Column(Text, nullable=True)
    parsed_success = Column(Boolean, default=False)
    notes = Column(String, nullable=True)
    
    user = relationship("User", back_populates="reports")
    test_results = relationship("TestResult", back_populates="report")


class TestResult(Base):
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=False)
    test_type_id = Column(Integer, ForeignKey("test_types.id"), nullable=False)
    value = Column(Float, nullable=False)
    unit = Column(String, nullable=False)
    status = Column(String, nullable=False)  # LOW, NORMAL, HIGH, etc.
    confidence = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    report = relationship("Report", back_populates="test_results")
    test_type = relationship("TestType", back_populates="test_results")

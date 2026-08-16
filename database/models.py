from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.engine import Base

class Website(Base):
    __tablename__ = "websites"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    base_url = Column(String, nullable=False)
    pages = relationship("Page", back_populates="website")

class Page(Base):
    __tablename__ = "pages"
    id = Column(Integer, primary_key=True, index=True)
    website_id = Column(Integer, ForeignKey("websites.id"))
    name = Column(String, nullable=False)
    url_path = Column(String, nullable=False)
    
    website = relationship("Website", back_populates="pages")
    elements = relationship("Element", back_populates="page")
    test_cases = relationship("TestCase", back_populates="page")

class Element(Base):
    __tablename__ = "elements"
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"))
    name = Column(String, nullable=False)
    locator_type = Column(String, nullable=False) # XPATH, ID, CSS, NAME
    locator_value = Column(String, nullable=False)
    
    page = relationship("Page", back_populates="elements")

class TestCase(Base):
    __tablename__ = "test_cases"
    id = Column(Integer, primary_key=True, index=True)
    page_id = Column(Integer, ForeignKey("pages.id"))
    name = Column(String, nullable=False)
    description = Column(Text)
    
    page = relationship("Page", back_populates="test_cases")
    steps = relationship("TestStep", back_populates="test_case")
    results = relationship("Result", back_populates="test_case")

class TestStep(Base):
    __tablename__ = "test_steps"
    id = Column(Integer, primary_key=True, index=True)
    testcase_id = Column(Integer, ForeignKey("test_cases.id"))
    step_order = Column(Integer, nullable=False)
    action = Column(Text, nullable=False)
    expected_result = Column(Text, nullable=False)
    
    test_case = relationship("TestCase", back_populates="steps")

class Suite(Base):
    __tablename__ = "suites"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    runs = relationship("Run", back_populates="suite")

class Run(Base):
    __tablename__ = "runs"
    id = Column(Integer, primary_key=True, index=True)
    suite_id = Column(Integer, ForeignKey("suites.id"))
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, nullable=True)
    status = Column(String, default="Running") # Running, Completed, Failed
    
    suite = relationship("Suite", back_populates="runs")
    results = relationship("Result", back_populates="run")

class Result(Base):
    __tablename__ = "results"
    id = Column(Integer, primary_key=True, index=True)
    run_id = Column(Integer, ForeignKey("runs.id"))
    testcase_id = Column(Integer, ForeignKey("test_cases.id"))
    status = Column(String, nullable=False) # Pass, Fail, Skip
    log = Column(Text, nullable=True)
    screenshot_path = Column(String, nullable=True)
    
    run = relationship("Run", back_populates="results")
    test_case = relationship("TestCase", back_populates="results")
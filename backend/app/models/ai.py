from sqlalchemy import Column, String, Text, Integer, Float, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
import enum
from app.db.base import Base, TimestampMixin

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    REVIEWING = "reviewing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class PromptTemplate(Base, TimestampMixin):
    __tablename__ = "prompt_templates"
    name = Column(String(100), nullable=False, index=True)
    content = Column(Text, nullable=False)
    version = Column(Integer, nullable=False, default=1)
    
    sessions = relationship("GenerationSession", back_populates="prompt_template")

class GenerationJob(Base, TimestampMixin):
    __tablename__ = "generation_jobs"
    project_id = Column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    status = Column(SQLEnum(JobStatus), default=JobStatus.PENDING, nullable=False)
    error_message = Column(Text, nullable=True)
    
    project = relationship("Project", back_populates="generation_jobs")
    presentation = relationship("Presentation", back_populates="job", uselist=False, cascade="all, delete-orphan")
    session = relationship("GenerationSession", back_populates="job", uselist=False, cascade="all, delete-orphan")

class GenerationSession(Base, TimestampMixin):
    __tablename__ = "generation_sessions"
    job_id = Column(ForeignKey("generation_jobs.id", ondelete="CASCADE"), unique=True, nullable=False)
    prompt_template_id = Column(ForeignKey("prompt_templates.id", ondelete="RESTRICT"), nullable=True)
    
    # AI Config Snapshot
    llm_model = Column(String(100), nullable=False)
    embedding_model = Column(String(100), nullable=False)
    temperature = Column(Float, nullable=True)
    top_p = Column(Float, nullable=True)
    max_tokens = Column(Integer, nullable=True)
    retrieval_strategy = Column(String(100), nullable=True)
    chunking_strategy = Column(String(100), nullable=True)
    
    # Overall Telemetry
    total_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    
    job = relationship("GenerationJob", back_populates="session")
    prompt_template = relationship("PromptTemplate", back_populates="sessions", lazy="selectin")
    steps = relationship("GenerationStep", back_populates="session", cascade="all, delete-orphan")

class GenerationStep(Base, TimestampMixin):
    __tablename__ = "generation_steps"
    session_id = Column(ForeignKey("generation_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    step_name = Column(String(100), nullable=False) # e.g., Planner, Retriever
    status = Column(String(50), nullable=False)
    latency_ms = Column(Integer, default=0)
    token_usage = Column(Integer, default=0)
    step_cost = Column(Float, default=0.0)
    input_summary = Column(Text, nullable=True)
    output_summary = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)
    
    session = relationship("GenerationSession", back_populates="steps")

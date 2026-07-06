from sqlalchemy import Column, String, Text, Integer, ForeignKey, Enum as SQLEnum, DateTime, Float
from sqlalchemy.orm import relationship
import enum
from pgvector.sqlalchemy import Vector
from app.db.base import Base, TimestampMixin

class UserRole(str, enum.Enum):
    USER = "user"
    ADMIN = "admin"

class DocumentStatus(str, enum.Enum):
    UPLOADING = "uploading"
    VALIDATING = "validating"
    STORED = "stored"
    EXTRACTING = "extracting"
    CHUNKING = "chunking"
    READY = "ready"
    FAILED = "failed"

class ProjectStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"

class User(Base, TimestampMixin):
    __tablename__ = "users"
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255), nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)

    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan", lazy="selectin")

class Project(Base, TimestampMixin):
    __tablename__ = "projects"
    user_id = Column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(SQLEnum(ProjectStatus), default=ProjectStatus.ACTIVE, nullable=False)

    # AI Workspace Defaults
    default_language = Column(String(50), nullable=True)
    default_audience = Column(String(100), nullable=True)
    default_style = Column(String(100), nullable=True)
    default_template_id = Column(ForeignKey("presentation_templates.id", ondelete="SET NULL"), nullable=True)
    default_slide_count = Column(Integer, nullable=True)
    default_duration_minutes = Column(Integer, nullable=True)

    owner = relationship("User", back_populates="projects")
    documents = relationship("Document", back_populates="project", cascade="all, delete-orphan", lazy="noload")
    generation_jobs = relationship("GenerationJob", back_populates="project", cascade="all, delete-orphan", lazy="noload")

class Document(Base, TimestampMixin):
    __tablename__ = "documents"
    project_id = Column(ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    checksum = Column(String(64), nullable=True) # SHA-256
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADING, nullable=False)
    
    # Extended Analytics Metadata
    processing_started_at = Column(DateTime(timezone=True), nullable=True)
    processing_completed_at = Column(DateTime(timezone=True), nullable=True)
    processing_duration_ms = Column(Integer, nullable=True)
    total_pages = Column(Integer, default=0)
    total_characters = Column(Integer, default=0)
    total_words = Column(Integer, default=0)
    estimated_tokens = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    average_chunk_size = Column(Float, default=0.0)
    largest_chunk_size = Column(Integer, default=0)
    smallest_chunk_size = Column(Integer, default=0)
    reading_time_minutes = Column(Integer, default=0)
    language = Column(String(50), nullable=True, default="en")
    extraction_method = Column(String(100), nullable=True, default="PyPDF")
    
    # Timeline
    uploaded_at = Column(DateTime(timezone=True), nullable=True)
    validated_at = Column(DateTime(timezone=True), nullable=True)
    stored_at = Column(DateTime(timezone=True), nullable=True)
    extracted_at = Column(DateTime(timezone=True), nullable=True)
    chunked_at = Column(DateTime(timezone=True), nullable=True)
    ready_at = Column(DateTime(timezone=True), nullable=True)
    
    # Failure Metadata
    failed_stage = Column(String(50), nullable=True)
    error_code = Column(String(50), nullable=True)
    error_message = Column(Text, nullable=True)

    project = relationship("Project", back_populates="documents")
    document_chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")

class DocumentChunk(Base, TimestampMixin):
    __tablename__ = "document_chunks"
    document_id = Column(ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    page_number = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=False, default=0)
    
    # Quality Indicators
    is_very_short = Column(Integer, default=0) # 0 False, 1 True
    is_low_text_density = Column(Integer, default=0)
    is_ocr_candidate = Column(Integer, default=0)
    
    # Optional Section Metadata
    heading = Column(String(255), nullable=True)
    section = Column(String(255), nullable=True)
    chapter = Column(String(255), nullable=True)
    
    # Vector store metadata
    embedding_provider = Column(String(100), nullable=True)
    embedding_model = Column(String(100), nullable=True)
    vector_store = Column(String(100), nullable=True)
    vector_dimension = Column(Integer, nullable=True)
    vector_reference = Column(String(255), nullable=True, index=True)
    checksum = Column(String(64), nullable=True)
    embedding = Column(Vector(768), nullable=True)

    document = relationship("Document", back_populates="document_chunks")

class PresentationTemplate(Base, TimestampMixin):
    __tablename__ = "presentation_templates"
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    presentations = relationship("Presentation", back_populates="template")

class Presentation(Base, TimestampMixin):
    __tablename__ = "presentations"
    job_id = Column(ForeignKey("generation_jobs.id", ondelete="CASCADE"), nullable=False, unique=True)
    template_id = Column(ForeignKey("presentation_templates.id", ondelete="RESTRICT"), nullable=False)
    title = Column(String(255), nullable=False)
    file_url = Column(String(1024), nullable=True)
    
    # Job creates presentation. Job manages presentation lifecycle.
    job = relationship("GenerationJob", back_populates="presentation")
    template = relationship("PresentationTemplate", back_populates="presentations", lazy="selectin")
    slides = relationship("Slide", back_populates="presentation", cascade="all, delete-orphan")
    citations = relationship("Citation", back_populates="presentation", cascade="all, delete-orphan")

class Slide(Base, TimestampMixin):
    __tablename__ = "slides"
    presentation_id = Column(ForeignKey("presentations.id", ondelete="CASCADE"), nullable=False, index=True)
    slide_number = Column(Integer, nullable=False)
    content_json = Column(Text, nullable=False) # Store structure as JSON text for MVP
    
    presentation = relationship("Presentation", back_populates="slides")

class Citation(Base, TimestampMixin):
    __tablename__ = "citations"
    presentation_id = Column(ForeignKey("presentations.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_id = Column(ForeignKey("document_chunks.id", ondelete="CASCADE"), nullable=False, index=True)
    slide_number = Column(Integer, nullable=False)
    quote_snippet = Column(Text, nullable=False)

    presentation = relationship("Presentation", back_populates="citations")
    chunk = relationship("DocumentChunk")

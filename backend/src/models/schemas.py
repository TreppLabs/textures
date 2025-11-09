"""
SQLAlchemy models for the Textures project.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Theme(Base):
    """Theme model - represents a collection of related texture generations."""
    __tablename__ = "themes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    base_prompt = Column(Text, nullable=False)
    parent_theme_id = Column(Integer, ForeignKey("themes.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    parent_theme = relationship("Theme", remote_side=[id])
    child_themes = relationship("Theme", back_populates="parent_theme")
    generations = relationship("Generation", back_populates="theme")

class Generation(Base):
    """Generation model - represents a single generation session."""
    __tablename__ = "generations"
    
    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=False)
    session_name = Column(String(255), nullable=True)  # Optional user-provided name
    base_prompt = Column(Text, nullable=False)
    variation_params = Column(Text, nullable=True)  # JSON string of parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    theme = relationship("Theme", back_populates="generations")
    images = relationship("Image", back_populates="generation")

class Image(Base):
    """Image model - represents a single generated image."""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    prompt = Column(Text, nullable=False)
    keywords = Column(Text, nullable=True)  # JSON array of extracted keywords
    rating = Column(Integer, nullable=True)  # 1-5 star rating
    variation_params = Column(Text, nullable=True)  # JSON string of specific variation params
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    generation = relationship("Generation", back_populates="images")

class Keyword(Base):
    """Keyword model - tracks keyword effectiveness across themes."""
    __tablename__ = "keywords"
    
    id = Column(Integer, primary_key=True, index=True)
    keyword = Column(String(100), nullable=False, index=True)
    category = Column(String(50), nullable=True)  # structural, organic, textural, etc.
    total_uses = Column(Integer, default=0)
    total_rating_sum = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    success_rate = Column(Float, default=0.0)  # Percentage of 4+ star ratings
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class PromptHistory(Base):
    """PromptHistory model - tracks prompt evolution over time."""
    __tablename__ = "prompt_history"
    
    id = Column(Integer, primary_key=True, index=True)
    theme_id = Column(Integer, ForeignKey("themes.id"), nullable=False)
    prompt_text = Column(Text, nullable=False)
    keywords_used = Column(Text, nullable=True)  # JSON array
    generation_id = Column(Integer, ForeignKey("generations.id"), nullable=True)
    average_rating = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    theme = relationship("Theme")
    generation = relationship("Generation")

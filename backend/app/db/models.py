import datetime
from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey, Text, Table
from sqlalchemy.orm import relationship
from app.db.session import Base

# --- Junction Tables for Many-to-Many Tag Relationships ---

memory_tags = Table(
    "memory_tags",
    Base.metadata,
    Column("memory_id", String, ForeignKey("memories.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

project_tags = Table(
    "project_tags",
    Base.metadata,
    Column("project_id", String, ForeignKey("projects.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

conversation_tags = Table(
    "conversation_tags",
    Base.metadata,
    Column("conversation_id", String, ForeignKey("conversations.id", ondelete="CASCADE"), primary_key=True),
    Column("tag_id", String, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
)

# --- Core Models ---

class Tag(Base):
    __tablename__ = "tags"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    nickname = Column(String)
    personality_preferences = Column(Text, default="{}") # JSON string for generic dicts
    communication_style = Column(String)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")


class Memory(Base):
    __tablename__ = "memories"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    memory_type = Column(String, nullable=False) # 'preference', 'fact', 'context'
    content = Column(Text, nullable=False)
    importance_score = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    
    # Future vector DB hook
    is_embedded = Column(Boolean, default=False)

    user = relationship("User", back_populates="memories")
    tags = relationship("Tag", secondary=memory_tags)


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    message = Column(Text, nullable=False)
    role = Column(String, nullable=False) # 'user', 'assistant', 'tool'
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    tags = relationship("Tag", secondary=conversation_tags)


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    folder_path = Column(String)
    deadlines = Column(Text, default="[]") # JSON string of ISO dates

    user = relationship("User", back_populates="projects")
    tags = relationship("Tag", secondary=project_tags)


class CustomCommand(Base):
    __tablename__ = "custom_commands"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, unique=True, index=True, nullable=False) # e.g., 'Study Mode'
    actions = Column(Text, nullable=False) # JSON array of tool calls


class ToolPermission(Base):
    __tablename__ = "tool_permissions"

    tool_name = Column(String, primary_key=True, index=True)
    permission_level = Column(Integer, default=1) # 1=Safe, 2=Modify, 3=Dangerous
    confirmation_required = Column(Boolean, default=True)


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id")) # Optional
    action_type = Column(String, nullable=False)
    target = Column(String)
    status = Column(String, nullable=False) # 'success', 'failed', 'denied'
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

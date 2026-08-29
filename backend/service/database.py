from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Text,
    DateTime
)
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime


DATABASE_URL = "sqlite:///./followai.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    conversation_type = Column(
        String(50),
        nullable=False
    )

    filename = Column(
        String(255),
        nullable=False
    )

    transcript = Column(
        Text,
        nullable=False
    )

    # Generated email
    email_subject = Column(
        String(500),
        nullable=True
    )

    email_body = Column(
        Text,
        nullable=True
    )

    # Human approval status
    approval_status = Column(
        String(50),
        default="pending"
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


Base.metadata.create_all(bind=engine)
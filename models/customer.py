from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import uuid

# local imports
from config.dbconfig import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(
        DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC)
    )

    # one customer -> many accounts
    accounts = relationship("Account", back_populates="customer")

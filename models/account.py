from sqlalchemy import Column, String, DECIMAL, ForeignKey, DateTime, Enum
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

# local imports
from config.dbconfig import Base


class AccountStatusEnum(enum.Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class AccountTypeEnum(str, enum.Enum):
    CHECKING = "checking"
    SAVINGS = "savings"


class Account(Base):
    __tablename__ = "accounts"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_number = Column(String(20), unique=True, nullable=False)
    customer_id = Column(CHAR(36), ForeignKey("customers.id"), nullable=False)
    balance = Column(DECIMAL(15, 2), nullable=False, default=0.00)
    account_type = Column(String(20), default="checking")
    status = Column(
        Enum(AccountStatusEnum, values_callable=lambda x: [e.value for e in x]),
        default=AccountStatusEnum.ACTIVE,
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship(
        "AccountTransactions",
        back_populates="account",
        foreign_keys="[AccountTransactions.account_id]",
    )

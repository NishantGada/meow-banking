from sqlalchemy import Column, Enum, String, DECIMAL, ForeignKey, DateTime
from sqlalchemy.dialects.mysql import CHAR
from sqlalchemy.orm import relationship
from datetime import datetime, UTC
import uuid
import enum

# local imports
from config.dbconfig import Base


class TransactionTypeEnum(str, enum.Enum):
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class AccountTransactions(Base):
    __tablename__ = "account_transactions"

    id = Column(CHAR(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    account_id = Column(CHAR(36), ForeignKey("accounts.id"), nullable=False)
    transaction_type = Column(
        Enum(TransactionTypeEnum, values_callable=lambda x: [e.value for e in x]),
        nullable=False,
    )
    amount = Column(DECIMAL(15, 2), nullable=False)
    from_account_id = Column(CHAR(36), ForeignKey("accounts.id"), nullable=True)
    to_account_id = Column(CHAR(36), ForeignKey("accounts.id"), nullable=True)
    description = Column(String(200))
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    account = relationship("Account", foreign_keys=[account_id])

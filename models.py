from sqlalchemy import Column, Integer, String, DateTime, func, Boolean
from sqlalchemy.schema import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID


Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    admin = Column(Boolean)
    psw = Column(String(60), nullable=False)
    mail = Column(String(100))
    adv = relationship("Advertising", back_populates="owner")


class Token(Base):
    __tablename__ = 'tokens'
    id = Column(UUID, primary_key=True, server_default=func.uuid_generate_v4())
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'))
    user = relationship('User', lazy='joined')
    created = Column(DateTime, server_default=func.now())


class Advertising(Base):
    __tablename__ = "advertisings"
    id = Column(Integer, primary_key=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    title = Column(String(100), nullable=False, unique=True)
    description = Column(String(300))
    create_date = Column(DateTime, server_default=func.now())
    owner = relationship('User', back_populates="adv")

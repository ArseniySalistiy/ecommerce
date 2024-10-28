from app.backend.db import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.schema import CreateTable
from sqlalchemy.orm import relationship
from app.models.products import Product
from app.models.user import User
from app.models.review import Review
from app.models.rating import Rating

class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    parent_id = Column(Integer, ForeignKey('categories.id'), nullable=True)
    products = relationship('Product', back_populates='category')

print(CreateTable(Category.__table__))
print(CreateTable(Product.__table__))
print(CreateTable(User.__table__))
print(CreateTable(Rating.__table__))
print(CreateTable(Review.__table__))
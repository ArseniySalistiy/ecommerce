from app.backend.db import Base
from sqlalchemy import Column, ForeignKey, String, Integer, Float, Boolean
from sqlalchemy.orm import relationship

class Product(Base):
    __tablename__ = 'products'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    slug = Column(String, unique=True, index=True)
    description = Column(String)
    price = Column(Integer)
    image_url = Column(String)
    stock = Column(Integer)
    supplier_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    category_id = Column(Integer, ForeignKey('categories.id')) # принимаем id с класса категорий
    rating = Column(Float)
    is_active = Column(Boolean, default=True)
    category = relationship('Category', back_populates='products') # устанавливаем свзяь один ко многим

from app.backend.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, Boolean, ForeignKey

class Rating(Base):
    __tablename__ = 'Ratings'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    grade: Mapped[int] = mapped_column(Integer)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
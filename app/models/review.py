from app.backend.db import Base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Integer, String, Boolean, ForeignKey, func #с помощью func можем использовать любую SQL функцию
from datetime import datetime

class Review(Base):
    __tablename__ = 'Reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'))
    rating_id: Mapped[int] = mapped_column(Integer, ForeignKey('Ratings.id'))
    comment: Mapped[str] = mapped_column(String)
    comment_date: Mapped[datetime] = mapped_column(server_default=func.now()) #server_default - устанавливает значение на уровне бд
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

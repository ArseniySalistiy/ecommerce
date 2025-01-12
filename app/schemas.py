from pydantic import BaseModel, Field

class CreateProduct(BaseModel):
    name: str
    description: str
    price: int
    image_url: str
    stock: int
    category: int

class CreateCategory(BaseModel):
    name: str
    parent_id: int | None

class CreateUser(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str

class CreateReview(BaseModel):
    comment: str

class CreateRating(BaseModel):
    rating: int = Field(ge=0, le=10, description='Your grade should be between 0 and 10')
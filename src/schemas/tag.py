from pydantic import BaseModel


class TagModel(BaseModel):
    id: int
    name: str


class TagResponse(TagModel):
    name: str

    class Config:
        from_attributes = True


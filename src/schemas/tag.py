from pydantic import BaseModel, Field


class TagModel(BaseModel):
    name: str = Field(max_length=25)


class TagResponse(TagModel):
    name: str

    class Config:
        from_attributes = True


""" 
додати в class ImageResponse
    tags: List[TagResponse]
    ---
додати в class ImageModel:
    tags: List[str]
"""
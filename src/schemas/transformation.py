from pydantic import BaseModel, ConfigDict


class CropSchema(BaseModel):
    id: int
    aspect_ratio: float = 1.0
    width: int = 0
    is_rounded: bool = False
    crop: str = "fill"
    angle: int = 0
    effect: str = "cartoonify"


class PhotoTransformResponse(BaseModel):
    id: int = 1
    title: str
    description: str
    file_path_transform: str

    model_config = ConfigDict(from_attributes=True)

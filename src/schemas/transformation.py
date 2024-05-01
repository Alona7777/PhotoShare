from datetime import datetime, date
from typing import Optional

from pydantic import BaseModel, EmailStr, Field, ConfigDict


class CropSchema(BaseModel):
    id: int
    aspect_ratio: float = 1.0
    width: int = 300
    crop: str = "fill"

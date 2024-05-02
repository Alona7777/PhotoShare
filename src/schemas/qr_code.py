from pydantic import BaseModel, ConfigDict


class QRCodeResponse(BaseModel):
    id: int
    file_path: str

    model_config = ConfigDict(from_attributes=True)

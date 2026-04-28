from pydantic import BaseModel, Field
from typing import Literal


class StatusUpdateRequest(BaseModel):
    status: Literal["online", "offline"] = Field(..., description="Status do vendedor: online ou offline")


class StatusUpdateResponse(BaseModel):
    user_id: str
    status: str
    message: str


class LocationRequest(BaseModel):
    latitude: float = Field(..., description="Latitude da localização do vendedor")
    longitude: float = Field(..., description="Longitude da localização do vendedor")
    accuracy: float = Field(..., description="Precisão da localização em metros")


class LocationResponse(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    accuracy: float
    message: str

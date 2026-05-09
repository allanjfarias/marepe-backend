from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime
from typing import Optional


class StatusUpdateRequest(BaseModel):
    status: Literal["online", "offline", "paused"] = Field(
        ..., description="Status do vendedor: online ou offline")


class StatusUpdateResponse(BaseModel):
    user_id: str
    status: str
    last_seen_at: str
    message: str


class LocationRequest(BaseModel):
    latitude: float = Field(...,
                            description="Latitude da localização do vendedor")
    longitude: float = Field(...,
                             description="Longitude da localização do vendedor")
    accuracy: float = Field(...,
                            description="Precisão da localização em metros")


class LocationResponse(BaseModel):
    user_id: str
    latitude: float
    longitude: float
    accuracy: float
    message: str


class NearbyVendorSchema(BaseModel):
    vendor_id: str
    status: str
    latitude: float
    longitude: float
    last_seen_at: Optional[datetime]
    created_at: Optional[datetime]
from uuid import UUID
from pydantic import BaseModel, Field
from typing import List, Literal
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
    categorias: list[str] = []
    nome: Optional[str] = None


class CategoriaVitrineDTO(BaseModel):
    id: UUID
    nome_categoria: str
    is_active: bool


class VitrineResponse(BaseModel):
    categorias: List[CategoriaVitrineDTO]


class ToggleCategoriaRequest(BaseModel):
    id_categoria: UUID
    is_active: bool


class CatalogoResponse(BaseModel):
    id: UUID
    nome_categoria: str
    is_active: bool
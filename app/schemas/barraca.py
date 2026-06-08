from typing import List, Literal, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class EstablishmentDetailsResponse(BaseModel):
    vendor_id: str
    establishment_name: str
    owner_name: str
    establishment_photos: List[str] = Field(default_factory=list)
    menu_photos: List[str] = Field(default_factory=list)
    association_status: Literal["none", "this", "other"]



class AssociatedCustomer(BaseModel):
    association_id: str
    nome: str
    horario_associacao: datetime

class AssociatedCustomersResponse(BaseModel):
    customers: List[AssociatedCustomer]

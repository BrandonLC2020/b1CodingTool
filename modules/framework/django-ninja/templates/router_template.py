from ninja import Router
from typing import List
from .schemas import EntityIn, EntityOut
from .models import Entity

router = Router(tags=["entities"])

@router.get("/", response=List[EntityOut])
def list_entities(request):
    return Entity.objects.all()

@router.post("/", response=EntityOut)
def create_entity(request, data: EntityIn):
    entity = Entity.objects.create(**data.dict())
    return entity

@router.get("/{id}", response=EntityOut)
def get_entity(request, id: int):
    entity = Entity.objects.get(id=id)
    return entity

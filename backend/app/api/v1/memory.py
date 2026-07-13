import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.dependencies import get_db, get_current_user_id
from app.db.crud.memories import memory as crud_memory, MemoryCreate

router = APIRouter()

class MemoryResponse(BaseModel):
    id: str
    content: str
    importance_score: int
    
class MemoryRequest(BaseModel):
    memory_type: str = "fact"
    content: str
    importance_score: int = 1

@router.get("/", response_model=List[MemoryResponse])
async def get_memories(
    skip: int = 0, limit: int = 100,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    memories = await crud_memory.get_by_user(db, user_id=user_id, skip=skip, limit=limit)
    return [{"id": m.id, "content": m.content, "importance_score": m.importance_score} for m in memories]

@router.post("/", response_model=MemoryResponse)
async def add_memory(
    request: MemoryRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    new_memory = MemoryCreate(
        id=str(uuid.uuid4()),
        user_id=user_id,
        memory_type=request.memory_type,
        content=request.content,
        importance_score=request.importance_score
    )
    m = await crud_memory.create(db, obj_in=new_memory)
    return MemoryResponse(id=m.id, content=m.content, importance_score=m.importance_score)

@router.delete("/{memory_id}")
async def delete_memory(
    memory_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db)
):
    m = await crud_memory.get(db, id=memory_id)
    if not m or m.user_id != user_id:
        raise HTTPException(status_code=404, detail="Memory not found")
    await crud_memory.remove(db, id=memory_id)
    return {"status": "deleted"}

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import or_
from app.db.crud.base import CRUDBase
from app.db.models import Memory, Tag
from pydantic import BaseModel

class MemoryCreate(BaseModel):
    id: str
    user_id: str
    memory_type: str
    content: str
    importance_score: int = 1
    is_embedded: bool = False

class MemoryUpdate(BaseModel):
    content: Optional[str] = None
    importance_score: Optional[int] = None
    is_embedded: Optional[bool] = None

class CRUDMemory(CRUDBase[Memory, MemoryCreate, MemoryUpdate]):
    async def get_by_user(
        self, db: AsyncSession, *, user_id: str, skip: int = 0, limit: int = 100
    ) -> List[Memory]:
        result = await db.execute(
            select(Memory)
            .filter(Memory.user_id == user_id)
            .order_by(Memory.importance_score.desc(), Memory.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return result.scalars().all()

    async def search(
        self, db: AsyncSession, *, user_id: str, query: str, limit: int = 5
    ) -> List[Memory]:
        """
        Basic keyword search (Pre-FAISS). 
        Will be replaced by Vector DB hook later.
        """
        # SQLite simple LIKE search for MVP
        search_pattern = f"%{query}%"
        result = await db.execute(
            select(Memory)
            .filter(Memory.user_id == user_id)
            .filter(
                or_(
                    Memory.content.ilike(search_pattern),
                    Memory.tags.any(Tag.name.ilike(search_pattern))
                )
            )
            .order_by(Memory.importance_score.desc())
            .limit(limit)
        )
        return result.scalars().all()

memory = CRUDMemory(Memory)

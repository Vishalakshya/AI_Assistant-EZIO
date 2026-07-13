from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.crud.memories import memory as crud_memory
from app.db.session import AsyncSessionLocal

class MemoryContextBuilder:
    """
    Retrieves User, Project, and Conversation context BEFORE LLM execution.
    """
    
    async def build_context(self, user_id: str, current_message: str) -> str:
        """
        Gathers relevant memory and constructs a system prompt injection.
        """
        async with AsyncSessionLocal() as db:
            # 1. Fetch recent relevant memories (semantic/keyword search)
            relevant_memories = await crud_memory.search(db, user_id=user_id, query=current_message, limit=5)
            
            # 2. Fetch User Preferences (In real app, from user table)
            # 3. Fetch active Projects
            
        context_lines = []
        if relevant_memories:
            context_lines.append("--- RELEVANT MEMORY ---")
            for m in relevant_memories:
                context_lines.append(f"- {m.content}")
                
        # Fallback empty context
        if not context_lines:
            return "No specific memory context found for this request."
            
        return "\n".join(context_lines)

memory_builder = MemoryContextBuilder()

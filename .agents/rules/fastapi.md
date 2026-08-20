# FastAPI & Python Best Practices

When working inside the `backend/` directory, adhere to the following rules:

1. **Environment**: We use `uv` for dependency management.
2. **Asynchronous Code**: Always use asynchronous endpoints (`async def`) and async database drivers (e.g., `asyncpg`) to maximize throughput.
3. **Pydantic v2**: Use strictly typed Pydantic models for all API request and response schemas. Ensure validation is robust.
4. **Separation of Concerns**: 
   - Keep routing (`api/`) as thin as possible. 
   - Push business logic down into the `services/` layer.
5. **Database**: Use SQLAlchemy (or SQLModel) with Alembic for all database operations and migrations.
6. **LLM Integration**: 
   - Never embed provider-specific SDKs (like OpenAI's client) directly into business logic.
   - Always route LLM requests through the `AI Gateway` (as defined in `ARCHITECTURE.md`) to ensure models can be swapped out easily.
   - Use `instructor` to enforce JSON structure from the LLMs.

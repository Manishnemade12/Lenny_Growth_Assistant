"""FastAPI Artifact API routes for generating and retrieving artifacts."""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.db.repositories.artifact_repo import ArtifactRepository
from app.schemas.artifact import ArtifactCreate, ArtifactResponse

router = APIRouter()


@router.post("/artifacts", response_model=ArtifactResponse, status_code=status.HTTP_201_CREATED)
async def create_artifact(
    payload: ArtifactCreate,
    db: AsyncSession = Depends(get_db),
):
    """Generate and store an artifact."""
    repo = ArtifactRepository(db)
    # Simple placeholder generator for prompt request
    title = payload.prompt[:30].title() or "Generated Artifact"
    content = payload.prompt

    artifact = await repo.create(
        session_id=payload.session_id,
        artifact_type=payload.type,
        title=title,
        content=content,
    )
    return ArtifactResponse(
        id=artifact.id,
        type=artifact.type,
        title=artifact.title,
        content=artifact.content,
        created_at=artifact.created_at,
    )


@router.get("/artifacts/{artifact_id}", response_model=ArtifactResponse)
async def get_artifact(artifact_id: UUID, db: AsyncSession = Depends(get_db)):
    """Fetch an artifact by ID."""
    repo = ArtifactRepository(db)
    artifact = await repo.get_by_id(artifact_id)
    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return ArtifactResponse(
        id=artifact.id,
        type=artifact.type,
        title=artifact.title,
        content=artifact.content,
        created_at=artifact.created_at,
    )

from typing import Optional

from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import hashlib
from sqlalchemy.orm import Session

import models
import schemas
from database import Base, engine, get_db, SessionLocal

# ---------------------------------------------------------------------------
# App initialisation
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Status Check API",
    description="Task-tracker MVP built on FastAPI + SQLite. Tasks are called 'commitments'.",
    version="1.0.0",
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_password_hash(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def get_current_user(token: str = Depends(oauth2_scheme)):
    if token != "mvp_secret_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return "admin"

@app.on_event("startup")
def startup_event():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        user = db.query(models.User).filter(models.User.username == "admin").first()
        if not user:
            new_user = models.User(username="admin", hashed_password=get_password_hash("password123"))
            db.add(new_user)
            db.commit()
    finally:
        db.close()

# ---------------------------------------------------------------------------
# CORS — allow all origins so the frontend can communicate freely during MVP
# ---------------------------------------------------------------------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", include_in_schema=False)
def serve_frontend():
    return FileResponse("static/index.html")

@app.post("/token", response_model=schemas.Token)
def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user or user.hashed_password != get_password_hash(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": "mvp_secret_token", "token_type": "bearer"}


@app.post(
    "/commitments/",
    response_model=schemas.CommitmentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new commitment",
)
def create_commitment(
    commitment: schemas.CommitmentCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> models.Commitment:
    """Create a new commitment and persist it to the database."""
    db_commitment = models.Commitment(**commitment.model_dump())
    db.add(db_commitment)
    db.commit()
    db.refresh(db_commitment)
    return db_commitment


@app.get(
    "/commitments/",
    response_model=list[schemas.CommitmentRead],
    summary="Get all commitments",
)
def read_commitments(
    project: Optional[str] = Query(default=None, description="Filter by project name"),
    reviewer: Optional[str] = Query(default=None, description="Filter by reviewer name"),
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=500, description="Max records to return"),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> list[models.Commitment]:
    """
    Retrieve all commitments.

    - Optionally filter by **project** and/or **reviewer**.
    - Supports pagination via **skip** and **limit**.
    """
    query = db.query(models.Commitment)
    if project is not None:
        query = query.filter(models.Commitment.project == project)
    if reviewer is not None:
        query = query.filter(models.Commitment.reviewer == reviewer)
    return query.offset(skip).limit(limit).all()


@app.put(
    "/commitments/{commitment_id}",
    response_model=schemas.CommitmentRead,
    summary="Update an existing commitment",
)
def update_commitment(
    commitment_id: int,
    commitment_update: schemas.CommitmentUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> models.Commitment:
    """
    Partially update a commitment by its **id**.

    Only the fields provided in the request body will be updated (PATCH-style behaviour).
    """
    db_commitment = db.get(models.Commitment, commitment_id)
    if db_commitment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commitment with id={commitment_id} not found.",
        )

    update_data = commitment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_commitment, field, value)

    db.commit()
    db.refresh(db_commitment)
    return db_commitment


@app.delete(
    "/commitments/{commitment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a commitment",
)
def delete_commitment(
    commitment_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user),
) -> None:
    """Permanently delete a commitment by its **id**."""
    db_commitment = db.get(models.Commitment, commitment_id)
    if db_commitment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Commitment with id={commitment_id} not found.",
        )

    db.delete(db_commitment)
    db.commit()

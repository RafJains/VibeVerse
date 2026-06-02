from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import CurrentUserRead, LoginRequest, Token, UserCreate, UserRead
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def signup(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    return auth_service.create_user(db=db, payload=payload)


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> Token:
    user = auth_service.authenticate_user(
        db=db,
        email_or_username=payload.email_or_username,
        password=payload.password,
    )
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return Token(access_token=create_access_token(subject=str(user.id)))


@router.get("/me", response_model=CurrentUserRead)
def read_current_user(current_user: User = Depends(auth_service.get_current_user)) -> User:
    return current_user


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Logout successful. Token invalidation will be added later."}

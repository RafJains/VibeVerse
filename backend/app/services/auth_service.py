from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.core.security import decode_access_token, hash_password, verify_password
from app.db.session import get_db
from app.models.user import Profile, User
from app.schemas.auth import TokenPayload, UserCreate


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).one_or_none()


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).one_or_none()


def create_user(db: Session, payload: UserCreate) -> User:
    if get_user_by_email(db, payload.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )
    if get_user_by_username(db, payload.username) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username is already registered",
        )

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        role="normal_user",
        is_active=True,
    )
    db.add(user)
    db.flush()

    db.add(Profile(user_id=user.id, display_name=user.username))
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email_or_username: str, password: str) -> User | None:
    user = (
        db.query(User)
        .filter(or_(User.email == email_or_username, User.username == email_or_username))
        .one_or_none()
    )
    if user is None or not user.is_active:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = TokenPayload(**decode_access_token(token))
    except ValueError as exc:
        raise credentials_error from exc

    if payload.sub is None:
        raise credentials_error

    try:
        user_id = int(payload.sub)
    except ValueError as exc:
        raise credentials_error from exc

    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise credentials_error
    return user

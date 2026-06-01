from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models after Base is defined so Alembic can detect metadata.
import app.models.entity  # noqa: E402,F401
import app.models.user  # noqa: E402,F401

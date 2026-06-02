from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


# Import models after Base is defined so Alembic can detect metadata.
import app.models.collection  # noqa: E402,F401
import app.models.community  # noqa: E402,F401
import app.models.entity  # noqa: E402,F401
import app.models.feed  # noqa: E402,F401
import app.models.post  # noqa: E402,F401
import app.models.review  # noqa: E402,F401
import app.models.user  # noqa: E402,F401

from contextvars import ContextVar

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)

_sessionmaker = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Sesion activa de pruebas. Cuando la suite la define, SessionLocal() devuelve
# un proxy sobre ella: asi los tests que abren su propia sesion participan de la
# transaccion que luego se revierte, en vez de escribir en la base real.
_active_session: ContextVar[Session | None] = ContextVar("active_db_session", default=None)


class _SessionProxy:
    """Delega en la sesion de pruebas compartida.

    ``close()`` y el cierre del contexto ``with`` no hacen nada para no
    Invalidar la sesion que la fixture ``db`` sigue usando.
    """

    __slots__ = ("_session",)

    def __init__(self, session: Session) -> None:
        self._session = session

    def __getattr__(self, name):
        return getattr(self._session, name)

    def __enter__(self) -> Session:
        return self._session

    def __exit__(self, *exc_info) -> bool:
        # No se cierra: la transaccion se revierte en la fixture.
        return False

    def close(self) -> None:
        return None


class _SessionFactory:
    """Fachada de ``SessionLocal`` que respeta la sesion de pruebas activa."""

    def __call__(self, **kwargs) -> Session:
        active = _active_session.get()
        if active is not None:
            return _SessionProxy(active)
        return _sessionmaker(**kwargs)

    def __getattr__(self, name):
        return getattr(_sessionmaker, name)


SessionLocal = _SessionFactory()


def set_active_session(session: Session | None):
    """Activa/desactiva la sesion compartida de pruebas. Devuelve el token."""
    return _active_session.set(session)


def reset_active_session(token) -> None:
    try:
        _active_session.reset(token)
    except ValueError:  # pragma: no cover - token de otro contexto
        _active_session.set(None)


# Engine alternativo para el codigo que hace SQL crudo (pgvector, CU-32) y por
# tanto no pasa por la sesion. La suite lo sustituye por el engine del schema de
# pruebas; si no, se usaria el de produccion y escribiria en los datos reales.
_engine_override = None


def set_engine_override(engine_override) -> None:
    global _engine_override
    _engine_override = engine_override


def get_engine():
    """Engine a usar para SQL crudo: el de pruebas si esta definido."""
    return _engine_override if _engine_override is not None else engine


class Base(DeclarativeBase):
    pass


def get_db():
    active = _active_session.get()
    if active is not None:
        yield active
        return
    db = _sessionmaker()
    try:
        yield db
    finally:
        db.close()

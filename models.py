from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from sqlalchemy import ForeignKey, func, Engine
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from config import logger


class Base(DeclarativeBase):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    @property
    def id_dict(self):
        return {'id': self.id}


class User(Base):
    __tablename__ = 'user'

    email: Mapped[str] = mapped_column(unique=True, nullable=True)
    password: Mapped[str] = mapped_column(nullable=True)


class Announcement(Base):
    __tablename__ = 'announcement'

    title: Mapped[str]
    description: Mapped[str]
    create_at: Mapped[datetime] = mapped_column(server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey('user.id'))

    @property
    def dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'descriptoin': self.description,
            'create_at': self.create_at.isoformat(),
            'user_id': self.user_id
        }


def create_tables(engine: Engine):
    try:
        # Base.metadata.drop_all(engine) # Удалить все таблицы
        Base.metadata.create_all(engine)
        logger.info("Таблицы успешно созданы")
    except SQLAlchemyError as e:
        logger.error(f"Произошла ошибка при создании таблиц: {e}")

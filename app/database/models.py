"""Модуль с моделями, которые будут превращены в таблицы базы данных"""

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey, create_engine, ForeignKey

from config import BaseSettingsDataBase

db_setting = BaseSettingsDataBase()

URL_DATABASE_SQLITE = "sqlite:///" + db_setting.DB_URL

engine = create_engine(URL_DATABASE_SQLITE, echo=db_setting.ECHO_QUERY_SQL)

class Base(DeclarativeBase):
    """Мета класс для всех других моделей базы данных"""
    pass


class Users(Base):
    """Модель таблицы пользователей"""
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    vk_id: Mapped[int] = mapped_column(unique=True, nullable=False)
    in_process: Mapped[bool] = mapped_column(default=False, nullable=False)
    in_process_wiki: Mapped[bool] = mapped_column(default=False, nullable=False)
    in_process_weather: Mapped[bool] = mapped_column(default=False, nullable=False)
    in_process_number: Mapped[bool] = mapped_column(default=False, nullable=False)

    in_process_create_note: Mapped[bool] = mapped_column(default=False, nullable=False)
    in_process_delete_note: Mapped[bool] = mapped_column(default=False, nullable=False)

    is_superuser: Mapped[bool] = mapped_column(default=False, nullable=False)
    in_process_mailing: Mapped[bool] = mapped_column(default=False, nullable=False)

    def __repr__(self) -> str:
        """Опеределение отображения объектов модели"""
        return f"Users(vk_id: {self.vk_id})"
    
class Notes(Base):
    """Модель таблицы заметок"""
    __tablename__ = 'note'

    id:  Mapped[int] = mapped_column(primary_key=True, nullable=False)
    text_note: Mapped[str] = mapped_column()

    f_user_id: Mapped[int] = mapped_column(ForeignKey('user.vk_id', ondelete='CASCADE'), nullable=False)

    def __repr__(self) -> str:
        """Опеределения отображения объектов модели"""
        return f"Notes(id: {self.id}, f_user_id: {self.f_user_id})"
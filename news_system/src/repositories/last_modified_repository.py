from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import LastModified
from news_system.src.handlers.custom_exceptions import IntegrityViolationException


class LastModifiedRepository:
    """Репозиторий для работы с заголовками Last-Modified."""

    @staticmethod
    async def get_header(session: AsyncSession) -> Optional[str]:
        """
        Получает значение заголовка Last-Modified.

        :param session: Асинхронная сессия SQLAlchemy.
        :return: Значение заголовка или None, если запись отсутствует.
        """
        request = await session.execute(select(LastModified))
        response = request.scalars().one_or_none()
        return response.last_modified if response else None

    async def update_header(self, session: AsyncSession, value: str) -> None:
        """
        Обновляет заголовок Last-Modified в базе данных.

        :param session: Асинхронная сессия SQLAlchemy.
        :param value: Новое значение заголовка.
        """
        await session.execute(update(LastModified).values(last_modified=value))
        await self._secure_commit(session)

    @staticmethod
    async def _secure_commit(session: AsyncSession) -> None:
        """
        Безопасно выполняет commit, перехватывая ошибки целостности.

        :param session: Асинхронная сессия SQLAlchemy.
        :raises IntegrityViolationException: Если возникает ошибка целостности данных.
        """
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise IntegrityViolationException(str(exc))

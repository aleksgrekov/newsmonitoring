from typing import Optional

from sqlalchemy import exists, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import LastModified
from news_system.src.handlers.custom_exceptions import IntegrityViolationException
from news_system.src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


class LastModifiedRepository:
    """
    Репозиторий для работы с заголовками Last-Modified.

    Методы:
        - get_header: Получает значение заголовка Last-Modified.
        - update_header: Обновляет или создает запись с заголовком Last-Modified.
        - _secure_commit: Безопасно выполняет commit.
    """

    @staticmethod
    async def get_header(session: AsyncSession) -> Optional[str]:
        """
        Получает значение заголовка Last-Modified.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Returns:
            Optional[str]: Значение заголовка или None, если запись отсутствует.
        """
        request = await session.execute(select(LastModified))
        response = request.scalars().one_or_none()
        return response.last_modified if response else None

    async def update_header(self, session: AsyncSession, value: Optional[str]) -> None:
        """
        Обновляет или создает запись с заголовком Last-Modified.

        Если записи нет, вставляется новая запись с id=1.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            value (Optional[str]): Новое значение заголовка. Если None, обновление не выполняется.
        """
        if value is None:
            logger.info("Заголовок Last-Modified отсутствует, обновление не требуется.")
            return

        if await self._record_exists(session):
            await self._update_record(session, value)
            logger.info("Заголовок Last-Modified обновлен.")
        else:
            await LastModifiedRepository._create_record(session, value)
            logger.info("Заголовок Last-Modified добавлен в базу данных.")

        await LastModifiedRepository._secure_commit(session)

    @staticmethod
    async def _record_exists(session: AsyncSession) -> bool:
        """
        Проверяет, существует ли запись с id=1.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Returns:
            bool: True, если запись существует, иначе False.
        """
        result = await session.execute(select(exists().where(LastModified.id == 1)))
        return result.scalar()

    @staticmethod
    async def _update_record(session: AsyncSession, value: str) -> None:
        """
        Обновляет запись с заголовком Last-Modified.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            value (str): Новое значение заголовка.
        """
        await session.execute(
            update(LastModified).values(last_modified=value).where(LastModified.id == 1)
        )

    @staticmethod
    async def _create_record(session: AsyncSession, value: str) -> None:
        """
        Создает новую запись с заголовком Last-Modified.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            value (str): Значение заголовка.
        """
        new_record = LastModified(id=1, last_modified=value)
        session.add(new_record)

    @staticmethod
    async def _secure_commit(session: AsyncSession) -> None:
        """
        Безопасно выполняет commit, перехватывая ошибки целостности.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Raises:
            IntegrityViolationException: Если возникает ошибка целостности данных.
        """
        try:
            await session.commit()
        except IntegrityError as exc:
            await session.rollback()
            raise IntegrityViolationException(str(exc))

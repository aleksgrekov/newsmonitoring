from typing import Optional

from sqlalchemy import select, update, exists
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database import LastModified
from news_system.src.handlers.custom_exceptions import IntegrityViolationException
from news_system.src.logger.logger_config import configure_logging

logger = configure_logging(__name__)


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

    @staticmethod
    async def update_header(session: AsyncSession, value: Optional[str]) -> None:
        """
        Обновляет заголовок Last-Modified в базе данных.

        Если записи нет, вставляется новая запись с id=1.

        :param session: Асинхронная сессия SQLAlchemy.
        :param value: Новое значение заголовка. Если None, обновление не выполняется.
        """
        if value is not None:
            # Проверяем, существует ли запись
            result = await session.execute(select(exists().where(LastModified.id == 1)))
            record_exists = result.scalar()

            if record_exists:
                # Если запись существует, обновляем
                await session.execute(
                    update(LastModified)
                    .values(last_modified=value)
                    .where(LastModified.id == 1)
                )
                logger.info("Заголовок Last-Modified обновлен.")
            else:
                # Если записи нет, создаём новую с id=1
                new_record = LastModified(id=1, last_modified=value)
                session.add(new_record)
                logger.info("Заголовок Last-Modified добавлен в базу данных.")

            await LastModifiedRepository._secure_commit(session)
        else:
            logger.info("Заголовок Last-Modified отсутствует, обновление не требуется.")

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

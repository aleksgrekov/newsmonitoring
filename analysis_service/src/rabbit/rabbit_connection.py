from aio_pika import connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection
from src.rabbit.interfaces import IConnection


class RabbitConnection(IConnection):
    """
    Реализация для подключения к RabbitMQ и получения канала.
    """

    def __init__(self, url: str):
        self._url = url
        self._connection: AbstractConnection | None = None
        self._channel: AbstractChannel | None = None

    async def connect(self) -> None:
        try:
            self._connection = await connect_robust(self._url)
            self._channel = await self._connection.channel(publisher_confirms=False)
        except Exception as e:
            raise Exception(f"Ошибка при подключении к RabbitMQ: {e}")

    async def disconnect(self) -> None:
        if self._channel and not self._channel.is_closed:
            await self._channel.close()
        if self._connection and not self._connection.is_closed:
            await self._connection.close()

    def get_channel(self) -> AbstractChannel | None:
        return self._channel

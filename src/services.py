import logging
import random
import string

from pydantic.networks import HttpUrl

from src.repositories import BaseRepository
from src.schemes import Links, RequestLink

LOGGER = logging.getLogger(__name__)


class ShortenerService:
    """
    Класс сокращателя
    """

    def __init__(self, domen: str, sql_repository: BaseRepository):
        self.domen = domen
        self.sql_repository = sql_repository

    async def __get_data_by_full_link(self, full_link: HttpUrl):
        """
        Получаем данные из бд по полной ссылке

        Args:
             full_link: Полная ссылка

        Returns:
            Данные из бд, если они есть
        """
        query = "SELECT * FROM links WHERE full_link = ? LIMIT 1"
        result = await self.sql_repository.execute_read_query(query, (str(full_link),))
        if not result:
            return None
        return Links(**result[0])

    async def __get_data_by_short_link(self, short_link: str):
        """
        Получаем данные из бд по короткой ссылке

        Args:
            short_link: Короткая ссылка

        Returns:
            Данные из бд, если они есть
        """
        # инкремент счетчика переходов
        update_query = "UPDATE links SET clicks = clicks + 1 WHERE short_link = :short_link"
        await self.sql_repository.execute_write_query(update_query, {"short_link": short_link})

        select_query = "SELECT * FROM links WHERE short_link = :short_link"
        result = await self.sql_repository.execute_read_query(select_query, {"short_link": short_link})

        if not result:
            return None
        return Links(**result[0])

    async def __generate_short_link(self):
        """
        Генерируем domen + token

        Args:
            domen: домен

        Returns:
            domen + token
        """
        return self.domen + "".join(random.sample(string.ascii_letters + string.digits, 5))

    async def create_link(
        self,
        full_link: RequestLink,
    ):
        """
        Ищем ссылку в бд, если она есть - возвращаем сопоставленную короткую, иначе генерируем короткую.

        Args:
            full_link: полная ссылка

        Returns:
             Данные с короткой и полной ссылками
        """
        last_symbol = str(full_link.link).strip()[-1]
        full_link = str(full_link.link)[:-1] if last_symbol == "/" else full_link.link
        link_from_bd = await self.__get_data_by_full_link(full_link)

        if link_from_bd:
            LOGGER.info(
                f"Возврат ранее сгенерированной ссылки {link_from_bd.short_link}"
                f"для полной ссылки {link_from_bd.full_link}"
            )
            return link_from_bd.dict()

        else:
            short_link = None
            unique_error = True
            query = "INSERT INTO links (full_link, short_link) VALUES (?, ?)"
            error_count = 0
            while unique_error:
                short_link = await self.__generate_short_link()
                unique_error = await self.sql_repository.execute_write_query(query, (str(full_link), short_link))
                error_count += 1
                if unique_error and error_count > 5:
                    return {"status": "Ошибка при работе сервиса"}

            LOGGER.info(f"Вернули новую сгенерированную ссылку {short_link} для полной ссылки {full_link}")
            return {"full_link": full_link, "short_link": short_link}

    async def get_full_link(self, token: str):
        """
        Ищем фуловую ссылку по токену и возвращаем если она есть

        Args:
            token: токен короткой ссылки

        Returns:
            фуловую ссылку, если нашли
        """
        link_from_bd = await self.__get_data_by_short_link(self.domen + token)
        if link_from_bd:
            LOGGER.info(f"Инициирован переход на {link_from_bd.full_link} по короткой ссылке {link_from_bd.short_link}")
            return link_from_bd.full_link
        return None

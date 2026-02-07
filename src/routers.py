from fastapi import APIRouter, Depends, HTTPException, status
from starlette.responses import RedirectResponse

from config import DB_NAME, DOMEN
from src.repositories import AsyncSqliteRepository
from src.schemes import RequestLink
from src.services import ShortenerService

router = APIRouter(prefix="/v1", tags=["Short-link"])


def get_shortener_service() -> ShortenerService:
    """Фабрика для создания ShortenerService."""
    repository = AsyncSqliteRepository(DB_NAME)
    return ShortenerService(domen=DOMEN, sql_repository=repository)


CurrentShortenerService = Depends(get_shortener_service)


@router.post("/shorten/", status_code=status.HTTP_200_OK)
async def create_short_link(full_link: RequestLink, service: ShortenerService = CurrentShortenerService):
    """
    Эндпоинт создания короткой ссылки.

    Args:
        full_link: Полная ссылка, которой и будет сопоставляться короткая
        service: Сервис сокращателя

    Returns:
        Словарь с полной и короткой ссылкой
    """
    return await service.create_link(full_link)


@router.get("/{code}", status_code=status.HTTP_200_OK)
async def try_to_redirect(code: str, service: ShortenerService = CurrentShortenerService):
    """
    Эндпоинт принимает на вход токен, сопоставляет его с доменом и ищет в бд фулловую ссылку,
    если она найдена происходит редерект, иначе возвращаем статус 404

    Args:
        code: Токен короткой ссылки
        service: Сервис сокращателя

    Returns:
        Объект RedirectResponse

    """
    full_link = await service.get_full_link(code)
    if full_link:
        return RedirectResponse(full_link)
    else:
        raise HTTPException(status_code=404)

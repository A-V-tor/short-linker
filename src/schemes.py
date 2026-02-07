from pydantic import BaseModel, HttpUrl


class RequestLink(BaseModel):
    link: HttpUrl


class Links(BaseModel):
    full_link: HttpUrl
    short_link: HttpUrl

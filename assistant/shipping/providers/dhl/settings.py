from pydantic import BaseSettings, HttpUrl


class Settings(BaseSettings):
    testing: bool = True
    server_url: HttpUrl
    site_id = str = 'DServiceVal'
    password = str = 'testServVal'

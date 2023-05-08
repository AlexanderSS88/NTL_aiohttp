import os


TOKEN_TTL = int(os.getenv('TOKEN_TTL', 60 * 60 * 24))
PG_USER = os.getenv('PG_USER', 'application')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'fucking_spilberg')
PG_HOST = os.getenv('PG_HOST', '127.0.0.1')
PG_PORT = os.getenv('PG_PORT', 5431)
PG_DB = os.getenv('PG_DB', 'ntl_aiohttp')
PG_DSN = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'

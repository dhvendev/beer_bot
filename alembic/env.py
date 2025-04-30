from logging.config import fileConfig
from alembic import context
from bot.db_async import Base, User, Chat, CountDrink, CommandHistory, BanUser, GamesHistory, BoxHistory, metadata
from sqlalchemy import create_engine
from core.config import settings

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


target_metadata = Base.metadata
print(target_metadata.tables.keys())

def run_migrations_online() -> None:
    url = f"postgresql+psycopg2://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    print(target_metadata)
    connectable = create_engine(url)

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()

run_migrations_online()

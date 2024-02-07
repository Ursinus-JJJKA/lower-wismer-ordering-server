from dotenv import dotenv_values
from sqlmodel import create_engine, Session

CONFIG = dotenv_values(".env")
DATABASE_URL = f"postgresql://{CONFIG.get('POSTGRES_USER','postgres')}:{CONFIG.get('POSTGRES_PASSWORD','postgres')}@{CONFIG.get('POSTGRES_HOST','postgres_db')}:{CONFIG.get('POSTGRES_PORT','5432')}/{CONFIG.get('POSTGRES_DB','food_db')}"
del CONFIG

engine = create_engine(DATABASE_URL, echo=True)
# Dependency
def get_session():
    with Session(engine) as session:
        yield session
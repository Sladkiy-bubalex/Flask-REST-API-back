from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import create_tables


engine = create_engine(("sqlite:///flask_api_back.db"), echo=True)
Session = sessionmaker(bind=engine)

create_tables(engine)  # Создаем таблицы

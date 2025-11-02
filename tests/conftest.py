import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from dotenv import load_dotenv
import os

# local imports
from config.dbconfig import Base, get_db
from main import app

load_dotenv()


TEST_DB = f"mysql+pymysql://{os.getenv('DB_USER')}:{os.getenv('PASSWORD')}@localhost:3306/{os.getenv('TEST_DATABASE')}"


@pytest.fixture
def client():
    engine = create_engine(TEST_DB)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    db = Session()

    def get_test_db():
        yield db

    app.dependency_overrides[get_db] = get_test_db

    test_client = TestClient(app)
    yield test_client

    db.close()
    Base.metadata.drop_all(engine)

import pytest
# conftest.py
import os
import pytest
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv() 


@pytest.fixture(scope="session")
def mongo_client():
    """Shared MongoDB client for all tests."""
    uri = os.getenv("MONGO_URI")
    assert uri, "MONGO_URI is not set in .env"
    client = MongoClient(uri)
    yield client
    client.close()


@pytest.fixture(scope="session")
def applications(mongo_client):
    db = mongo_client["bitbybitdevelopment"]
    return db["applications"]


@pytest.fixture(scope="session")
def chakra_results(mongo_client):
    db = mongo_client["bitbybitdevelopment"]
    return db["chakraassessments"]  


@pytest.fixture
def search_term():
    return "camacho"
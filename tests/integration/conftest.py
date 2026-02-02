"""
Fixtures for integration tests only. Uses real MongoDB container and real Gemini API.
No mocks for DB or Gemini; unit tests elsewhere use mocks.
"""
import os
import hashlib
import secrets
import urllib.parse
import pytest
from fastapi.testclient import TestClient
from bson import ObjectId

# Lazy imports for app and container so we set env first (see app_client fixture)


def _hash_password(password: str) -> str:
    """Match auth_service password hashing for test user creation."""
    salt = secrets.token_hex(16)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), salt.encode(), 100000
    )
    return f"{salt}${password_hash.hex()}"


# MongoDB test container credentials (required for Mongo 7+ which enables auth)
MONGO_TEST_USER = "test"
MONGO_TEST_PASS = "test"


@pytest.fixture(scope="session")
def mongo_container():
    """Start a real MongoDB container for the test session (ephemeral test DB)."""
    import docker
    from testcontainers.mongodb import MongoDbContainer

    try:
        with MongoDbContainer(
            "mongo:7",
            username=MONGO_TEST_USER,
            password=MONGO_TEST_PASS,
        ) as mongo:
            yield mongo
    except docker.errors.DockerException as e:
        pytest.skip(
            f"Docker unavailable or timed out (required for integration tests): {e}"
        )


@pytest.fixture(scope="session")
def test_mongodb_uri(mongo_container):
    """MongoDB connection URI for the test container (with auth for Mongo 7+)."""
    host = mongo_container.get_container_host_ip()
    port = mongo_container.get_exposed_port(27017)
    user = urllib.parse.quote_plus(MONGO_TEST_USER)
    password = urllib.parse.quote_plus(MONGO_TEST_PASS)
    return f"mongodb://{user}:{password}@{host}:{port}/?authSource=admin"


@pytest.fixture(scope="session")
def test_env(test_mongodb_uri):
    """Set env so app uses the test MongoDB. Must run before app is imported."""
    old_uri = os.environ.get("MONGODB_URI")
    old_db = os.environ.get("MONGODB_DB")
    os.environ["MONGODB_URI"] = test_mongodb_uri
    os.environ["MONGODB_DB"] = "tif_test"
    yield
    if old_uri is not None:
        os.environ["MONGODB_URI"] = old_uri
    else:
        os.environ.pop("MONGODB_URI", None)
    if old_db is not None:
        os.environ["MONGODB_DB"] = old_db
    else:
        os.environ.pop("MONGODB_DB", None)


@pytest.fixture(scope="session")
def app_client(test_env):
    """Test client with real DB (MongoDB container). No mocks for Gemini or DB."""
    from app.main import app

    with TestClient(app) as c:
        yield c


@pytest.fixture
def client(app_client):
    """Per-test alias for app_client."""
    return app_client


@pytest.fixture(scope="session")
def auth_token(test_env, test_mongodb_uri):
    """
    Create a verified test user in the test DB and return a valid JWT.
    Depends on test_env so app.config is never imported with .env's MONGODB_URI
    (which may be a hostname like 'mongodb' that doesn't resolve outside Docker).
    """
    import jwt
    from datetime import datetime, timedelta, timezone
    from pymongo import MongoClient
    from app.config import settings

    sync_client = MongoClient(test_mongodb_uri)
    db = sync_client["tif_test"]
    users = db["users"]

    test_email = "integration-test@test.com"
    test_username = "integration_test_user"
    test_password = "testpassword123"
    user_id = ObjectId()
    password_hash = _hash_password(test_password)

    users.insert_one({
        "_id": user_id,
        "email": test_email,
        "username": test_username,
        "password_hash": password_hash,
        "is_verified": True,
        "is_active": True,
        "name": "Integration Test User",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    sync_client.close()

    access_payload = {
        "user_id": str(user_id),
        "email": test_email,
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(
        access_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return token


@pytest.fixture
def auth_token_fresh_user(test_env, test_mongodb_uri):
    """
    Create a new verified test user and JWT for each test. Use when tests need
    isolated conversation history (e.g. context-dependent call scenarios).
    """
    import jwt
    from datetime import datetime, timedelta, timezone
    from pymongo import MongoClient
    from app.config import settings

    sync_client = MongoClient(test_mongodb_uri)
    db = sync_client["tif_test"]
    users = db["users"]

    user_id = ObjectId()
    test_email = f"integration-{user_id}@test.com"
    test_username = f"user_{user_id}"
    test_password = "testpassword123"
    password_hash = _hash_password(test_password)

    users.insert_one({
        "_id": user_id,
        "email": test_email,
        "username": test_username,
        "password_hash": password_hash,
        "is_verified": True,
        "is_active": True,
        "name": "Integration Test User",
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
    })
    sync_client.close()

    access_payload = {
        "user_id": str(user_id),
        "email": test_email,
        "type": "access",
        "exp": datetime.now(timezone.utc)
        + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRE_SECONDS),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(
        access_payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )
    return token


def skip_if_no_gemini_key():
    """Skip integration tests that call Gemini if GEMINI_API_KEY is not set."""
    if not os.environ.get("GEMINI_API_KEY"):
        pytest.skip(
            "GEMINI_API_KEY not set; integration tests require real Gemini API"
        )

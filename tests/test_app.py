import importlib
import sys
import os
import pytest
from fastapi.testclient import TestClient


def _load_app():
    # Ensure repo root is in sys.path so 'src.app' imports cleanly
    repo_root = os.getcwd()
    if repo_root not in sys.path:
        sys.path.insert(0, repo_root)
    # Remove cached module so 'activities' is reset
    if 'src.app' in sys.modules:
        del sys.modules['src.app']
    module = importlib.import_module('src.app')
    importlib.reload(module)
    return module


@pytest.fixture
def client():
    app_module = _load_app()
    return TestClient(app_module.app)


def test_get_activities(client):
    resp = client.get('/activities')
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert 'Chess Club' in data


def test_signup_success(client):
    activity = 'Chess Club'
    email = 'newstudent@example.com'
    resp = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert resp.status_code == 200
    resp2 = client.get('/activities')
    assert email in resp2.json()[activity]['participants']


def test_signup_duplicate(client):
    activity = 'Chess Club'
    email = 'michael@mergington.edu'
    resp = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert resp.status_code == 400


def test_signup_not_found(client):
    activity = 'NoSuchActivity'
    email = 'someone@example.com'
    resp = client.post(f"/activities/{activity}/signup", params={'email': email})
    assert resp.status_code == 404

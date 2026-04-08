# tests/integration/test_server.py
import pytest
from fastapi.testclient import TestClient
from b1.server.main import app


# TestClient from fastapi/starlette runs the ASGI app in-process — no real server.
# Path.cwd() is set by cd_project/monkeypatch.chdir before each test.

@pytest.fixture
def client(cd_project):
    with TestClient(app) as c:
        yield c


def test_get_project_returns_name_and_initialized_true(client, cd_project):
    resp = client.get("/api/project")
    assert resp.status_code == 200
    data = resp.json()
    assert data["initialized"] is True
    assert data["name"] == cd_project.name


def test_get_config_returns_config_shape(client):
    resp = client.get("/api/config")
    assert resp.status_code == 200
    data = resp.json()
    assert "upstream_repo" in data
    assert "active_agents" in data


def test_get_modules_returns_empty_list_with_no_modules(client):
    resp = client.get("/api/modules")
    assert resp.status_code == 200
    assert resp.json() == []


def test_get_modules_returns_installed_modules(make_project, monkeypatch):
    project = make_project(modules=["django"])
    monkeypatch.chdir(project)
    with TestClient(app) as client:
        resp = client.get("/api/modules")
    assert resp.status_code == 200
    names = [m["name"] for m in resp.json()]
    assert "django" in names


def test_get_context_returns_compiled_content(client):
    resp = client.get("/api/context")
    assert resp.status_code == 200
    data = resp.json()
    assert "content" in data
    assert isinstance(data["content"], str)


def test_get_context_returns_400_when_not_initialized(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    with TestClient(app) as client:
        resp = client.get("/api/context")
    assert resp.status_code == 400

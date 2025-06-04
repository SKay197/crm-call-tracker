import os
import sys
import tempfile
import json
import sqlite3
import pytest
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import app

@pytest.fixture
def client(monkeypatch):
    fd, path = tempfile.mkstemp()
    os.close(fd)
    monkeypatch.setattr(app, 'DB_NAME', path)
    app.init_db()
    with app.app.test_client() as client:
        yield client
    os.remove(path)

def test_create_and_get_call(client):
    res = client.post('/api/calls', json={'name': 'Alice', 'phone': '123'})
    assert res.status_code == 201
    call_id = res.get_json()['id']

    res = client.get(f'/api/calls/{call_id}')
    assert res.status_code == 200
    data = res.get_json()
    assert data['name'] == 'Alice'
    assert data['phone'] == '123'


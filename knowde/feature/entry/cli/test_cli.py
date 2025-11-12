"""CLI test."""

from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from knowde.api import root_router
from knowde.feature.entry.cli.proc import sync_proc
from knowde.feature.user.routers.repo.client import AuthPost, auth_header


@patch("knowde.config.LocalConfig.load")
def test_sync_cmd(mock_load, tmp_path: Path):
    """Sync command test."""
    client = TestClient(root_router())
    ap = AuthPost(client=client.post)
    d = {"email": "test@test.com", "password": "test"}
    ap.register(**d)
    res = ap.login(**d)
    mock_load.return_value.ANCHOR = tmp_path
    mock_load.return_value.CREDENTIALS = res.json()

    # tmp_pathに適当なファイルとディレクトリを作成
    (tmp_path / "test_dir").mkdir()
    (tmp_path / "test_dir" / "test_file.kn").write_text("""
        # title1
    """)
    sync_proc("**/*.kn", get_client=client.get, post_client=client.post)

    h = auth_header()
    res = client.get("/namespace", headers=h)
    assert res.is_success

    g = res.json()["g"]
    assert len(g["edges"]) > 0

"""Tests for Neo4j schema installation."""

from unittest.mock import AsyncMock

from pytest_mock import MockerFixture

from tanbun.config.schema import ASYNC_LABELS, SYNC_LABELS, install_schema
from tanbun.conftest import mark_async_test


@mark_async_test()
async def test_install_schema_installs_sync_and_async_labels(
    mocker: MockerFixture,
) -> None:
    """Install every explicitly declared label with its matching database API."""
    settings = mocker.patch("tanbun.config.schema.Settings").return_value
    install_sync = mocker.patch("tanbun.config.schema.db.install_labels")
    install_async = mocker.patch(
        "tanbun.config.schema.adb.install_labels",
        new_callable=AsyncMock,
    )
    close_async = mocker.patch(
        "tanbun.config.schema.adb.close_connection",
        new_callable=AsyncMock,
    )

    await install_schema()

    settings.setup_db.assert_called_once_with()
    assert [call.args[0] for call in install_sync.call_args_list] == list(SYNC_LABELS)
    assert [call.args[0] for call in install_async.call_args_list] == list(ASYNC_LABELS)
    settings.terdown_db.assert_called_once_with()
    close_async.assert_awaited_once_with()

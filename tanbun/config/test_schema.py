"""Tests for Neo4j schema installation."""

from unittest.mock import AsyncMock

from pytest_mock import MockerFixture

from tanbun.config.schema import ASYNC_LABELS, install_schema
from tanbun.conftest import mark_async_test


@mark_async_test()
async def test_install_schema_installs_all_labels(
    mocker: MockerFixture,
) -> None:
    """Install every explicitly declared label with its matching database API."""
    settings = mocker.patch("tanbun.config.schema.Settings").return_value
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
    assert [call.args[0] for call in install_async.call_args_list] == list(ASYNC_LABELS)
    close_async.assert_awaited_once_with()

"""test definition domain."""
import pytest
from pydantic import ValidationError

from knowde._feature.term.domain import MAX_CHARS
from knowde.feature.definition.domain import Definition


def test_char_length() -> None:
    """Check validation."""
    with pytest.raises(ValidationError):
        Definition(name="a" * (MAX_CHARS + 1), explain="")

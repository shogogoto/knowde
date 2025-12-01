"""constant."""

from typing import Final

from knowde.feature.parsing.primitive.mark import Marker

BRACE_MARKER: Final = Marker(m_open="{", m_close="}")  # 波括弧

FORMULA_IGNORE_MARK: Final = Marker(m_open=r"\$", m_close=r"\$")

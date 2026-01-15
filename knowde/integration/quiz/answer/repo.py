"""回答関連repo."""

from knowde.shared.types import UUIDy


async def list_answers_by_quiz(quiz_uid: UUIDy):
    """クイズのフィードバックとして回答を取得する.

    正答率や何を選んで誤答してしまったかなど
        それぞれの選択率
    """

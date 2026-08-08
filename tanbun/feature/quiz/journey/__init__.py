"""Quizを利用者の一連の体験として理解するためのシナリオ.

このpackageは、新しいdomainやusecaseをまとめる場所ではない。
StudyPlan、Recommendation、Answer、QuizChain、LearningProgressという
独立した機能を、利用者がどの順序で使い、何を得るのかを記述する。

ここに置くテストは網羅性や内部実装の検証を目的としない。
公開APIだけを使い、tanbunismにおける学習体験の代表例を、
実行可能な仕様として残す。

複数の操作が将来ひとつの業務ルールとして不可分になった場合に限り、
その時点で高レベルなusecaseへ昇格させる。
"""

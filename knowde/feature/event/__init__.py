"""出来事を記述.

観測結果など、帰納の対象となる
* Personもwhenやwhereに依存している
* Eventと同レベルの依存度なので同レベルのフィーチャーにすべし
* よってこのフィーチャーではPersonへ依存させない
"""
from .interface import ev_router  # noqa: F401

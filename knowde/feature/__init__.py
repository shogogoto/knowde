"""ユーザーストーリーを実現するE2E機能.

primitiveやcomplexに依存した発展的な機能.
自身しか使用しないpackageはfeatureの子パッケージとする
    ただし、1機能を実現するために特化したpackageであるため、
    子packageができる場合、構造のおかしさを疑った方がよいかも
E2E機能を意識せずにprimitiveなどの部品群を作り始めたのが
  混乱と行き先の不透明さ、やる気の低下の原因では?
/featureの各ディレクトリ直下のテストはe2eテスト
"""

# ruff: noqa
from .cli import cli

"""Feature colocation の依存境界を守るテスト."""

import ast
from pathlib import Path

KNOWDE_DIR = Path(__file__).parent.parent
PRIMITIVE_DIR = Path(__file__).parent / "primitive"


def _imported_modules(path: Path) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.append(node.module)
    return modules


def test_legacy_package_source_files_are_removed():
    """Integration/shared へ新しい実装を戻さない."""
    for package_name in ("integration", "shared"):
        package = KNOWDE_DIR / package_name
        source_files = list(package.rglob("*.py")) if package.exists() else []
        assert source_files == []


def test_primitive_does_not_depend_on_feature_packages():
    """Primitive を機能層から独立させる。."""
    invalid: list[tuple[Path, str]] = []
    for path in PRIMITIVE_DIR.rglob("*.py"):
        feature_imports = [
            module
            for module in _imported_modules(path)
            if module.startswith("knowde.feature.")
            and not module.startswith("knowde.feature.primitive")
        ]
        invalid.extend(
            (path.relative_to(KNOWDE_DIR), module) for module in feature_imports
        )

    assert invalid == []

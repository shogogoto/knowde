"""Feature colocation の依存境界を守るテスト."""

import ast
from pathlib import Path

KNOWDE_DIR = Path(__file__).parent.parent
FOUNDATION_DIRS = (
    Path(__file__).parent / "domain",
    Path(__file__).parent / "repo",
)


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


def test_foundation_does_not_depend_on_specific_features():
    """直下のdomain/repoを個別のfeatureから独立させる."""
    invalid: list[tuple[Path, str]] = []
    for foundation_dir in FOUNDATION_DIRS:
        for path in foundation_dir.rglob("*.py"):
            feature_imports = [
                module
                for module in _imported_modules(path)
                if module.startswith("knowde.feature.")
                and not module.startswith(
                    ("knowde.feature.domain", "knowde.feature.repo"),
                )
            ]
            invalid.extend(
                (path.relative_to(KNOWDE_DIR), module) for module in feature_imports
            )

    assert invalid == []

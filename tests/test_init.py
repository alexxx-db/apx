"""Tests for the init command."""

from pathlib import Path

from conftest import init_project_async


async def test_init_with_custom_path(tmp_path: Path) -> None:
    """Test that init works correctly when using a subdirectory path.

    Regression test for: components being placed in nested directory
    (e.g., new-apx/new-apx/src instead of new-apx/src)
    """
    # Create a subdirectory path (simulating `apx init new-apx`)
    project_path = tmp_path / "new-apx"
    project_path.mkdir(parents=True, exist_ok=True)

    # Initialize with sidebar layout (triggers component add)
    result = await init_project_async(
        project_path,
        name="test-app",
        template="essential",
        layout="sidebar",
        skip_build=True,
        skip_dependencies=False,
    )

    assert result.returncode == 0, f"Init failed: {result.stderr}"

    # Verify components are in correct location
    ui_components = project_path / "src" / "test_app" / "ui" / "components" / "ui"
    assert ui_components.exists(), f"Components should be at {ui_components}"

    # Verify NO nested structure exists
    nested_path = project_path / "new-apx" / "src"
    assert not nested_path.exists(), f"Nested path should NOT exist: {nested_path}"

    # Verify sidebar.tsx exists (proves sidebar components were added)
    sidebar_file = ui_components / "sidebar.tsx"
    assert sidebar_file.exists(), f"sidebar.tsx should exist at {sidebar_file}"

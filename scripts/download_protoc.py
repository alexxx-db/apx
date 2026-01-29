# /// script
# requires-python = ">=3.11"
# dependencies = ["httpx", "typer"]
# ///

from __future__ import annotations

import io
import platform
import shutil
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path

import httpx
import typer

DEFAULT_PROTOC_VERSION = "28.3"
DEFAULT_OUTPUT_DIR = Path(".protoc")
GITHUB_RELEASES_BASE = "https://github.com/protocolbuffers/protobuf/releases/download"


@dataclass(frozen=True, slots=True)
class PlatformInfo:
    platform: str  # 'linux', 'osx', 'win64'
    arch: str  # 'x86_64', 'aarch_64'

    def get_filename(self, version: str) -> str:
        """Get protoc zip filename for this platform."""
        if self.platform == "win64":
            return f"protoc-{version}-win64.zip"
        return f"protoc-{version}-{self.platform}-{self.arch}.zip"


app = typer.Typer(add_completion=False)


def detect_platform() -> PlatformInfo:
    """Detect current platform and architecture."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    # Normalize platform name
    if system == "darwin":
        platform_name = "osx"
    elif system == "windows":
        platform_name = "win64"
    elif system == "linux":
        platform_name = "linux"
    else:
        typer.echo(f"error: unsupported platform: {system}", err=True)
        raise typer.Exit(code=1)

    # Normalize architecture
    if machine in ("x86_64", "amd64"):
        arch = "x86_64"
    elif machine in ("aarch64", "arm64"):
        arch = "aarch_64"
    else:
        typer.echo(f"error: unsupported architecture: {machine}", err=True)
        raise typer.Exit(code=1)

    return PlatformInfo(platform=platform_name, arch=arch)


def download_and_extract_protoc(
    client: httpx.Client,
    version: str,
    platform_info: PlatformInfo,
    output_dir: Path,
) -> None:
    """Download and extract protoc binary from GitHub releases."""
    filename = platform_info.get_filename(version)
    url = f"{GITHUB_RELEASES_BASE}/v{version}/{filename}"

    typer.echo(f"download: {url}")

    try:
        resp = client.get(url)
        resp.raise_for_status()
    except httpx.HTTPError as exc:
        typer.echo(f"error: failed to download protoc: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    typer.echo(f"downloaded: {len(resp.content) / 1024 / 1024:.1f} MB")

    # Extract zip file
    typer.echo(f"extracting to: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(output_dir)
    except (zipfile.BadZipFile, ValueError) as exc:
        typer.echo(f"error: failed to extract protoc: {exc}", err=True)
        raise typer.Exit(code=1) from exc

    # Make protoc executable on Unix
    protoc_path = output_dir / "bin" / "protoc"
    if protoc_path.exists() and platform.system() != "Windows":
        protoc_path.chmod(0o755)

    typer.echo(f"saved: {protoc_path}")


def install_protoc_macos_brew(output_dir: Path) -> None:
    """Install protoc via Homebrew on macOS and copy to output directory."""
    typer.echo("installing via homebrew")

    try:
        # Install via brew
        subprocess.run(
            ["brew", "install", "protobuf"],
            check=True,
            capture_output=True,
            text=True,
        )

        # Find protoc location
        result = subprocess.run(
            ["which", "protoc"],
            check=True,
            capture_output=True,
            text=True,
        )
        protoc_path = Path(result.stdout.strip())

        # Find brew prefix for protobuf
        result = subprocess.run(
            ["brew", "--prefix", "protobuf"],
            check=True,
            capture_output=True,
            text=True,
        )
        brew_prefix = Path(result.stdout.strip())

        # Create output directory structure
        output_dir.mkdir(parents=True, exist_ok=True)
        (output_dir / "bin").mkdir(exist_ok=True)

        # Copy protoc binary
        shutil.copy2(protoc_path, output_dir / "bin" / "protoc")
        typer.echo(f"copied: {protoc_path} -> {output_dir / 'bin' / 'protoc'}")

        # Copy include files
        include_src = brew_prefix / "include"
        if include_src.exists():
            shutil.copytree(
                include_src,
                output_dir / "include",
                dirs_exist_ok=True,
            )
            typer.echo(f"copied: {include_src} -> {output_dir / 'include'}")

    except subprocess.CalledProcessError as exc:
        typer.echo(f"error: brew install failed: {exc}", err=True)
        if exc.stderr:
            typer.echo(f"stderr: {exc.stderr}", err=True)
        raise typer.Exit(code=1) from exc
    except Exception as exc:
        typer.echo(f"error: failed to copy from brew: {exc}", err=True)
        raise typer.Exit(code=1) from exc


def verify_protoc_installation(output_dir: Path) -> None:
    """Verify that protoc was installed correctly."""
    protoc_exe = "protoc.exe" if platform.system() == "Windows" else "protoc"
    protoc_path = output_dir / "bin" / protoc_exe

    if not protoc_path.exists():
        typer.echo(f"error: protoc not found at {protoc_path}", err=True)
        raise typer.Exit(code=1)

    # Try to run protoc --version
    try:
        result = subprocess.run(
            [str(protoc_path), "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        typer.echo(f"verified: {result.stdout.strip()}")
    except subprocess.CalledProcessError as exc:
        typer.echo(f"error: protoc verification failed: {exc}", err=True)
        raise typer.Exit(code=1) from exc


@app.command()
def main(
    version: str = typer.Option(DEFAULT_PROTOC_VERSION, "--version"),
    output_dir: Path = typer.Option(DEFAULT_OUTPUT_DIR, "--output-dir", "-o"),
    use_brew: bool = typer.Option(False, "--use-brew", help="Use Homebrew on macOS"),
) -> None:
    """
    Download and install protoc for the current platform.

    Protoc is installed to:
      - {output-dir}/bin/protoc
      - {output-dir}/include/
    """
    output_dir = output_dir.expanduser().resolve()

    # Check if already installed
    protoc_exe = "protoc.exe" if platform.system() == "Windows" else "protoc"
    protoc_path = output_dir / "bin" / protoc_exe

    if protoc_path.exists():
        typer.echo(f"skip: protoc already exists at {protoc_path}")
        verify_protoc_installation(output_dir)
        return

    # Determine installation method
    if use_brew and platform.system() == "Darwin":
        install_protoc_macos_brew(output_dir)
    else:
        platform_info = detect_platform()
        typer.echo(f"detected platform: {platform_info.platform}-{platform_info.arch}")

        timeout = httpx.Timeout(connect=10.0, read=60.0, write=60.0, pool=10.0)
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            download_and_extract_protoc(client, version, platform_info, output_dir)

    # Verify installation
    verify_protoc_installation(output_dir)


if __name__ == "__main__":
    app()

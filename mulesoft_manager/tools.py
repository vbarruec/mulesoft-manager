"""
tools.py
Instalación y verificación de herramientas: Java, Maven, VS Code.
"""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
import sys
import zipfile
import tarfile
import urllib.request
from pathlib import Path
from typing import Optional, Tuple

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, DownloadColumn
from rich.table import Table

from .config import GlobalConfig
from .constants import DEFAULT_JAVA_VERSION, DEFAULT_MAVEN_VERSION, VSCODE_EXTENSIONS

console = Console()

# ---------------------------------------------------------------------------
# URLs de descarga manual
# ---------------------------------------------------------------------------

JAVA_ADOPTIUM_URL = (
    "https://api.adoptium.net/v3/binary/latest/{version}/ga/windows/x64/jdk/hotspot/normal/adoptium"
)

MAVEN_DOWNLOAD_URL = (
    "https://dlcdn.apache.org/maven/maven-3/{version}/binaries/apache-maven-{version}-bin.zip"
)


# ---------------------------------------------------------------------------
# Verificación de herramientas
# ---------------------------------------------------------------------------

def check_java(java_home: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Verifica si Java está instalado y devuelve (ok, version_string).
    """
    java_cmd = None
    if java_home:
        java_cmd = str(java_home / "bin" / "java.exe")

    if java_cmd is None or not Path(java_cmd).exists():
        java_cmd = shutil.which("java")

    if java_cmd is None:
        return False, "No encontrado"

    try:
        result = subprocess.run(
            [java_cmd, "-version"],
            capture_output=True, text=True, timeout=10
        )
        # Java imprime la versión en stderr
        output = result.stderr or result.stdout
        version_line = output.splitlines()[0] if output else ""
        return True, version_line.strip()
    except Exception as e:
        return False, str(e)


def check_maven(maven_home: Optional[Path] = None) -> Tuple[bool, str]:
    """
    Verifica si Maven está instalado y devuelve (ok, version_string).
    """
    mvn_cmd = None
    if maven_home:
        mvn_cmd = str(maven_home / "bin" / "mvn.cmd")

    if mvn_cmd is None or not Path(str(mvn_cmd)).exists():
        mvn_cmd = shutil.which("mvn") or shutil.which("mvn.cmd")

    if mvn_cmd is None:
        return False, "No encontrado"

    try:
        result = subprocess.run(
            [mvn_cmd, "--version"],
            capture_output=True, text=True, timeout=15
        )
        output = result.stdout or result.stderr
        version_line = output.splitlines()[0] if output else ""
        return True, version_line.strip()
    except Exception as e:
        return False, str(e)


def check_vscode() -> Tuple[bool, str]:
    """Verifica si VS Code está instalado."""
    code_cmd = shutil.which("code")
    if code_cmd is None:
        # Comprobar rutas habituales en Windows
        possible = [
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "bin" / "code.cmd",
            Path("C:/Program Files/Microsoft VS Code/bin/code.cmd"),
        ]
        for p in possible:
            if p.exists():
                code_cmd = str(p)
                break

    if code_cmd is None:
        return False, "No encontrado"

    try:
        result = subprocess.run(
            [code_cmd, "--version"],
            capture_output=True, text=True, timeout=10
        )
        version = result.stdout.splitlines()[0] if result.stdout else "versión desconocida"
        return True, version.strip()
    except Exception as e:
        return False, str(e)


def check_git() -> Tuple[bool, str]:
    """Verifica si Git está instalado."""
    git_cmd = shutil.which("git")
    if git_cmd is None:
        return False, "No encontrado"
    try:
        result = subprocess.run(
            [git_cmd, "--version"],
            capture_output=True, text=True, timeout=10
        )
        return True, result.stdout.strip()
    except Exception as e:
        return False, str(e)


def check_ssh_keygen() -> Tuple[bool, str]:
    """Verifica si ssh-keygen está disponible."""
    cmd = shutil.which("ssh-keygen")
    if cmd is None:
        return False, "No encontrado (instalar Git para Windows incluye ssh-keygen)"
    try:
        result = subprocess.run([cmd, "--help"], capture_output=True, text=True, timeout=5)
        return True, "Disponible"
    except Exception:
        return True, "Disponible"


def print_tools_status(cfg: GlobalConfig) -> None:
    """Muestra una tabla con el estado de todas las herramientas."""
    table = Table(title="Estado de herramientas", show_header=True, header_style="bold cyan")
    table.add_column("Herramienta", style="bold")
    table.add_column("Estado")
    table.add_column("Versión / Detalle")

    checks = [
        ("Java", check_java(cfg.java_home)),
        ("Maven", check_maven(cfg.maven_home)),
        ("VS Code", check_vscode()),
        ("Git", check_git()),
        ("ssh-keygen", check_ssh_keygen()),
    ]

    for name, (ok, detail) in checks:
        status = "[green]✅ Instalado[/green]" if ok else "[red]❌ No encontrado[/red]"
        table.add_row(name, status, detail)

    console.print(table)


# ---------------------------------------------------------------------------
# Instalación via winget (Windows)
# ---------------------------------------------------------------------------

def winget_available() -> bool:
    """Comprueba si winget está disponible."""
    return shutil.which("winget") is not None


def install_via_winget(package_id: str, display_name: str) -> bool:
    """
    Instala un paquete via winget.
    Devuelve True si tuvo éxito.
    """
    if not winget_available():
        console.print("[red]winget no disponible. Instala manualmente.[/red]")
        return False

    console.print(f"[cyan]Instalando {display_name} via winget...[/cyan]")
    try:
        result = subprocess.run(
            ["winget", "install", "--id", package_id,
             "--accept-source-agreements", "--accept-package-agreements",
             "--silent"],
            timeout=300
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        console.print("[red]Tiempo de espera agotado.[/red]")
        return False
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return False


def install_java(cfg: GlobalConfig, tools_dir: Path) -> Optional[Path]:
    """
    Instala Java JDK.
    Primero intenta winget; si no, descarga Adoptium.
    Devuelve la ruta al JAVA_HOME instalado, o None si falla.
    """
    version = cfg.get("java", "version", default=DEFAULT_JAVA_VERSION)
    method = cfg.get("java", "install_method", default="winget")

    console.print(f"\n[bold]Instalando Java JDK {version}...[/bold]")

    if method == "winget" and winget_available():
        # Eclipse Temurin (Adoptium) en winget
        winget_id = f"EclipseAdoptium.Temurin.{version}.JDK"
        ok = install_via_winget(winget_id, f"Java {version} (Temurin)")
        if ok:
            # Buscar JAVA_HOME automáticamente
            java_home = _find_java_home(version)
            if java_home:
                cfg.set(str(java_home), "java", "home")
                cfg.save()
                console.print(f"[green]Java instalado en: {java_home}[/green]")
                return java_home
        console.print("[yellow]No se pudo detectar JAVA_HOME automáticamente después de winget.[/yellow]")
        console.print("[yellow]Configura manualmente java.home en config.yaml[/yellow]")
        return None
    else:
        # Descarga manual de Adoptium
        return _install_java_manual(version, tools_dir)


def _find_java_home(version: str) -> Optional[Path]:
    """Busca el JAVA_HOME de la versión instalada."""
    # JAVA_HOME del sistema
    env_java = os.environ.get("JAVA_HOME")
    if env_java and Path(env_java).exists():
        return Path(env_java)

    # Rutas habituales en Windows con Temurin
    candidates = [
        Path(f"C:/Program Files/Eclipse Adoptium/jdk-{version}"),
        Path(f"C:/Program Files/Java/jdk-{version}"),
        Path(f"C:/Program Files/Microsoft/jdk-{version}"),
    ]
    for c in candidates:
        if c.exists():
            return c

    # Buscar con glob
    adoptium_base = Path("C:/Program Files/Eclipse Adoptium")
    if adoptium_base.exists():
        matches = list(adoptium_base.glob(f"jdk-{version}*"))
        if matches:
            return matches[0]

    return None


def _install_java_manual(version: str, tools_dir: Path) -> Optional[Path]:
    """Descarga e instala Java manualmente en tools/java/."""
    java_dir = tools_dir / "java"
    java_dir.mkdir(parents=True, exist_ok=True)

    url = JAVA_ADOPTIUM_URL.format(version=version)
    dest = java_dir / f"jdk-{version}-windows-x64.zip"

    console.print(f"[cyan]Descargando Java {version} desde Adoptium...[/cyan]")
    console.print(f"[dim]URL: {url}[/dim]")

    try:
        _download_file(url, dest)
        console.print("[cyan]Extrayendo...[/cyan]")
        extract_dir = java_dir / f"jdk-{version}"
        with zipfile.ZipFile(dest, "r") as zf:
            zf.extractall(java_dir)
        # El ZIP de Adoptium crea una carpeta como jdk-17.0.x+y
        extracted = sorted(java_dir.glob(f"jdk-{version}*"))
        if extracted:
            java_home = extracted[0]
            dest.unlink()  # limpiar ZIP
            console.print(f"[green]Java instalado en: {java_home}[/green]")
            return java_home
    except Exception as e:
        console.print(f"[red]Error descargando Java: {e}[/red]")
        console.print(f"[yellow]Descarga manualmente desde https://adoptium.net y extrae en: {java_dir}[/yellow]")

    return None


def install_maven(cfg: GlobalConfig, tools_dir: Path) -> Optional[Path]:
    """
    Instala Apache Maven en tools/maven/.
    Devuelve la ruta al MAVEN_HOME.
    """
    version = cfg.get("maven", "version", default=DEFAULT_MAVEN_VERSION)
    console.print(f"\n[bold]Instalando Apache Maven {version}...[/bold]")

    maven_dir = tools_dir / "maven"
    maven_dir.mkdir(parents=True, exist_ok=True)

    target_dir = maven_dir / f"apache-maven-{version}"
    if target_dir.exists():
        console.print(f"[green]Maven ya instalado en: {target_dir}[/green]")
        return target_dir

    url = MAVEN_DOWNLOAD_URL.format(version=version)
    dest = maven_dir / f"apache-maven-{version}-bin.zip"

    console.print(f"[cyan]Descargando Maven {version}...[/cyan]")
    console.print(f"[dim]URL: {url}[/dim]")

    try:
        _download_file(url, dest)
        console.print("[cyan]Extrayendo...[/cyan]")
        with zipfile.ZipFile(dest, "r") as zf:
            zf.extractall(maven_dir)
        dest.unlink()

        if target_dir.exists():
            cfg.set(str(target_dir), "maven", "home")
            cfg.save()
            console.print(f"[green]Maven instalado en: {target_dir}[/green]")
            return target_dir
    except Exception as e:
        console.print(f"[red]Error descargando Maven: {e}[/red]")
        console.print(f"[yellow]Descarga manualmente desde https://maven.apache.org/download.cgi y extrae en: {maven_dir}[/yellow]")

    return None


def install_vscode(cfg: GlobalConfig) -> bool:
    """Instala VS Code via winget o indica URL de descarga."""
    ok, _ = check_vscode()
    if ok:
        console.print("[green]VS Code ya está instalado.[/green]")
        return True

    console.print("\n[bold]Instalando Visual Studio Code...[/bold]")
    method = cfg.get("vscode", "install_method", default="winget")

    if method == "winget" and winget_available():
        return install_via_winget("Microsoft.VisualStudioCode", "Visual Studio Code")
    else:
        console.print("[yellow]Descarga VS Code manualmente desde:[/yellow]")
        console.print("[link=https://code.visualstudio.com/download]https://code.visualstudio.com/download[/link]")
        return False


def install_vscode_extensions(extensions: list[str]) -> None:
    """Instala extensiones de VS Code."""
    code_cmd = _find_vscode_cmd()
    if code_cmd is None:
        console.print("[red]VS Code no encontrado. Instala primero VS Code.[/red]")
        return

    console.print(f"\n[bold]Instalando {len(extensions)} extensiones de VS Code...[/bold]")

    failed = []
    for ext in extensions:
        console.print(f"  [cyan]→ {ext}[/cyan]", end="")
        try:
            result = subprocess.run(
                [code_cmd, "--install-extension", ext, "--force"],
                capture_output=True, text=True, timeout=120
            )
            if result.returncode == 0:
                console.print(" [green]✓[/green]")
            else:
                console.print(" [red]✗[/red]")
                failed.append(ext)
        except Exception as e:
            console.print(f" [red]✗ ({e})[/red]")
            failed.append(ext)

    if failed:
        console.print(f"\n[yellow]Extensiones con error ({len(failed)}):[/yellow]")
        for ext in failed:
            console.print(f"  [red]• {ext}[/red]")
        console.print("[yellow]Instálalas manualmente desde VS Code Extensions.[/yellow]")
    else:
        console.print("\n[green]Todas las extensiones instaladas correctamente.[/green]")


def list_installed_extensions() -> list[str]:
    """Devuelve la lista de extensiones instaladas en VS Code."""
    code_cmd = _find_vscode_cmd()
    if code_cmd is None:
        return []
    try:
        result = subprocess.run(
            [code_cmd, "--list-extensions"],
            capture_output=True, text=True, timeout=30
        )
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def _find_vscode_cmd() -> Optional[str]:
    """Encuentra el ejecutable de VS Code."""
    cmd = shutil.which("code")
    if cmd:
        return cmd
    # Windows: rutas habituales
    candidates = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Microsoft VS Code" / "bin" / "code.cmd",
        Path("C:/Program Files/Microsoft VS Code/bin/code.cmd"),
        Path(os.environ.get("APPDATA", "")) / "../Local/Programs/Microsoft VS Code/bin/code.cmd",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


# ---------------------------------------------------------------------------
# Descarga de archivos con barra de progreso
# ---------------------------------------------------------------------------

def _download_file(url: str, dest: Path) -> None:
    """Descarga un archivo desde URL con barra de progreso."""
    import urllib.request

    def reporthook(block_num, block_size, total_size):
        pass  # Usamos context manager de rich para progreso

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        DownloadColumn(),
        console=console,
    ) as progress:
        task = progress.add_task(f"Descargando {dest.name}", total=None)

        def hook(count, block_size, total_size):
            if total_size > 0:
                progress.update(task, total=total_size, completed=count * block_size)

        urllib.request.urlretrieve(url, dest, reporthook=hook)
        progress.update(task, completed=dest.stat().st_size if dest.exists() else 0)

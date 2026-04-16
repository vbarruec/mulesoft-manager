"""
git_manager.py
Gestión de SSH keys, configuración Git y clonado de repositorios por cliente.
"""

from __future__ import annotations

import os
import platform
import shutil
import stat
import subprocess
import textwrap
from pathlib import Path
from typing import Optional, List

from rich.console import Console

from .config import ClientConfig, GlobalConfig
from .constants import (
    GITCONFIG_TEMPLATE,
    SSH_CONFIG_ENTRY_TEMPLATE,
    SSH_CONFIG_ENTRY_CODECOMMIT_TEMPLATE,
    VCS_TYPES,
    MULE_REGIONS,
)

console = Console()


# ---------------------------------------------------------------------------
# SSH Key Management
# ---------------------------------------------------------------------------

def generate_ssh_key(
    root: Path,
    client: ClientConfig,
    key_type: str = "ed25519",
    bits: int = 4096,
    comment: Optional[str] = None,
    force: bool = False,
) -> Optional[Path]:
    """
    Genera un par de claves SSH para el cliente.
    Guarda la clave privada en <root>/.ssh/<ssh_key_name>.
    Devuelve la ruta a la clave privada, o None si falla.
    """
    ssh_dir = root / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)

    key_path = ssh_dir / client.ssh_key_name
    pub_key_path = Path(str(key_path) + ".pub")

    if key_path.exists() and not force:
        console.print(f"[yellow]La clave SSH ya existe: {key_path}[/yellow]")
        console.print("[yellow]Usa --force para regenerarla.[/yellow]")
        return key_path

    keygen = shutil.which("ssh-keygen")
    if keygen is None:
        console.print("[red]ssh-keygen no encontrado. Instala Git para Windows.[/red]")
        return None

    if comment is None:
        comment = f"{client.name}@{client.vcs_type}"

    cmd = [keygen, "-t", key_type, "-C", comment, "-f", str(key_path), "-N", ""]
    if key_type == "rsa":
        cmd += ["-b", str(bits)]

    console.print(f"[cyan]Generando clave SSH ({key_type}) para {client.display_name}...[/cyan]")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            console.print(f"[red]Error generando clave: {result.stderr}[/red]")
            return None

        # Asegurarse de que la clave privada tiene permisos correctos (600)
        _set_private_key_permissions(key_path)

        console.print(f"[green]Clave SSH generada:[/green]")
        console.print(f"  Privada: [dim]{key_path}[/dim]")
        console.print(f"  Pública: [dim]{pub_key_path}[/dim]")

        # Mostrar la clave pública para que el usuario la registre en su VCS
        _print_public_key(pub_key_path, client)

        return key_path

    except subprocess.TimeoutExpired:
        console.print("[red]Tiempo de espera agotado generando clave SSH.[/red]")
        return None
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        return None


def _set_private_key_permissions(key_path: Path) -> None:
    """Establece permisos restrictivos en la clave privada."""
    try:
        if platform.system() == "Windows":
            # En Windows: usar icacls para dar permisos solo al usuario actual
            username = os.environ.get("USERNAME", "")
            subprocess.run(
                ["icacls", str(key_path), "/inheritance:r",
                 "/grant:r", f"{username}:(R,W)"],
                capture_output=True
            )
        else:
            os.chmod(key_path, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass  # No crítico


def _print_public_key(pub_key_path: Path, client: ClientConfig) -> None:
    """Imprime la clave pública y las instrucciones para registrarla."""
    if not pub_key_path.exists():
        return

    pub_key = pub_key_path.read_text(encoding="utf-8").strip()
    vcs_info = VCS_TYPES.get(client.vcs_type, {})

    console.print(f"\n[bold yellow]📋 Clave pública para {client.display_name} / {vcs_info.get('display', client.vcs_type)}:[/bold yellow]")
    console.print(f"[bold green]{pub_key}[/bold green]\n")

    # Instrucciones según el VCS
    instructions = {
        "github": "Añade esta clave en: https://github.com/settings/ssh/new",
        "gitlab": "Añade esta clave en: https://gitlab.com/-/user_settings/ssh_keys",
        "bitbucket": "Añade esta clave en: https://bitbucket.org/account/settings/ssh-keys/",
        "codecommit": "Sube la clave pública en IAM → Usuario → Security credentials → SSH keys for AWS CodeCommit",
        "azure": "Añade esta clave en: https://dev.azure.com → User settings → SSH public keys",
    }
    hint = instructions.get(client.vcs_type, "Registra esta clave pública en tu proveedor VCS.")
    console.print(f"[dim]💡 {hint}[/dim]\n")


def show_public_key(root: Path, client: ClientConfig) -> None:
    """Muestra la clave pública de un cliente."""
    pub_key_path = Path(str(client.ssh_key_path) + ".pub")
    if not pub_key_path.exists():
        console.print(f"[red]No se encontró la clave pública: {pub_key_path}[/red]")
        console.print(f"[yellow]Genera la clave con: mulesoft-manager ssh generate {client.name}[/yellow]")
        return
    _print_public_key(pub_key_path, client)


# ---------------------------------------------------------------------------
# SSH Config File
# ---------------------------------------------------------------------------

def update_ssh_config(root: Path, client: ClientConfig) -> None:
    """
    Añade o actualiza la entrada del cliente en <root>/.ssh/config.
    Gestiona también ~/.ssh/config para que git use las claves correctas.
    """
    ssh_dir = root / ".ssh"
    ssh_dir.mkdir(parents=True, exist_ok=True)
    ssh_config_path = ssh_dir / "config"

    # Leer config existente
    existing = ssh_config_path.read_text(encoding="utf-8") if ssh_config_path.exists() else ""

    # Marcadores de inicio/fin para este cliente
    marker_start = f"# ===== BEGIN {client.name.upper()} ====="
    marker_end = f"# ===== END {client.name.upper()} ====="

    # Generar la entrada para este cliente
    new_entry = _build_ssh_entry(root, client)

    # Reemplazar o añadir
    if marker_start in existing:
        # Actualizar bloque existente
        import re
        pattern = re.compile(
            rf"{re.escape(marker_start)}.*?{re.escape(marker_end)}\n?",
            re.DOTALL
        )
        updated = pattern.sub(f"{marker_start}\n{new_entry}\n{marker_end}\n", existing)
    else:
        # Añadir al final
        updated = existing + f"\n{marker_start}\n{new_entry}\n{marker_end}\n"

    ssh_config_path.write_text(updated, encoding="utf-8")
    console.print(f"[green]SSH config actualizado: {ssh_config_path}[/green]")

    # También crear/actualizar include en ~/.ssh/config
    _update_global_ssh_config(ssh_config_path)


def _build_ssh_entry(root: Path, client: ClientConfig) -> str:
    """Construye la entrada SSH para el cliente."""
    key_path = client.ssh_key_path
    # En Windows, convertir a forward slashes para SSH
    key_path_str = str(key_path).replace("\\", "/")

    if client.vcs_type == "codecommit":
        region_info = MULE_REGIONS.get(client.mule_region, {})
        aws_region = client.get("vcs", "aws_region", default="us-east-1")
        host = f"git-codecommit.{aws_region}.amazonaws.com"
        codecommit_user = client.get("vcs", "codecommit_user_id", default="APKA...")
        return SSH_CONFIG_ENTRY_CODECOMMIT_TEMPLATE.format(
            client_display=client.display_name,
            vcs_display=VCS_TYPES["codecommit"]["display"],
            ssh_alias=client.ssh_alias,
            ssh_host=host,
            region=aws_region,
            codecommit_user=codecommit_user,
            key_path=key_path_str,
        )
    else:
        vcs_info = VCS_TYPES.get(client.vcs_type, {})
        return SSH_CONFIG_ENTRY_TEMPLATE.format(
            client_display=client.display_name,
            vcs_display=vcs_info.get("display", client.vcs_type),
            ssh_alias=client.ssh_alias,
            ssh_host=client.vcs_host,
            key_path=key_path_str,
        )


def _update_global_ssh_config(workspace_ssh_config: Path) -> None:
    """
    Añade un Include en ~/.ssh/config apuntando al config del workspace.
    """
    global_ssh_dir = Path.home() / ".ssh"
    global_ssh_dir.mkdir(parents=True, exist_ok=True)
    global_config_path = global_ssh_dir / "config"

    # Leer config global existente
    existing = global_config_path.read_text(encoding="utf-8") if global_config_path.exists() else ""

    include_line = f"Include {workspace_ssh_config}"
    # Convertir a forward slashes (necesario para SSH en Windows/Git Bash)
    include_line = f"Include {str(workspace_ssh_config).replace(chr(92), '/')}"

    if include_line in existing:
        return  # Ya incluido

    # Añadir el Include al principio del archivo (debe ir antes de cualquier Host)
    marker = "# MuleSoft Manager - Workspace SSH includes"
    if marker not in existing:
        new_content = f"{marker}\n{include_line}\n\n{existing}"
        global_config_path.write_text(new_content, encoding="utf-8")
        console.print(f"[green]Include añadido en ~/.ssh/config[/green]")


def remove_ssh_config_entry(root: Path, client: ClientConfig) -> None:
    """Elimina la entrada SSH de un cliente del archivo config."""
    ssh_config_path = root / ".ssh" / "config"
    if not ssh_config_path.exists():
        return

    marker_start = f"# ===== BEGIN {client.name.upper()} ====="
    marker_end = f"# ===== END {client.name.upper()} ====="

    content = ssh_config_path.read_text(encoding="utf-8")
    if marker_start not in content:
        return

    import re
    pattern = re.compile(
        rf"\n?{re.escape(marker_start)}.*?{re.escape(marker_end)}\n?",
        re.DOTALL
    )
    updated = pattern.sub("", content)
    ssh_config_path.write_text(updated, encoding="utf-8")
    console.print(f"[green]Entrada SSH eliminada para: {client.name}[/green]")


# ---------------------------------------------------------------------------
# Git Config por Cliente
# ---------------------------------------------------------------------------

def create_gitconfig(root: Path, client: ClientConfig) -> Path:
    """
    Crea el archivo .gitconfig específico para el cliente.
    Usa GIT_CONFIG_GLOBAL conditional includes.
    """
    gitconfig_dir = root / ".gitconfig"
    gitconfig_dir.mkdir(parents=True, exist_ok=True)
    gitconfig_path = client.gitconfig_path

    # Ruta del SSH config del workspace (forward slashes para git)
    ssh_config_path = str(root / ".ssh" / "config").replace("\\", "/")
    ssh_key_path = str(client.ssh_key_path).replace("\\", "/")

    content = GITCONFIG_TEMPLATE.format(
        git_name=client.get("vcs", "git_name", default=client.vcs_username),
        git_email=client.vcs_email,
        ssh_key_path=ssh_key_path,
        ssh_config_path=ssh_config_path,
    )

    gitconfig_path.write_text(content, encoding="utf-8")
    console.print(f"[green]gitconfig creado: {gitconfig_path}[/green]")

    # Actualizar el .gitconfig global con conditional include
    _update_global_gitconfig(root, client, gitconfig_path)

    return gitconfig_path


def _update_global_gitconfig(root: Path, client: ClientConfig, client_gitconfig: Path) -> None:
    """
    Añade un 'includeIf' en el ~/.gitconfig global para que cuando Git
    opera dentro de projects/<client>/ use el gitconfig del cliente.
    """
    global_gitconfig = Path.home() / ".gitconfig"
    existing = global_gitconfig.read_text(encoding="utf-8") if global_gitconfig.exists() else ""

    # La carpeta del cliente (con forward slashes y trailing slash obligatorio para git)
    project_path = str(root / "projects" / client.name).replace("\\", "/") + "/"
    client_cfg_path = str(client_gitconfig).replace("\\", "/")

    include_section = f'[includeIf "gitdir:{project_path}"]'
    include_line = f"\tpath = {client_cfg_path}"

    if include_section in existing:
        # Ya existe, actualizar la ruta
        import re
        pattern = re.compile(
            rf"{re.escape(include_section)}\s*\n.*?(?=\[|$)",
            re.DOTALL
        )
        new_block = f"{include_section}\n{include_line}\n\n"
        if pattern.search(existing):
            updated = pattern.sub(new_block, existing)
        else:
            updated = existing + f"\n{include_section}\n{include_line}\n"
    else:
        # Añadir al final
        updated = existing + f"\n# MuleSoft Manager - {client.display_name}\n{include_section}\n{include_line}\n"

    global_gitconfig.write_text(updated, encoding="utf-8")
    console.print(f"[green]includeIf añadido en ~/.gitconfig para {client.display_name}[/green]")


def remove_gitconfig_entry(root: Path, client: ClientConfig) -> None:
    """Elimina el includeIf del cliente del ~/.gitconfig global."""
    global_gitconfig = Path.home() / ".gitconfig"
    if not global_gitconfig.exists():
        return

    project_path = str(root / "projects" / client.name).replace("\\", "/") + "/"
    include_section = f'[includeIf "gitdir:{project_path}"]'

    content = global_gitconfig.read_text(encoding="utf-8")
    if include_section not in content:
        return

    import re
    pattern = re.compile(
        rf"\n?# MuleSoft Manager - .*?\n{re.escape(include_section)}\n.*?(?=\[|$)",
        re.DOTALL
    )
    updated = pattern.sub("", content)
    global_gitconfig.write_text(updated, encoding="utf-8")


# ---------------------------------------------------------------------------
# Clonado y sincronización de repositorios
# ---------------------------------------------------------------------------

def clone_repositories(root: Path, client: ClientConfig, force: bool = False) -> dict:
    """
    Clona todos los repositorios del cliente.
    Devuelve un dict {repo_name: (ok, message)}.
    """
    results = {}
    project_dir = client.project_dir
    project_dir.mkdir(parents=True, exist_ok=True)

    repos = client.repositories
    if not repos:
        console.print(f"[yellow]No hay repositorios configurados para {client.display_name}[/yellow]")
        return results

    console.print(f"\n[bold]Clonando {len(repos)} repositorio(s) para {client.display_name}...[/bold]")

    for repo in repos:
        name = repo.get("name", "")
        url = _resolve_repo_url(repo, client)
        branch = repo.get("branch", "main")
        dest = project_dir / name

        if dest.exists() and (dest / ".git").exists():
            if force:
                console.print(f"  [yellow]→ {name}: ya existe, actualizando (pull)...[/yellow]")
                ok, msg = _git_pull(dest, branch)
            else:
                console.print(f"  [dim]→ {name}: ya clonado (omitiendo)[/dim]")
                results[name] = (True, "Ya clonado")
                continue
        else:
            console.print(f"  [cyan]→ {name}: clonando {url}...[/cyan]")
            ok, msg = _git_clone(url, dest, branch)

        results[name] = (ok, msg)
        if ok:
            console.print(f"  [green]  ✓ {name}[/green]")
        else:
            console.print(f"  [red]  ✗ {name}: {msg}[/red]")

    return results


def pull_repositories(root: Path, client: ClientConfig) -> dict:
    """
    Ejecuta git pull en todos los repositorios del cliente.
    """
    results = {}
    project_dir = client.project_dir

    if not project_dir.exists():
        console.print(f"[yellow]Carpeta de proyectos no encontrada: {project_dir}[/yellow]")
        return results

    repos = [d for d in project_dir.iterdir() if d.is_dir() and (d / ".git").exists()]

    if not repos:
        console.print(f"[yellow]No hay repositorios en {project_dir}[/yellow]")
        return results

    console.print(f"\n[bold]Actualizando {len(repos)} repositorio(s) para {client.display_name}...[/bold]")

    for repo_dir in sorted(repos):
        console.print(f"  [cyan]→ {repo_dir.name}[/cyan]", end="")
        ok, msg = _git_pull(repo_dir, branch=None)
        results[repo_dir.name] = (ok, msg)
        if ok:
            console.print(f" [green]✓ {msg}[/green]")
        else:
            console.print(f" [red]✗ {msg}[/red]")

    return results


def _resolve_repo_url(repo: dict, client: ClientConfig) -> str:
    """
    Resuelve la URL del repositorio, sustituyendo el host por el alias SSH.
    """
    url = repo.get("url", "")

    if not url:
        # Construir URL desde plantilla si no está definida
        vcs_info = VCS_TYPES.get(client.vcs_type, {})
        template = vcs_info.get("clone_url_template", "")
        url = template.format(
            alias=client.ssh_alias,
            org=client.vcs_organization,
            repo=repo.get("name", ""),
            project=repo.get("azure_project", client.vcs_organization),
        )
        return url

    # Sustituir el host por el alias SSH en URLs SSH existentes
    # Ejemplo: git@github.com:org/repo.git → git@github-cliente:org/repo.git
    ssh_host = client.vcs_host
    ssh_alias = client.ssh_alias

    if f"@{ssh_host}:" in url:
        url = url.replace(f"@{ssh_host}:", f"@{ssh_alias}:", 1)
    elif f"@{ssh_host}/" in url:
        url = url.replace(f"@{ssh_host}/", f"@{ssh_alias}/", 1)

    return url


def _git_clone(url: str, dest: Path, branch: str = "main") -> tuple[bool, str]:
    """Ejecuta git clone."""
    git = shutil.which("git")
    if git is None:
        return False, "git no encontrado"
    try:
        cmd = [git, "clone", "--branch", branch, url, str(dest)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        if result.returncode == 0:
            return True, "Clonado correctamente"
        else:
            return False, result.stderr.strip()
    except subprocess.TimeoutExpired:
        return False, "Tiempo de espera agotado"
    except Exception as e:
        return False, str(e)


def _git_pull(repo_dir: Path, branch: Optional[str] = None) -> tuple[bool, str]:
    """Ejecuta git pull en un repositorio local."""
    git = shutil.which("git")
    if git is None:
        return False, "git no encontrado"
    try:
        cmd = [git, "pull"]
        if branch:
            cmd += ["origin", branch]
        result = subprocess.run(
            cmd, cwd=str(repo_dir), capture_output=True, text=True, timeout=120
        )
        output = result.stdout.strip() or result.stderr.strip()
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, "Tiempo de espera agotado"
    except Exception as e:
        return False, str(e)


def add_repository(root: Path, client: ClientConfig, repo: dict) -> None:
    """
    Añade un nuevo repositorio a la configuración del cliente y lo clona.
    """
    repos = client.repositories
    # Evitar duplicados
    existing_names = [r.get("name") for r in repos]
    if repo.get("name") in existing_names:
        console.print(f"[yellow]El repositorio '{repo['name']}' ya está configurado.[/yellow]")
        return

    repos.append(repo)
    client.set(repos, "repositories")
    client.save()
    console.print(f"[green]Repositorio '{repo['name']}' añadido a la configuración.[/green]")

    # Clonar inmediatamente
    url = _resolve_repo_url(repo, client)
    dest = client.project_dir / repo["name"]
    branch = repo.get("branch", "main")
    ok, msg = _git_clone(url, dest, branch)
    if ok:
        console.print(f"[green]Repositorio clonado en: {dest}[/green]")
    else:
        console.print(f"[red]Error clonando: {msg}[/red]")


def remove_repository(root: Path, client: ClientConfig, repo_name: str) -> None:
    """
    Elimina un repositorio de la configuración del cliente.
    No borra los archivos locales.
    """
    repos = [r for r in client.repositories if r.get("name") != repo_name]
    client.set(repos, "repositories")
    client.save()
    console.print(f"[green]Repositorio '{repo_name}' eliminado de la configuración.[/green]")
    console.print(f"[dim]Los archivos locales no han sido borrados.[/dim]")

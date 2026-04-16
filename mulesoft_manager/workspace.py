"""
workspace.py
Creación y gestión de la estructura de carpetas del workspace MuleSoft.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.tree import Tree

from .constants import WORKSPACE_DIRS, CLIENT_DIRS
from .config import GlobalConfig, ClientConfig

console = Console()


# ---------------------------------------------------------------------------
# Creación de la estructura global del workspace
# ---------------------------------------------------------------------------

def create_workspace_structure(root: Path) -> None:
    """
    Crea toda la estructura de carpetas del workspace MuleSoft.
    Idempotente: no destruye carpetas existentes.
    """
    dirs = [
        root / ".mulesoft-manager",
        root / ".mulesoft-manager" / "clients",
        root / "tools",
        root / "tools" / "java",
        root / "tools" / "maven",
        root / ".ssh",
        root / ".gitconfig",
        root / ".vscode-workspaces",
        root / ".maven",
        root / "projects",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # Crear .gitignore en la raíz del workspace
    _create_root_gitignore(root)

    # Crear README en la raíz
    _create_workspace_readme(root)


def create_client_structure(root: Path, client_name: str) -> None:
    """
    Crea la carpeta del cliente dentro de /projects.
    """
    project_dir = root / "projects" / client_name
    project_dir.mkdir(parents=True, exist_ok=True)

    # Carpeta para settings Maven del cliente
    maven_dir = root / ".maven" / client_name
    maven_dir.mkdir(parents=True, exist_ok=True)


def ensure_workspace_exists(root: Path) -> bool:
    """Devuelve True si el workspace ya está inicializado."""
    config_file = root / ".mulesoft-manager" / "config.yaml"
    return config_file.exists()


# ---------------------------------------------------------------------------
# .gitignore del workspace
# ---------------------------------------------------------------------------

def _create_root_gitignore(root: Path) -> None:
    """Crea un .gitignore en la raíz del workspace."""
    gitignore_path = root / ".gitignore"
    if gitignore_path.exists():
        return  # No sobreescribir si ya existe

    content = """\
# MuleSoft Manager - Workspace root .gitignore
# No rastrear las claves SSH (son privadas)
.ssh/

# No rastrear credenciales de Anypoint
.maven/*/settings.xml

# Archivos de configuración con contraseñas
*.env
*.secret

# Archivos temporales de herramientas
tools/java/
tools/maven/
*.tmp
*.log

# VS Code archivos de estado local
.vscode-workspaces/*.code-workspace

# Python
__pycache__/
*.pyc
*.pyo
.venv/
venv/
"""
    gitignore_path.write_text(content, encoding="utf-8")


def _create_workspace_readme(root: Path) -> None:
    """Crea un README.md en la raíz del workspace."""
    readme_path = root / "README.md"
    if readme_path.exists():
        return

    content = """\
# MuleSoft Workspace

Workspace gestionado por **mulesoft-manager**.

## Estructura

```
workspace/
├── .mulesoft-manager/    # Configuración del gestor
│   ├── config.yaml       # Config global
│   └── clients/          # Config por cliente (*.yaml)
├── .ssh/                 # Claves SSH por cliente
├── .gitconfig/           # .gitconfig por cliente
├── .vscode-workspaces/   # Archivos .code-workspace por cliente
├── .maven/               # settings.xml Maven por cliente
├── tools/                # Java, Maven (instalación local)
│   ├── java/
│   └── maven/
└── projects/             # Repositorios por cliente
    └── <cliente>/
        ├── repo1/
        └── repo2/
```

## Comandos principales

```bash
# Inicializar workspace
python -m mulesoft_manager init

# Añadir un cliente
python -m mulesoft_manager client add

# Listar clientes
python -m mulesoft_manager client list

# Sincronizar repos de un cliente
python -m mulesoft_manager client sync <nombre>

# Verificar herramientas instaladas
python -m mulesoft_manager tools check
```

> ⚠️ **No subas a Git** las carpetas `.ssh/` ni los archivos `settings.xml` con credenciales.
"""
    readme_path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Visualización del árbol del workspace
# ---------------------------------------------------------------------------

def print_workspace_tree(root: Path, global_cfg: GlobalConfig) -> None:
    """Imprime el árbol de carpetas del workspace en la terminal."""
    from .config import list_clients

    tree = Tree(
        f"[bold cyan]📁 {root}[/bold cyan]",
        guide_style="dim",
    )

    # .mulesoft-manager
    mgr = tree.add("[bold yellow]📁 .mulesoft-manager[/bold yellow]")
    mgr.add("[green]📄 config.yaml[/green]  ← configuración global")
    clients_dir = root / ".mulesoft-manager" / "clients"
    if clients_dir.exists():
        cl_branch = mgr.add("[bold yellow]📁 clients[/bold yellow]")
        for yf in sorted(clients_dir.glob("*.yaml")):
            cl_branch.add(f"[green]📄 {yf.name}[/green]")

    # .ssh
    ssh_dir = root / ".ssh"
    ssh_branch = tree.add("[bold yellow]📁 .ssh[/bold yellow]  ← claves SSH")
    if ssh_dir.exists():
        for kf in sorted(ssh_dir.iterdir()):
            if kf.name == "config":
                ssh_branch.add(f"[blue]📄 {kf.name}[/blue]  ← SSH config routing")
            elif kf.suffix == ".pub":
                ssh_branch.add(f"[green]🔑 {kf.name}[/green]  ← clave pública")
            else:
                ssh_branch.add(f"[red]🔒 {kf.name}[/red]  ← clave privada")

    # .gitconfig
    git_branch = tree.add("[bold yellow]📁 .gitconfig[/bold yellow]  ← configs git por cliente")
    gitconfig_dir = root / ".gitconfig"
    if gitconfig_dir.exists():
        for gf in sorted(gitconfig_dir.glob("*.gitconfig")):
            git_branch.add(f"[green]📄 {gf.name}[/green]")

    # .vscode-workspaces
    ws_branch = tree.add("[bold yellow]📁 .vscode-workspaces[/bold yellow]  ← workspaces VS Code")
    ws_dir = root / ".vscode-workspaces"
    if ws_dir.exists():
        for wf in sorted(ws_dir.glob("*.code-workspace")):
            ws_branch.add(f"[cyan]📄 {wf.name}[/cyan]")

    # .maven
    maven_branch = tree.add("[bold yellow]📁 .maven[/bold yellow]  ← settings Maven por cliente")
    maven_dir = root / ".maven"
    if maven_dir.exists():
        for cf in sorted(maven_dir.iterdir()):
            if cf.is_dir():
                m = maven_branch.add(f"[bold]📁 {cf.name}[/bold]")
                m.add("[green]📄 settings.xml[/green]")

    # tools
    tools_branch = tree.add("[bold yellow]📁 tools[/bold yellow]  ← herramientas instaladas")
    tools_dir = root / "tools"
    if tools_dir.exists():
        for tf in sorted(tools_dir.iterdir()):
            if tf.is_dir():
                tools_branch.add(f"[dim]📁 {tf.name}[/dim]")

    # projects
    projects_branch = tree.add("[bold yellow]📁 projects[/bold yellow]  ← repositorios por cliente")
    projects_dir = root / "projects"
    if projects_dir.exists():
        for client_dir in sorted(projects_dir.iterdir()):
            if client_dir.is_dir():
                cb = projects_branch.add(f"[bold cyan]📁 {client_dir.name}[/bold cyan]")
                for repo_dir in sorted(client_dir.iterdir()):
                    if repo_dir.is_dir():
                        cb.add(f"[dim]📁 {repo_dir.name}[/dim]")

    console.print(tree)

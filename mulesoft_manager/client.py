"""
client.py
Operaciones de alto nivel sobre clientes MuleSoft:
  - Crear cliente completo (estructura + SSH + git + VS Code + Maven)
  - Actualizar configuración
  - Eliminar cliente
  - Listar clientes
  - Sincronizar repositorios
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .config import ClientConfig, GlobalConfig, list_clients
from .workspace import create_client_structure
from .git_manager import (
    generate_ssh_key,
    update_ssh_config,
    create_gitconfig,
    clone_repositories,
    pull_repositories,
    remove_ssh_config_entry,
    remove_gitconfig_entry,
    show_public_key,
)
from .vscode import (
    create_workspace_file,
    create_maven_settings,
    install_extensions,
)
from .constants import VCS_TYPES, MULE_REGIONS

console = Console()


# ---------------------------------------------------------------------------
# Crear cliente completo
# ---------------------------------------------------------------------------

def setup_client(
    root: Path,
    client: ClientConfig,
    global_cfg: GlobalConfig,
    generate_key: bool = True,
    clone_repos: bool = True,
    install_ext: bool = False,
) -> None:
    """
    Realiza la configuración completa de un nuevo cliente:
    1. Crea la estructura de carpetas
    2. Genera clave SSH
    3. Actualiza SSH config
    4. Crea .gitconfig del cliente
    5. Crea workspace VS Code
    6. Crea Maven settings.xml
    7. (Opcional) Clona repositorios
    8. (Opcional) Instala extensiones VS Code
    """
    vcs_info = VCS_TYPES.get(client.vcs_type, {})
    region_info = MULE_REGIONS.get(client.mule_region, MULE_REGIONS["us"])

    console.print(
        Panel(
            f"[bold cyan]Configurando cliente: {client.display_name}[/bold cyan]\n"
            f"  VCS: [yellow]{vcs_info.get('display', client.vcs_type)}[/yellow] "
            f"({client.vcs_host})\n"
            f"  Región Mule: [yellow]{region_info['display']}[/yellow]\n"
            f"  Usuario git: [yellow]{client.vcs_username}[/yellow]",
            border_style="cyan",
        )
    )

    # 1. Estructura de carpetas
    console.print("\n[bold]1/7 Creando estructura de carpetas...[/bold]")
    create_client_structure(root, client.name)
    client.save()
    console.print("[green]  ✓ Estructura creada[/green]")

    # 2. Clave SSH
    if generate_key:
        console.print(f"\n[bold]2/7 Generando clave SSH...[/bold]")
        key_path = generate_ssh_key(
            root, client,
            key_type=global_cfg.ssh_key_type,
            bits=global_cfg.ssh_key_bits,
        )
        if key_path:
            console.print("[green]  ✓ Clave SSH generada[/green]")
            console.print("[yellow]  ⚠ Registra la clave pública en tu proveedor VCS antes de continuar.[/yellow]")
        else:
            console.print("[red]  ✗ Error generando clave SSH[/red]")
    else:
        console.print("\n[dim]2/7 Clave SSH: omitida[/dim]")

    # 3. SSH config
    console.print("\n[bold]3/7 Actualizando SSH config...[/bold]")
    update_ssh_config(root, client)
    console.print("[green]  ✓ SSH config actualizado[/green]")

    # 4. .gitconfig del cliente
    console.print("\n[bold]4/7 Creando .gitconfig del cliente...[/bold]")
    create_gitconfig(root, client)
    console.print("[green]  ✓ .gitconfig creado[/green]")

    # 5. VS Code workspace
    console.print("\n[bold]5/7 Creando workspace VS Code...[/bold]")
    create_workspace_file(root, client, global_cfg)
    console.print("[green]  ✓ Workspace VS Code creado[/green]")

    # 6. Maven settings.xml
    console.print("\n[bold]6/7 Creando Maven settings.xml...[/bold]")
    create_maven_settings(root, client)
    console.print("[green]  ✓ Maven settings.xml creado[/green]")

    # 7. Clonar repositorios
    if clone_repos and client.repositories:
        console.print(f"\n[bold]7/7 Clonando repositorios...[/bold]")
        results = clone_repositories(root, client)
        ok_count = sum(1 for ok, _ in results.values() if ok)
        console.print(f"[green]  ✓ {ok_count}/{len(results)} repositorios clonados[/green]")
    else:
        if not client.repositories:
            console.print("\n[dim]7/7 Clonado de repositorios: no hay repos configurados[/dim]")
        else:
            console.print("\n[dim]7/7 Clonado de repositorios: omitido[/dim]")

    # 8. Extensiones VS Code
    if install_ext:
        console.print("\n[bold]+ Instalando extensiones VS Code...[/bold]")
        install_extensions(global_cfg.extensions)

    # Resumen
    _print_client_summary(root, client)


# ---------------------------------------------------------------------------
# Actualizar cliente
# ---------------------------------------------------------------------------

def update_client_vcs(
    root: Path,
    client: ClientConfig,
    global_cfg: GlobalConfig,
    new_vcs_type: Optional[str] = None,
    new_vcs_host: Optional[str] = None,
    new_username: Optional[str] = None,
    new_email: Optional[str] = None,
    regenerate_key: bool = False,
) -> None:
    """
    Actualiza la configuración VCS de un cliente.
    """
    console.print(f"\n[bold]Actualizando VCS para {client.display_name}...[/bold]")

    if new_vcs_type:
        client.set(new_vcs_type, "vcs", "type")
    if new_vcs_host:
        client.set(new_vcs_host, "vcs", "host")
    if new_username:
        client.set(new_username, "vcs", "username")
    if new_email:
        client.set(new_email, "vcs", "email")

    client.save()
    console.print("[green]  ✓ Configuración VCS guardada[/green]")

    # Regenerar clave SSH si se pide o si cambió el VCS
    if regenerate_key or new_vcs_type:
        console.print("\n[cyan]Regenerando clave SSH...[/cyan]")
        generate_ssh_key(root, client, key_type=global_cfg.ssh_key_type, force=True)

    # Actualizar SSH config
    update_ssh_config(root, client)

    # Actualizar .gitconfig
    create_gitconfig(root, client)

    # Actualizar VS Code workspace
    create_workspace_file(root, client, global_cfg)

    console.print(f"\n[green]✅ Cliente {client.display_name} actualizado.[/green]")


def update_client_region(
    root: Path,
    client: ClientConfig,
    global_cfg: GlobalConfig,
    new_region: str,
) -> None:
    """Cambia la región Mule de un cliente y actualiza los archivos."""
    if new_region not in MULE_REGIONS:
        console.print(f"[red]Región desconocida: {new_region}. Usa: {', '.join(MULE_REGIONS.keys())}[/red]")
        return

    client.set(new_region, "mule_region")
    client.save()

    # Actualizar Maven settings y VS Code workspace
    create_maven_settings(root, client)
    create_workspace_file(root, client, global_cfg)
    console.print(f"[green]Región actualizada a: {MULE_REGIONS[new_region]['display']}[/green]")


def update_anypoint_credentials(
    root: Path,
    client: ClientConfig,
    username: str,
    password: str,
) -> None:
    """Actualiza las credenciales de Anypoint Platform del cliente."""
    client.set(username, "anypoint", "username")
    client.set(password, "anypoint", "password")
    client.save()

    # Regenerar Maven settings con nuevas credenciales
    create_maven_settings(root, client)
    console.print(f"[green]Credenciales Anypoint actualizadas para {client.display_name}.[/green]")


# ---------------------------------------------------------------------------
# Eliminar cliente
# ---------------------------------------------------------------------------

def remove_client(root: Path, client: ClientConfig, remove_files: bool = False) -> None:
    """
    Elimina un cliente del workspace.
    Por seguridad, NO borra los archivos de código por defecto.
    """
    console.print(f"\n[bold red]Eliminando cliente: {client.display_name}[/bold red]")

    # 1. Eliminar entrada SSH config
    remove_ssh_config_entry(root, client)
    console.print("[green]  ✓ Entrada SSH eliminada[/green]")

    # 2. Eliminar includeIf del ~/.gitconfig global
    remove_gitconfig_entry(root, client)
    console.print("[green]  ✓ includeIf git eliminado[/green]")

    # 3. Borrar archivos del cliente (clave SSH, gitconfig, workspace, maven)
    files_to_delete = [
        client.ssh_key_path,
        Path(str(client.ssh_key_path) + ".pub"),
        client.gitconfig_path,
        client.workspace_file_path,
    ]
    for f in files_to_delete:
        if f.exists():
            f.unlink()
            console.print(f"[green]  ✓ Eliminado: {f.name}[/green]")

    # 4. Borrar directorio Maven
    maven_dir = root / ".maven" / client.name
    if maven_dir.exists():
        import shutil
        shutil.rmtree(maven_dir)
        console.print("[green]  ✓ Maven settings eliminados[/green]")

    # 5. (Opcional) Borrar código fuente
    if remove_files:
        project_dir = client.project_dir
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
            console.print(f"[green]  ✓ Carpeta de proyectos eliminada: {project_dir}[/green]")
    else:
        console.print(f"[dim]  El código fuente se conserva en: {client.project_dir}[/dim]")

    # 6. Eliminar config del cliente
    client.delete()
    console.print(f"[green]  ✓ Configuración del cliente eliminada[/green]")

    console.print(f"\n[green]✅ Cliente {client.display_name} eliminado correctamente.[/green]")


# ---------------------------------------------------------------------------
# Listar clientes
# ---------------------------------------------------------------------------

def print_clients_table(root: Path) -> None:
    """Imprime una tabla con todos los clientes configurados."""
    clients = list_clients(root)

    if not clients:
        console.print("[yellow]No hay clientes configurados en este workspace.[/yellow]")
        console.print("[dim]Usa: mulesoft-manager client add[/dim]")
        return

    table = Table(
        title=f"Clientes MuleSoft ({len(clients)})",
        show_header=True,
        header_style="bold cyan",
    )
    table.add_column("Nombre", style="bold")
    table.add_column("Display")
    table.add_column("VCS")
    table.add_column("Host")
    table.add_column("Región")
    table.add_column("Repos")
    table.add_column("SSH Key")
    table.add_column("Workspace")

    for client in clients:
        vcs_info = VCS_TYPES.get(client.vcs_type, {})
        repos_count = str(len(client.repositories))

        ssh_ok = "✅" if client.ssh_key_path.exists() else "❌"
        ws_ok = "✅" if client.workspace_file_path.exists() else "❌"

        table.add_row(
            client.name,
            client.display_name,
            vcs_info.get("display", client.vcs_type),
            client.vcs_host,
            client.mule_region.upper(),
            repos_count,
            ssh_ok,
            ws_ok,
        )

    console.print(table)


def print_client_detail(root: Path, client: ClientConfig) -> None:
    """Muestra el detalle completo de un cliente."""
    vcs_info = VCS_TYPES.get(client.vcs_type, {})
    region_info = MULE_REGIONS.get(client.mule_region, {})

    # Panel principal
    text = Text()
    text.append(f"Nombre: ", style="bold")
    text.append(f"{client.display_name}\n")
    text.append(f"ID: ", style="bold")
    text.append(f"{client.name}\n")
    text.append(f"Región Mule: ", style="bold")
    text.append(f"{region_info.get('display', client.mule_region)}\n")
    text.append(f"\nVCS\n", style="bold cyan")
    text.append(f"  Tipo: ", style="bold")
    text.append(f"{vcs_info.get('display', client.vcs_type)}\n")
    text.append(f"  Host: ", style="bold")
    text.append(f"{client.vcs_host}\n")
    text.append(f"  Usuario: ", style="bold")
    text.append(f"{client.vcs_username}\n")
    text.append(f"  Email: ", style="bold")
    text.append(f"{client.vcs_email}\n")
    text.append(f"  SSH Alias: ", style="bold")
    text.append(f"{client.ssh_alias}\n")

    console.print(Panel(text, title=f"[bold cyan]{client.display_name}[/bold cyan]", border_style="cyan"))

    # Archivos de configuración
    files_table = Table(title="Archivos de configuración", show_header=True)
    files_table.add_column("Archivo")
    files_table.add_column("Ruta")
    files_table.add_column("Estado")

    files = [
        ("SSH Key (privada)", client.ssh_key_path),
        ("SSH Key (pública)", Path(str(client.ssh_key_path) + ".pub")),
        (".gitconfig", client.gitconfig_path),
        ("VS Code Workspace", client.workspace_file_path),
        ("Maven settings.xml", client.maven_settings_path),
    ]

    for name, path in files:
        status = "[green]✅ Existe[/green]" if path.exists() else "[red]❌ No existe[/red]"
        files_table.add_row(name, str(path), status)

    console.print(files_table)

    # Repositorios
    repos = client.repositories
    if repos:
        repos_table = Table(title=f"Repositorios ({len(repos)})", show_header=True)
        repos_table.add_column("Nombre")
        repos_table.add_column("URL")
        repos_table.add_column("Rama")
        repos_table.add_column("Clonado")

        for repo in repos:
            repo_dir = client.project_dir / repo.get("name", "")
            cloned = "[green]✅[/green]" if (repo_dir / ".git").exists() else "[yellow]⬜[/yellow]"
            repos_table.add_row(
                repo.get("name", ""),
                repo.get("url", "(auto)"),
                repo.get("branch", "main"),
                cloned,
            )
        console.print(repos_table)
    else:
        console.print("[dim]No hay repositorios configurados.[/dim]")


# ---------------------------------------------------------------------------
# Sincronizar repositorios
# ---------------------------------------------------------------------------

def sync_client(root: Path, client: ClientConfig, full: bool = False) -> None:
    """
    Sincroniza los repositorios del cliente:
    - full=False: git pull en repos ya clonados
    - full=True: clone los que faltan + pull en los existentes
    """
    if full:
        clone_repositories(root, client, force=True)
    else:
        pull_repositories(root, client)


# ---------------------------------------------------------------------------
# Resumen final
# ---------------------------------------------------------------------------

def _print_client_summary(root: Path, client: ClientConfig) -> None:
    """Imprime un resumen de la configuración del cliente."""
    pub_key_path = Path(str(client.ssh_key_path) + ".pub")

    lines = [
        f"\n[bold green]✅ Cliente {client.display_name} configurado correctamente.[/bold green]\n",
        "[bold]Próximos pasos:[/bold]",
        f"1. [yellow]Registra la clave pública SSH[/yellow] en tu proveedor VCS:",
    ]

    if pub_key_path.exists():
        lines.append(f"   [dim]{pub_key_path.read_text(encoding='utf-8').strip()[:80]}...[/dim]")

    lines += [
        f"2. Abre VS Code con el workspace: [cyan]code \"{client.workspace_file_path}\"[/cyan]",
        f"3. Edita las credenciales Anypoint en: [dim]{client.maven_settings_path}[/dim]",
    ]

    if client.repositories:
        lines.append(
            f"4. Clona los repos: [cyan]mulesoft-manager client sync {client.name}[/cyan]"
        )

    console.print("\n".join(lines))

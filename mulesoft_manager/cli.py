"""
cli.py
Interfaz de línea de comandos principal del gestor de proyectos MuleSoft.

Comandos disponibles:
  init                      Inicializa el workspace desde cero
  tree                      Muestra el árbol del workspace
  tools check               Verifica herramientas instaladas
  tools install             Instala Java, Maven, VS Code y extensiones
  client list               Lista todos los clientes
  client add                Añade un nuevo cliente (interactivo o desde YAML)
  client show <name>        Muestra detalles de un cliente
  client update <name>      Actualiza configuración de un cliente
  client sync <name>        Sincroniza repositorios de un cliente
  client open <name>        Abre el workspace VS Code del cliente
  client remove <name>      Elimina un cliente
  ssh generate <name>       Genera clave SSH para un cliente
  ssh show <name>           Muestra la clave pública de un cliente
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from .config import (
    GlobalConfig,
    ClientConfig,
    find_workspace_root,
    save_workspace_pointer,
    list_clients,
    derive_client_names,
)
from .constants import VCS_TYPES, MULE_REGIONS, VSCODE_EXTENSIONS
from .i18n import t, set_lang, get_lang
from .workspace import (
    create_workspace_structure,
    print_workspace_tree,
    ensure_workspace_exists,
)
from .tools import (
    print_tools_status,
    install_java,
    install_maven,
    install_vscode,
    install_vscode_extensions,
    check_java,
    check_maven,
    check_vscode,
)
from .git_manager import (
    generate_ssh_key,
    show_public_key,
    add_repository,
    remove_repository,
    update_ssh_config,
    create_gitconfig,
)
from .vscode import (
    create_workspace_file,
    create_maven_settings,
    open_workspace,
)
from .client import (
    setup_client,
    update_client_vcs,
    update_client_region,
    update_anypoint_credentials,
    remove_client,
    print_clients_table,
    print_client_detail,
    sync_client,
)

console = Console()


# ---------------------------------------------------------------------------
# Utilidades internas
# ---------------------------------------------------------------------------

def _get_workspace() -> tuple[Path, GlobalConfig]:
    """Obtiene el workspace root y config, saliendo con error si no existe."""
    root = find_workspace_root()
    if root is None:
        console.print(t("cmd.no_workspace"))
        console.print(t("cmd.run_init"))
        sys.exit(1)
    return root, GlobalConfig(root)


def _get_client(root: Path, name: str) -> ClientConfig:
    """Carga un cliente, saliendo con error si no existe."""
    c = ClientConfig(root, name)
    if not c.exists():
        console.print(t("cmd.client_not_found", name=name))
        console.print(t("cmd.use_list"))
        sys.exit(1)
    return c


def _prompt_repository(
    organization: str = "",
    vcs_info: Optional[dict] = None,
    alias_hint: str = "",
) -> Optional[dict]:
    """Solicita interactivamente los datos de un repositorio."""
    console.print("\n[dim]── Datos del repositorio ──[/dim]")
    name = Prompt.ask(t("wizard.repo_name"))
    if not name:
        return None

    if vcs_info and organization and alias_hint:
        console.print(f"  [dim]Ejemplo: git@{alias_hint}:{organization}/{name}.git[/dim]")

    url = Prompt.ask("  URL (vacío = construir automáticamente desde alias SSH)", default="")
    branch = Prompt.ask("  Rama principal", default="main")
    description = Prompt.ask("  Descripción (opcional)", default="")

    repo: dict = {"name": name, "branch": branch}
    if url:
        repo["url"] = url
    if description:
        repo["description"] = description
    return repo


# ---------------------------------------------------------------------------
# Asistente de nuevo cliente
# ---------------------------------------------------------------------------

def _interactive_client_wizard(root: Path) -> Optional[ClientConfig]:
    """Asistente interactivo paso a paso para crear un nuevo cliente."""
    console.print(
        Panel(
            "[bold cyan]➕ Asistente de nuevo cliente MuleSoft[/bold cyan]",
            border_style="cyan",
        )
    )

    data: dict = {}

    # ── Identificación ──────────────────────────────────────────────────────
    console.print(f"\n[bold]{t('wizard.section_id')}[/bold]")
    console.print(f"[dim]{t('wizard.name_desc')}[/dim]")
    raw_name = Prompt.ask(t("wizard.name_prompt"))

    # Derivar sugerencias automáticamente
    derived = derive_client_names(raw_name)
    data["name"] = derived["name"]

    # Mostrar las sugerencias derivadas
    console.print(
        f"  [dim]{t('wizard.derived_header', name=derived['name'])}[/dim]\n"
        f"    {t('wizard.derived_display', display_name=derived['display_name'])}\n"
        f"    {t('wizard.derived_org',     organization=derived['organization'])}\n"
        f"    {t('wizard.derived_user',    username=derived['username'])}"
    )

    data["display_name"] = Prompt.ask(
        t("wizard.display_prompt"),
        default=derived["display_name"],
    )

    # ── Anypoint Platform ───────────────────────────────────────────────────
    console.print(f"\n[bold]{t('wizard.section_ap')}[/bold]")
    console.print(t("wizard.regions_avail"))
    for k, v in MULE_REGIONS.items():
        console.print(f"  [cyan]{k}[/cyan] → {v['display']}")
    region = Prompt.ask(t("wizard.region_prompt"), choices=list(MULE_REGIONS.keys()), default="us")
    data["mule_region"] = region

    if Confirm.ask(t("wizard.has_creds"), default=False):
        data["anypoint"] = {
            "username": Prompt.ask(t("wizard.ap_user"), default=derived["username"]),
            "password": Prompt.ask(t("wizard.ap_pass"), password=True),
        }

    # ── VCS ─────────────────────────────────────────────────────────────────
    console.print(f"\n[bold]{t('wizard.section_vcs')}[/bold]")
    console.print(t("wizard.vcs_types_avail"))
    for k, v in VCS_TYPES.items():
        console.print(f"  [cyan]{k}[/cyan] → {v['display']}")
    vcs_type = Prompt.ask(t("wizard.vcs_prompt"), choices=list(VCS_TYPES.keys()), default="github")
    vcs_info = VCS_TYPES[vcs_type]

    default_host = vcs_info["default_host"]
    if vcs_type == "codecommit":
        aws_region = Prompt.ask(t("wizard.aws_region"), default="us-east-1")
        default_host = f"git-codecommit.{aws_region}.amazonaws.com"
        data.setdefault("vcs", {})["aws_region"] = aws_region

    host     = Prompt.ask(t("wizard.vcs_host"), default=default_host)
    username = Prompt.ask(t("wizard.vcs_user"),     default=derived["username"])
    git_name = Prompt.ask(t("wizard.vcs_git_name"), default=derived["git_name"])
    email    = Prompt.ask(t("wizard.vcs_email"))
    organization = Prompt.ask(t("wizard.vcs_org"),  default=derived["organization"])

    data.setdefault("vcs", {}).update({
        "type": vcs_type,
        "host": host,
        "username": username,
        "git_name": git_name,
        "email": email,
        "organization": organization,
    })

    if vcs_type == "codecommit":
        ccu = Prompt.ask(t("wizard.cc_user"), default="APKA...")
        data["vcs"]["codecommit_user_id"] = ccu

    # ── Repositorios ────────────────────────────────────────────────────────
    console.print(f"\n[bold]{t('wizard.section_repos')}[/bold]")
    repos = []
    alias_hint = f"{vcs_info['ssh_host_alias_prefix']}-{data['name']}"

    if Confirm.ask(t("wizard.add_repos"), default=True):
        while True:
            repo = _prompt_repository(
                organization=organization,
                vcs_info=vcs_info,
                alias_hint=alias_hint,
            )
            if repo:
                repos.append(repo)
            if not Confirm.ask(t("wizard.add_another"), default=False):
                break

    data["repositories"] = repos

    # ── Confirmación ────────────────────────────────────────────────────────
    console.print(
        Panel(
            f"[bold]Resumen:[/bold]\n"
            f"{t('wizard.confirm_name',   display=data['display_name'], name=data['name'])}\n"
            f"{t('wizard.confirm_vcs',    vcs=vcs_info['display'], host=host)}\n"
            f"{t('wizard.confirm_user',   user=username, email=email)}\n"
            f"{t('wizard.confirm_region', region=MULE_REGIONS[region]['display'])}\n"
            f"{t('wizard.confirm_repos',  n=len(repos))}",
            border_style="green",
            title=t("wizard.confirm_title"),
        )
    )

    if not Confirm.ask(t("wizard.confirm_prompt")):
        console.print(t("wizard.cancelled"))
        return None

    return ClientConfig.from_dict(root, data)


# ---------------------------------------------------------------------------
# Asistente de actualización
# ---------------------------------------------------------------------------

def _interactive_update(root: Path, client: ClientConfig, cfg: GlobalConfig) -> None:
    """Menú interactivo para actualizar un cliente."""
    while True:
        console.print(
            Panel(
                f"[bold cyan]✏ Actualizar: {client.display_name}[/bold cyan]",
                border_style="cyan",
            )
        )
        options = [
            ("1", t("update.opt1")),
            ("2", t("update.opt2")),
            ("3", t("update.opt3")),
            ("4", t("update.opt4")),
            ("5", t("update.opt5")),
            ("6", t("update.opt6")),
            ("7", t("update.opt7")),
            ("8", t("update.opt8")),
            ("0", t("update.opt0")),
        ]
        for key, label in options:
            console.print(f"  [cyan]{key}[/cyan]  {label}")

        choice = Prompt.ask(t("update.option"), choices=[k for k, _ in options])

        if choice == "0":
            break

        elif choice == "1":
            for k, v in VCS_TYPES.items():
                console.print(f"  [cyan]{k}[/cyan] → {v['display']}")
            new_vcs  = Prompt.ask(t("update.new_vcs"),  choices=list(VCS_TYPES.keys()))
            new_host = Prompt.ask(t("update.new_host"), default=VCS_TYPES[new_vcs]["default_host"])
            update_client_vcs(root, client, cfg, new_vcs_type=new_vcs, new_vcs_host=new_host, regenerate_key=True)

        elif choice == "2":
            new_user  = Prompt.ask(t("update.new_user"),  default=client.vcs_username)
            new_name  = Prompt.ask(t("update.new_name"),  default=client.get("vcs", "git_name", default=client.vcs_username))
            new_email = Prompt.ask(t("update.new_email"), default=client.vcs_email)
            client.set(new_name, "vcs", "git_name")
            update_client_vcs(root, client, cfg, new_username=new_user, new_email=new_email)

        elif choice == "3":
            for k, v in MULE_REGIONS.items():
                console.print(f"  [cyan]{k}[/cyan] → {v['display']}")
            new_region = Prompt.ask(t("update.new_region"), choices=list(MULE_REGIONS.keys()))
            update_client_region(root, client, cfg, new_region)

        elif choice == "4":
            au = Prompt.ask("Usuario Anypoint", default=client.anypoint_username)
            ap = Prompt.ask("Password Anypoint", password=True)
            update_anypoint_credentials(root, client, au, ap)

        elif choice == "5":
            generate_ssh_key(root, client, key_type=cfg.ssh_key_type, force=True)
            update_ssh_config(root, client)

        elif choice == "6":
            repo = _prompt_repository(
                organization=client.vcs_organization,
                vcs_info=VCS_TYPES.get(client.vcs_type),
                alias_hint=client.ssh_alias,
            )
            if repo:
                add_repository(root, client, repo)
                create_workspace_file(root, client, cfg)

        elif choice == "7":
            repos = client.repositories
            if not repos:
                console.print("[yellow]No hay repositorios configurados.[/yellow]")
            else:
                console.print("Repositorios actuales:")
                for r in repos:
                    console.print(f"  [cyan]{r['name']}[/cyan]  [{r.get('branch','main')}]")
                repo_name = Prompt.ask("Nombre del repo a eliminar")
                remove_repository(root, client, repo_name)
                create_workspace_file(root, client, cfg)

        elif choice == "8":
            update_ssh_config(root, client)
            create_gitconfig(root, client)
            create_workspace_file(root, client, cfg)
            create_maven_settings(root, client)
            console.print("[green]✅ Todos los archivos de configuración reconstruidos.[/green]")

        console.print()


# ===========================================================================
# CLI — Grupo raíz
# ===========================================================================

@click.group()
@click.version_option(version="1.0.0", prog_name="mulesoft-manager")
@click.option("--lang", default=None, type=click.Choice(["es", "en"]),
              help="Idioma de la interfaz / Interface language (es | en)")
def cli(lang: Optional[str]):
    """
    🔧 MuleSoft Manager — Gestión normalizada de entornos MuleSoft.

    Automatiza la configuración de workspace, SSH, Git y VS Code
    para múltiples clientes en una consultora.

    Usa --lang en para cambiar el idioma a inglés.
    """
    if lang:
        set_lang(lang)


# ===========================================================================
# init
# ===========================================================================

@cli.command()
@click.option("--path", "-p", type=click.Path(), default=None,
              help="Ruta raíz del workspace (ej: C:/MuleSoft)")
@click.option("--yes", "-y", is_flag=True, help="Saltar confirmaciones")
@click.option("--install-tools", is_flag=True, help="Instalar Java, Maven y VS Code")
@click.option("--install-extensions", "install_ext", is_flag=True,
              help="Instalar extensiones VS Code recomendadas")
def init(path: Optional[str], yes: bool, install_tools: bool, install_ext: bool):
    """
    Inicializa el workspace MuleSoft desde cero.

    Crea la estructura de carpetas y guarda la configuración global.
    """
    console.print(
        Panel(
            "[bold cyan]🔧 MuleSoft Manager — Inicialización del Workspace[/bold cyan]",
            border_style="cyan",
        )
    )

    if path is None:
        path = Prompt.ask("Ruta raíz del workspace", default="C:/MuleSoft")

    root = Path(path).expanduser().resolve()

    if ensure_workspace_exists(root):
        console.print(f"[yellow]El workspace ya existe en: {root}[/yellow]")
        if not yes and not Confirm.ask("¿Reinicializar? (no borra datos)"):
            return

    console.print(f"\n[dim]Workspace root: {root}[/dim]")
    if not yes and not Confirm.ask("¿Continuar?"):
        return

    # Estructura de carpetas
    console.print("\n[bold]► Creando estructura de carpetas...[/bold]")
    create_workspace_structure(root)

    # Config global
    console.print("[bold]► Guardando configuración global...[/bold]")
    cfg = GlobalConfig.create_new(root)
    save_workspace_pointer(root)
    console.print(f"[green]  ✓ {root / '.mulesoft-manager' / 'config.yaml'}[/green]")

    # Estado de herramientas
    console.print("\n[bold]► Estado de herramientas:[/bold]")
    print_tools_status(cfg)

    # Instalación opcional
    if install_tools:
        tools_dir = root / "tools"
        if not check_java(cfg.java_home)[0]:
            install_java(cfg, tools_dir)
        if not check_maven(cfg.maven_home)[0]:
            install_maven(cfg, tools_dir)
        if not check_vscode()[0]:
            install_vscode(cfg)

    if install_ext:
        install_vscode_extensions(cfg.extensions)

    console.print(
        Panel(
            f"[bold green]✅ Workspace listo en: {root}[/bold green]\n\n"
            f"Próximos pasos:\n"
            f"  [cyan]mulesoft-manager client add[/cyan]     → añadir primer cliente\n"
            f"  [cyan]mulesoft-manager tools check[/cyan]    → verificar herramientas\n"
            f"  [cyan]mulesoft-manager tree[/cyan]           → ver estructura",
            border_style="green",
        )
    )


# ===========================================================================
# tree
# ===========================================================================

@cli.command()
def tree():
    """Muestra el árbol de carpetas del workspace."""
    root, cfg = _get_workspace()
    print_workspace_tree(root, cfg)


# ===========================================================================
# tools
# ===========================================================================

@cli.group()
def tools():
    """Gestión de herramientas: Java, Maven, VS Code."""
    pass


@tools.command("check")
def tools_check():
    """Verifica el estado de todas las herramientas instaladas."""
    root, cfg = _get_workspace()
    print_tools_status(cfg)


@tools.command("install")
@click.option("--java", "do_java", is_flag=True, help="Instalar Java JDK")
@click.option("--maven", "do_maven", is_flag=True, help="Instalar Apache Maven")
@click.option("--vscode", "do_vscode", is_flag=True, help="Instalar VS Code")
@click.option("--extensions", "do_ext", is_flag=True, help="Instalar extensiones VS Code")
@click.option("--all", "do_all", is_flag=True, help="Instalar todas las herramientas")
def tools_install(do_java: bool, do_maven: bool, do_vscode: bool, do_ext: bool, do_all: bool):
    """Instala herramientas necesarias para desarrollo MuleSoft."""
    root, cfg = _get_workspace()
    tools_dir = root / "tools"

    if not any([do_java, do_maven, do_vscode, do_ext, do_all]):
        console.print("[yellow]Especifica qué instalar:[/yellow]")
        console.print("  --java  --maven  --vscode  --extensions  --all")
        return

    if do_all or do_java:
        install_java(cfg, tools_dir)
    if do_all or do_maven:
        install_maven(cfg, tools_dir)
    if do_all or do_vscode:
        install_vscode(cfg)
    if do_all or do_ext:
        install_vscode_extensions(cfg.extensions)


# ===========================================================================
# client
# ===========================================================================

@cli.group()
def client():
    """Gestión de clientes MuleSoft."""
    pass


@client.command("list")
def client_list():
    """Lista todos los clientes configurados."""
    root, cfg = _get_workspace()
    print_clients_table(root)


@client.command("show")
@click.argument("name")
def client_show(name: str):
    """Muestra el detalle completo de un cliente."""
    root, cfg = _get_workspace()
    c = _get_client(root, name)
    print_client_detail(root, c)


@client.command("add")
@click.option("--from-file", "-f", type=click.Path(exists=True), default=None,
              help="Cargar configuración desde archivo YAML")
@click.option("--no-key", is_flag=True, help="No generar clave SSH")
@click.option("--no-clone", is_flag=True, help="No clonar repositorios")
@click.option("--install-ext", is_flag=True, help="Instalar extensiones VS Code")
def client_add(from_file: Optional[str], no_key: bool, no_clone: bool, install_ext: bool):
    """
    Añade un nuevo cliente al workspace.

    Sin argumentos lanza el asistente interactivo.
    Con --from-file carga la configuración desde un YAML.
    """
    root, cfg = _get_workspace()

    if from_file:
        client_cfg = ClientConfig.from_file(root, Path(from_file))
        console.print(f"[cyan]Cargando configuración desde: {from_file}[/cyan]")
    else:
        client_cfg = _interactive_client_wizard(root)
        if client_cfg is None:
            return

    errors = client_cfg.validate()
    if errors:
        console.print("[red]❌ Errores en la configuración:[/red]")
        for e in errors:
            console.print(f"  [red]• {e}[/red]")
        return

    if client_cfg.exists():
        console.print(f"[yellow]El cliente '{client_cfg.name}' ya existe.[/yellow]")
        if not Confirm.ask("¿Sobreescribir?"):
            return

    setup_client(root, client_cfg, cfg,
                 generate_key=not no_key,
                 clone_repos=not no_clone,
                 install_ext=install_ext)


@client.command("update")
@click.argument("name")
@click.option("--vcs-type", default=None, type=click.Choice(list(VCS_TYPES.keys())),
              help="Nuevo tipo de VCS")
@click.option("--vcs-host", default=None, help="Nuevo host VCS")
@click.option("--username", default=None, help="Nuevo usuario git")
@click.option("--email", default=None, help="Nuevo email git")
@click.option("--region", default=None, type=click.Choice(list(MULE_REGIONS.keys())),
              help="Nueva región Mule")
@click.option("--anypoint-user", default=None, help="Usuario Anypoint Platform")
@click.option("--anypoint-pass", default=None, help="Password Anypoint Platform")
@click.option("--regen-key", is_flag=True, help="Regenerar clave SSH")
@click.option("--add-repo", is_flag=True, help="Añadir un repositorio")
@click.option("--remove-repo", default=None, metavar="REPO_NAME",
              help="Eliminar un repositorio por nombre")
@click.option("--interactive", "-i", is_flag=True, help="Modo interactivo")
def client_update(
    name: str, vcs_type, vcs_host, username, email, region,
    anypoint_user, anypoint_pass, regen_key, add_repo, remove_repo, interactive
):
    """
    Actualiza la configuración de un cliente.

    Con --interactive lanza el menú guiado.
    """
    root, cfg = _get_workspace()
    c = _get_client(root, name)

    if interactive or not any([vcs_type, vcs_host, username, email, region,
                                anypoint_user, anypoint_pass, regen_key,
                                add_repo, remove_repo]):
        _interactive_update(root, c, cfg)
        return

    if any([vcs_type, vcs_host, username, email, regen_key]):
        update_client_vcs(root, c, cfg,
                          new_vcs_type=vcs_type, new_vcs_host=vcs_host,
                          new_username=username, new_email=email,
                          regenerate_key=regen_key)

    if region:
        update_client_region(root, c, cfg, region)

    if anypoint_user or anypoint_pass:
        au = anypoint_user or Prompt.ask("Usuario Anypoint")
        ap = anypoint_pass or Prompt.ask("Password Anypoint", password=True)
        update_anypoint_credentials(root, c, au, ap)

    if add_repo:
        repo = _prompt_repository(
            organization=c.vcs_organization,
            vcs_info=VCS_TYPES.get(c.vcs_type),
            alias_hint=c.ssh_alias,
        )
        if repo:
            add_repository(root, c, repo)
            create_workspace_file(root, c, cfg)

    if remove_repo:
        remove_repository(root, c, remove_repo)
        create_workspace_file(root, c, cfg)


@client.command("sync")
@click.argument("name")
@click.option("--full", is_flag=True,
              help="Clonar repos faltantes además de hacer pull en los existentes")
def client_sync(name: str, full: bool):
    """
    Sincroniza los repositorios de un cliente.

    Por defecto hace git pull en los repos ya clonados.
    Con --full también clona los que aún no están.
    """
    root, cfg = _get_workspace()
    c = _get_client(root, name)
    sync_client(root, c, full=full)


@client.command("open")
@click.argument("name")
def client_open(name: str):
    """Abre el workspace VS Code del cliente."""
    root, cfg = _get_workspace()
    c = _get_client(root, name)
    open_workspace(c)


@client.command("remove")
@click.argument("name")
@click.option("--remove-files", is_flag=True,
              help="Borrar también el código fuente (irreversible)")
@click.option("--yes", "-y", is_flag=True, help="No pedir confirmación")
def client_remove(name: str, remove_files: bool, yes: bool):
    """
    Elimina un cliente del workspace.

    Por defecto conserva el código fuente (solo elimina la configuración).
    """
    root, cfg = _get_workspace()
    c = _get_client(root, name)

    console.print(f"\n[bold red]Eliminar cliente: {c.display_name}[/bold red]")
    if remove_files:
        console.print(f"[red bold]⚠ Se eliminará el código fuente en: {c.project_dir}[/red bold]")

    if not yes and not Confirm.ask("¿Confirmar?"):
        console.print("[dim]Cancelado.[/dim]")
        return

    remove_client(root, c, remove_files=remove_files)


# ===========================================================================
# ssh
# ===========================================================================

@cli.group()
def ssh():
    """Gestión de claves SSH por cliente."""
    pass


@ssh.command("generate")
@click.argument("name")
@click.option("--force", is_flag=True, help="Regenerar aunque ya exista")
@click.option("--type", "key_type", default=None,
              type=click.Choice(["ed25519", "rsa"]),
              help="Algoritmo de clave (default: ed25519)")
def ssh_generate(name: str, force: bool, key_type: Optional[str]):
    """Genera un par de claves SSH para el cliente."""
    root, cfg = _get_workspace()
    c = _get_client(root, name)
    kt = key_type or cfg.ssh_key_type
    key_path = generate_ssh_key(root, c, key_type=kt, bits=cfg.ssh_key_bits, force=force)
    if key_path:
        update_ssh_config(root, c)


@ssh.command("show")
@click.argument("name")
def ssh_show(name: str):
    """Muestra la clave pública SSH del cliente para copiar en el VCS."""
    root, cfg = _get_workspace()
    c = _get_client(root, name)
    show_public_key(root, c)

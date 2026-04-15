"""
i18n.py
Internacionalización para la interfaz de línea de comandos (CLI).

Uso:
    from mulesoft_manager.i18n import t, set_lang, get_lang

    # Cambiar idioma
    set_lang('en')

    # Traducir
    print(t('wizard.name_prompt'))
"""

from __future__ import annotations
from typing import Any

# ---------------------------------------------------------------------------
# Diccionario de traducciones
# ---------------------------------------------------------------------------

_TRANSLATIONS: dict[str, dict[str, str]] = {

    # ── ESPAÑOL (idioma por defecto) ────────────────────────────────────────
    "es": {
        # Asistente de nuevo cliente
        "wizard.section_id":       "── Identificación ──",
        "wizard.name_desc":        "El nombre interno se usa como ID de carpeta y clave SSH.",
        "wizard.name_prompt":      "Nombre interno del cliente (ej: acme_corp, banco_sabadell)",
        "wizard.derived_header":   "Sugerencias derivadas de [bold]{name}[/bold]:",
        "wizard.derived_display":  "  nombre completo → [cyan]{display_name}[/cyan]",
        "wizard.derived_org":      "  organización    → [cyan]{organization}[/cyan]",
        "wizard.derived_user":     "  usuario git     → [cyan]{username}[/cyan]",
        "wizard.display_prompt":   "Nombre completo / empresa",
        "wizard.section_ap":       "── Anypoint Platform ──",
        "wizard.regions_avail":    "Regiones disponibles:",
        "wizard.region_prompt":    "Región Mule",
        "wizard.has_creds":        "¿Tienes las credenciales de Anypoint Platform?",
        "wizard.ap_user":          "  Usuario Anypoint",
        "wizard.ap_pass":          "  Password Anypoint",
        "wizard.section_vcs":      "── Control de versiones (VCS) ──",
        "wizard.vcs_types_avail":  "Tipos disponibles:",
        "wizard.vcs_prompt":       "Tipo de VCS",
        "wizard.aws_region":       "  Región AWS (ej: eu-west-1)",
        "wizard.vcs_host":         "Host del servidor VCS",
        "wizard.vcs_user":         "Nombre de usuario git",
        "wizard.vcs_git_name":     "Nombre real (para commits)",
        "wizard.vcs_email":        "Email git",
        "wizard.vcs_org":          "Organización / namespace",
        "wizard.cc_user":          "  CodeCommit SSH User ID (IAM)",
        "wizard.section_repos":    "── Repositorios ──",
        "wizard.add_repos":        "¿Añadir repositorios ahora?",
        "wizard.add_another":      "¿Añadir otro repositorio?",
        "wizard.repo_name":        "  Nombre del repositorio",
        "wizard.repo_url":         "  URL (vacío = construir automáticamente desde alias SSH)",
        "wizard.repo_branch":      "  Rama principal",
        "wizard.repo_desc":        "  Descripción (opcional)",
        "wizard.confirm_title":    "Nuevo cliente",
        "wizard.confirm_name":     "  Nombre:    [cyan]{display}[/cyan] ([dim]{name}[/dim])",
        "wizard.confirm_vcs":      "  VCS:       [yellow]{vcs}[/yellow] ({host})",
        "wizard.confirm_user":     "  Usuario:   {user} <{email}>",
        "wizard.confirm_region":   "  Región:    [yellow]{region}[/yellow]",
        "wizard.confirm_repos":    "  Repos:     {n}",
        "wizard.confirm_prompt":   "¿Confirmar creación del cliente?",
        "wizard.cancelled":        "[dim]Operación cancelada.[/dim]",

        # Menú de actualización
        "update.opt1":  "Cambiar herramienta VCS (GitHub → GitLab, etc.)",
        "update.opt2":  "Cambiar usuario / email git",
        "update.opt3":  "Cambiar región Mule (us / eu)",
        "update.opt4":  "Actualizar credenciales Anypoint Platform",
        "update.opt5":  "Regenerar clave SSH",
        "update.opt6":  "Añadir repositorio",
        "update.opt7":  "Eliminar repositorio",
        "update.opt8":  "Reconstruir todos los archivos de configuración",
        "update.opt0":  "Salir",
        "update.option": "\nOpción",
        "update.new_vcs": "Nuevo tipo VCS",
        "update.new_host": "Nuevo host",
        "update.new_user": "Nuevo usuario",
        "update.new_name": "Nombre real (commits)",
        "update.new_email": "Nuevo email",
        "update.new_region": "Nueva región",
        "update.ap_user": "Usuario Anypoint",
        "update.ap_pass": "Password Anypoint",
        "update.remove_repo": "Nombre del repo a eliminar",
        "update.rebuild_ok": "[green]✅ Todos los archivos de configuración reconstruidos.[/green]",

        # Comandos / mensajes generales
        "cmd.client_not_found":   "[red]❌ Cliente no encontrado: '{name}'[/red]",
        "cmd.use_list":           "[yellow]Usa [bold]mulesoft-manager client list[/bold] para ver los clientes disponibles.[/yellow]",
        "cmd.no_workspace":       "[red]❌ Workspace no inicializado.[/red]",
        "cmd.run_init":           "[yellow]Ejecuta primero: [bold]mulesoft-manager init[/bold][/yellow]",
        "cmd.cancelled":          "Operación cancelada.",
        "cmd.invalid_region":     "[red]Región desconocida: {region}. Usa: {options}[/red]",
    },

    # ── ENGLISH ─────────────────────────────────────────────────────────────
    "en": {
        # New client wizard
        "wizard.section_id":       "── Identification ──",
        "wizard.name_desc":        "The internal name is used as the folder ID and SSH key name.",
        "wizard.name_prompt":      "Internal client name (e.g.: acme_corp, acme_bank)",
        "wizard.derived_header":   "Suggestions derived from [bold]{name}[/bold]:",
        "wizard.derived_display":  "  full name    → [cyan]{display_name}[/cyan]",
        "wizard.derived_org":      "  organization → [cyan]{organization}[/cyan]",
        "wizard.derived_user":     "  git user     → [cyan]{username}[/cyan]",
        "wizard.display_prompt":   "Full name / company",
        "wizard.section_ap":       "── Anypoint Platform ──",
        "wizard.regions_avail":    "Available regions:",
        "wizard.region_prompt":    "Mule Region",
        "wizard.has_creds":        "Do you have Anypoint Platform credentials?",
        "wizard.ap_user":          "  Anypoint user",
        "wizard.ap_pass":          "  Anypoint password",
        "wizard.section_vcs":      "── Version control (VCS) ──",
        "wizard.vcs_types_avail":  "Available types:",
        "wizard.vcs_prompt":       "VCS type",
        "wizard.aws_region":       "  AWS region (e.g.: eu-west-1)",
        "wizard.vcs_host":         "VCS server host",
        "wizard.vcs_user":         "Git username",
        "wizard.vcs_git_name":     "Real name (for commits)",
        "wizard.vcs_email":        "Git email",
        "wizard.vcs_org":          "Organization / namespace",
        "wizard.cc_user":          "  CodeCommit SSH User ID (IAM)",
        "wizard.section_repos":    "── Repositories ──",
        "wizard.add_repos":        "Add repositories now?",
        "wizard.add_another":      "Add another repository?",
        "wizard.repo_name":        "  Repository name",
        "wizard.repo_url":         "  URL (empty = build automatically from SSH alias)",
        "wizard.repo_branch":      "  Main branch",
        "wizard.repo_desc":        "  Description (optional)",
        "wizard.confirm_title":    "New client",
        "wizard.confirm_name":     "  Name:    [cyan]{display}[/cyan] ([dim]{name}[/dim])",
        "wizard.confirm_vcs":      "  VCS:     [yellow]{vcs}[/yellow] ({host})",
        "wizard.confirm_user":     "  User:    {user} <{email}>",
        "wizard.confirm_region":   "  Region:  [yellow]{region}[/yellow]",
        "wizard.confirm_repos":    "  Repos:   {n}",
        "wizard.confirm_prompt":   "Confirm client creation?",
        "wizard.cancelled":        "[dim]Operation cancelled.[/dim]",

        # Update menu
        "update.opt1":  "Change VCS tool (GitHub → GitLab, etc.)",
        "update.opt2":  "Change git user / email",
        "update.opt3":  "Change Mule region (us / eu)",
        "update.opt4":  "Update Anypoint Platform credentials",
        "update.opt5":  "Regenerate SSH key",
        "update.opt6":  "Add repository",
        "update.opt7":  "Remove repository",
        "update.opt8":  "Rebuild all configuration files",
        "update.opt0":  "Exit",
        "update.option": "\nOption",
        "update.new_vcs": "New VCS type",
        "update.new_host": "New host",
        "update.new_user": "New username",
        "update.new_name": "Real name (commits)",
        "update.new_email": "New email",
        "update.new_region": "New region",
        "update.ap_user": "Anypoint user",
        "update.ap_pass": "Anypoint password",
        "update.remove_repo": "Repository name to remove",
        "update.rebuild_ok": "[green]✅ All configuration files rebuilt.[/green]",

        # General messages
        "cmd.client_not_found":   "[red]❌ Client not found: '{name}'[/red]",
        "cmd.use_list":           "[yellow]Use [bold]mulesoft-manager client list[/bold] to see available clients.[/yellow]",
        "cmd.no_workspace":       "[red]❌ Workspace not initialized.[/red]",
        "cmd.run_init":           "[yellow]Run first: [bold]mulesoft-manager init[/bold][/yellow]",
        "cmd.cancelled":          "Operation cancelled.",
        "cmd.invalid_region":     "[red]Unknown region: {region}. Use: {options}[/red]",
    },
}

# ---------------------------------------------------------------------------
# Estado del idioma activo
# ---------------------------------------------------------------------------

_current_lang: str = "es"


def set_lang(lang: str) -> None:
    """Establece el idioma activo. Opciones: 'es', 'en'."""
    global _current_lang
    if lang in _TRANSLATIONS:
        _current_lang = lang


def get_lang() -> str:
    """Devuelve el idioma activo."""
    return _current_lang


def t(key: str, **kwargs: Any) -> str:
    """
    Devuelve la traducción de una clave.
    Si no existe en el idioma activo, cae al español.
    Soporta formato: t('wizard.confirm_name', display='Acme', name='acme')
    """
    text = (
        _TRANSLATIONS.get(_current_lang, {}).get(key)
        or _TRANSLATIONS.get("es", {}).get(key)
        or key
    )
    return text.format(**kwargs) if kwargs else text

"""
config.py
Gestión de configuración global y por cliente (archivos YAML).
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any, Optional

import yaml

from .constants import (
    APP_NAME,
    APP_VERSION,
    CONFIG_DIR_NAME,
    CLIENTS_DIR_NAME,
    GLOBAL_CONFIG_FILE,
    DEFAULT_JAVA_VERSION,
    DEFAULT_MAVEN_VERSION,
    VSCODE_EXTENSIONS,
    MULE_REGIONS,
    VCS_TYPES,
)


# ---------------------------------------------------------------------------
# Derivación de nombres sugeridos a partir del nombre del cliente
# ---------------------------------------------------------------------------

def derive_client_names(raw_name: str) -> dict:
    """
    Deriva valores sugeridos para los campos del cliente a partir del nombre interno.

    Ejemplo: "acme_corp" →
        display_name  = "Acme Corp"
        organization  = "acme-corp"
        username      = "acme-corp"
        git_name      = "Acme Corp"
        short         = "acme"      (primer segmento)

    Ejemplo: "banco_santander_es" →
        display_name  = "Banco Santander Es"
        organization  = "banco-santander-es"
        username      = "banco-santander-es"
        git_name      = "Banco Santander Es"
        short         = "banco"
    """
    import re

    # Normalizar: espacios y guiones → guiones bajos; quitar caracteres especiales
    normalized = re.sub(r"[\s\-]+", "_", raw_name.strip().lower())
    normalized = re.sub(r"[^a-z0-9_]", "", normalized).strip("_")
    if not normalized:
        normalized = "cliente"

    segments = [s for s in normalized.split("_") if s]

    # Nombre completo capitalizado
    display_name = " ".join(s.capitalize() for s in segments)

    # Organización (con guiones, estilo GitHub/GitLab)
    organization = "-".join(segments)

    # Usuario git sugerido (igual que org, es la convención más común)
    username = organization

    # Nombre real para commits (igual que display)
    git_name = display_name

    # Primer segmento (para sugerencias cortas)
    short = segments[0] if segments else normalized

    return {
        "name": normalized,
        "display_name": display_name,
        "organization": organization,
        "username": username,
        "git_name": git_name,
        "short": short,
    }


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _load_yaml(path: Path) -> dict:
    """Carga un archivo YAML y devuelve el diccionario."""
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data


def _save_yaml(path: Path, data: dict) -> None:
    """Guarda un diccionario en un archivo YAML con formato legible."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        yaml.dump(data, fh, allow_unicode=True, default_flow_style=False, sort_keys=False)


# ---------------------------------------------------------------------------
# Localización del workspace
# ---------------------------------------------------------------------------

def find_workspace_root() -> Optional[Path]:
    """
    Busca el workspace root. Estrategia:
    1. Variable de entorno MULESOFT_WORKSPACE
    2. Archivo de puntero en ~/%APPDATA%/mulesoft-manager/workspace.txt
    Devuelve None si no se ha inicializado aún.
    """
    # 1. Variable de entorno
    env_path = os.environ.get("MULESOFT_WORKSPACE")
    if env_path:
        p = Path(env_path)
        if (p / CONFIG_DIR_NAME / GLOBAL_CONFIG_FILE).exists():
            return p

    # 2. Archivo de puntero en AppData
    pointer_file = _get_pointer_file()
    if pointer_file.exists():
        stored = pointer_file.read_text(encoding="utf-8").strip()
        if stored:
            p = Path(stored)
            if (p / CONFIG_DIR_NAME / GLOBAL_CONFIG_FILE).exists():
                return p

    return None


def save_workspace_pointer(root: Path) -> None:
    """Guarda la ruta del workspace en el archivo de puntero."""
    pointer_file = _get_pointer_file()
    pointer_file.parent.mkdir(parents=True, exist_ok=True)
    pointer_file.write_text(str(root), encoding="utf-8")


def _get_pointer_file() -> Path:
    """Devuelve la ruta del archivo de puntero según el SO."""
    if sys.platform == "win32":
        appdata = os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming")
        return Path(appdata) / APP_NAME / "workspace.txt"
    else:
        return Path.home() / f".{APP_NAME}" / "workspace.txt"


# ---------------------------------------------------------------------------
# Configuración Global
# ---------------------------------------------------------------------------

class GlobalConfig:
    """
    Gestiona la configuración global del workspace MuleSoft.
    Archivo: <root>/.mulesoft-manager/config.yaml
    """

    DEFAULTS: dict = {
        "version": APP_VERSION,
        "java": {
            "version": DEFAULT_JAVA_VERSION,
            "install_method": "winget",   # winget | manual
            "home": None,                  # ruta al JDK, None = detectar automáticamente
        },
        "maven": {
            "version": DEFAULT_MAVEN_VERSION,
            "install_method": "manual",   # manual (descarga Apache)
            "home": None,
        },
        "vscode": {
            "install_method": "winget",
            "extensions": VSCODE_EXTENSIONS,
        },
        "git": {
            "default_branch": "main",
            "autocrlf": "false",
        },
        "ssh": {
            "key_bits": 4096,
            "key_type": "ed25519",        # ed25519 | rsa
        },
    }

    def __init__(self, root: Path):
        self.root = root
        self._config_dir = root / CONFIG_DIR_NAME
        self._config_file = self._config_dir / GLOBAL_CONFIG_FILE
        self._data: dict = {}
        self._load()

    # ---- I/O ---------------------------------------------------------------

    def _load(self) -> None:
        if self._config_file.exists():
            self._data = _load_yaml(self._config_file)
        else:
            self._data = {}

    def save(self) -> None:
        _save_yaml(self._config_file, self._data)

    # ---- Acceso a datos ----------------------------------------------------

    def get(self, *keys: str, default: Any = None) -> Any:
        """Acceso encadenado: config.get('java', 'version')"""
        obj = self._data
        for k in keys:
            if not isinstance(obj, dict):
                return default
            obj = obj.get(k, default)
        return obj

    def set(self, value: Any, *keys: str) -> None:
        """Escritura encadenada: config.set('17', 'java', 'version')"""
        obj = self._data
        for k in keys[:-1]:
            obj = obj.setdefault(k, {})
        obj[keys[-1]] = value

    @property
    def data(self) -> dict:
        return self._data

    # ---- Propiedades de conveniencia ----------------------------------------

    @property
    def root_path(self) -> Path:
        return self.root

    @property
    def java_home(self) -> Optional[Path]:
        home = self.get("java", "home")
        return Path(home) if home else None

    @property
    def maven_home(self) -> Optional[Path]:
        home = self.get("maven", "home")
        return Path(home) if home else None

    @property
    def ssh_key_type(self) -> str:
        return self.get("ssh", "key_type", default="ed25519")

    @property
    def ssh_key_bits(self) -> int:
        return int(self.get("ssh", "key_bits", default=4096))

    @property
    def extensions(self) -> list[str]:
        return self.get("vscode", "extensions", default=VSCODE_EXTENSIONS)

    # ---- Inicialización desde cero -----------------------------------------

    @classmethod
    def create_new(cls, root: Path, overrides: Optional[dict] = None) -> "GlobalConfig":
        """Crea una configuración nueva con valores por defecto."""
        cfg = cls(root)
        import copy
        cfg._data = copy.deepcopy(cls.DEFAULTS)
        cfg._data["root_path"] = str(root)
        if overrides:
            _deep_merge(cfg._data, overrides)
        cfg.save()
        return cfg

    def is_initialized(self) -> bool:
        return self._config_file.exists() and bool(self._data)


# ---------------------------------------------------------------------------
# Configuración por Cliente
# ---------------------------------------------------------------------------

class ClientConfig:
    """
    Gestiona la configuración de un cliente MuleSoft.
    Archivo: <root>/.mulesoft-manager/clients/<name>.yaml
    """

    REQUIRED_FIELDS = ["name", "vcs", "mule_region"]

    def __init__(self, root: Path, name: str):
        self.root = root
        self.name = name.lower().replace(" ", "_")
        self._clients_dir = root / CONFIG_DIR_NAME / CLIENTS_DIR_NAME
        self._config_file = self._clients_dir / f"{self.name}.yaml"
        self._data: dict = {}
        if self._config_file.exists():
            self._load()

    # ---- I/O ---------------------------------------------------------------

    def _load(self) -> None:
        self._data = _load_yaml(self._config_file)

    def save(self) -> None:
        _save_yaml(self._config_file, self._data)

    def exists(self) -> bool:
        return self._config_file.exists()

    def delete(self) -> None:
        if self._config_file.exists():
            self._config_file.unlink()

    # ---- Acceso a datos ----------------------------------------------------

    def get(self, *keys: str, default: Any = None) -> Any:
        obj = self._data
        for k in keys:
            if not isinstance(obj, dict):
                return default
            obj = obj.get(k, default)
        return obj

    def set(self, value: Any, *keys: str) -> None:
        obj = self._data
        for k in keys[:-1]:
            obj = obj.setdefault(k, {})
        obj[keys[-1]] = value

    @property
    def data(self) -> dict:
        return self._data

    # ---- Propiedades de conveniencia ----------------------------------------

    @property
    def display_name(self) -> str:
        return self.get("display_name", default=self.name)

    @property
    def mule_region(self) -> str:
        return self.get("mule_region", default="us")

    @property
    def vcs_type(self) -> str:
        return self.get("vcs", "type", default="github")

    @property
    def vcs_host(self) -> str:
        default_host = VCS_TYPES.get(self.vcs_type, {}).get("default_host", "")
        return self.get("vcs", "host", default=default_host)

    @property
    def vcs_username(self) -> str:
        return self.get("vcs", "username", default="")

    @property
    def vcs_email(self) -> str:
        return self.get("vcs", "email", default="")

    @property
    def vcs_organization(self) -> str:
        return self.get("vcs", "organization", default="")

    @property
    def ssh_key_name(self) -> str:
        """Nombre base del archivo de clave SSH (sin extensión)."""
        default = f"{self.name}_{self.vcs_type}"
        return self.get("vcs", "ssh_key_name", default=default)

    @property
    def ssh_alias(self) -> str:
        """Alias SSH para este cliente/VCS en ~/.ssh/config."""
        prefix = VCS_TYPES.get(self.vcs_type, {}).get("ssh_host_alias_prefix", self.vcs_type)
        return f"{prefix}-{self.name}"

    @property
    def repositories(self) -> list[dict]:
        return self.get("repositories", default=[])

    @property
    def anypoint_username(self) -> str:
        return self.get("anypoint", "username", default="")

    @property
    def anypoint_password(self) -> str:
        return self.get("anypoint", "password", default="")

    @property
    def project_dir(self) -> Path:
        return self.root / "projects" / self.name

    @property
    def ssh_key_path(self) -> Path:
        return self.root / ".ssh" / self.ssh_key_name

    @property
    def gitconfig_path(self) -> Path:
        return self.root / ".gitconfig" / f"{self.name}.gitconfig"

    @property
    def workspace_file_path(self) -> Path:
        return self.root / ".vscode-workspaces" / f"{self.name}.code-workspace"

    @property
    def maven_settings_path(self) -> Path:
        return self.root / ".maven" / self.name / "settings.xml"

    # ---- Validación --------------------------------------------------------

    def validate(self) -> list[str]:
        """Devuelve lista de errores de validación."""
        errors = []
        if not self.get("name"):
            errors.append("Falta el campo 'name'")
        if not self.get("mule_region"):
            errors.append("Falta el campo 'mule_region'")
        elif self.get("mule_region") not in MULE_REGIONS:
            errors.append(f"mule_region debe ser: {', '.join(MULE_REGIONS.keys())}")
        if not self.get("vcs"):
            errors.append("Falta la sección 'vcs'")
        elif self.vcs_type not in VCS_TYPES:
            errors.append(f"vcs.type debe ser uno de: {', '.join(VCS_TYPES.keys())}")
        return errors

    # ---- Creación desde cero -----------------------------------------------

    @classmethod
    def from_dict(cls, root: Path, data: dict) -> "ClientConfig":
        """Crea un ClientConfig desde un diccionario."""
        name = data.get("name", "").lower().replace(" ", "_")
        cfg = cls(root, name)
        cfg._data = data
        cfg._data["name"] = name
        return cfg

    @classmethod
    def from_file(cls, root: Path, yaml_file: Path) -> "ClientConfig":
        """Carga un ClientConfig desde un archivo YAML externo."""
        data = _load_yaml(yaml_file)
        return cls.from_dict(root, data)


# ---------------------------------------------------------------------------
# Listado de clientes
# ---------------------------------------------------------------------------

def list_clients(root: Path) -> list[ClientConfig]:
    """Devuelve todos los clientes configurados en el workspace."""
    clients_dir = root / CONFIG_DIR_NAME / CLIENTS_DIR_NAME
    if not clients_dir.exists():
        return []
    configs = []
    for yaml_file in sorted(clients_dir.glob("*.yaml")):
        name = yaml_file.stem
        cfg = ClientConfig(root, name)
        configs.append(cfg)
    return configs


# ------------------------------------------------------------
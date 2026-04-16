"""
constants.py
Constantes globales del gestor de proyectos MuleSoft.
"""

APP_NAME = "mulesoft-manager"
APP_VERSION = "1.0.0"
CONFIG_DIR_NAME = ".mulesoft-manager"
CLIENTS_DIR_NAME = "clients"
GLOBAL_CONFIG_FILE = "config.yaml"

# ---------------------------------------------------------------------------
# Versiones por defecto de herramientas
# ---------------------------------------------------------------------------
DEFAULT_JAVA_VERSION = "17"
DEFAULT_MAVEN_VERSION = "3.9.9"

# ---------------------------------------------------------------------------
# Extensiones VS Code recomendadas para MuleSoft
# ---------------------------------------------------------------------------
VSCODE_EXTENSIONS = [
    # MuleSoft — Anypoint Extension Pack (incluye soporte Mule, DataWeave, XML, etc.)
    "salesforce.mulesoft-pack",
]

# ---------------------------------------------------------------------------
# Tipos de VCS soportados y sus configuraciones SSH
# ---------------------------------------------------------------------------
VCS_TYPES = {
    "github": {
        "display": "GitHub",
        "default_host": "github.com",
        "ssh_host_alias_prefix": "github",
        "clone_url_template": "git@{alias}:{org}/{repo}.git",
    },
    "gitlab": {
        "display": "GitLab",
        "default_host": "gitlab.com",
        "ssh_host_alias_prefix": "gitlab",
        "clone_url_template": "git@{alias}:{org}/{repo}.git",
    },
    "bitbucket": {
        "display": "Bitbucket",
        "default_host": "bitbucket.org",
        "ssh_host_alias_prefix": "bitbucket",
        "clone_url_template": "git@{alias}:{org}/{repo}.git",
    },
    "codecommit": {
        "display": "AWS CodeCommit",
        "default_host": "git-codecommit.{region}.amazonaws.com",
        "ssh_host_alias_prefix": "codecommit",
        "clone_url_template": "ssh://{alias}/v1/repos/{repo}",
    },
    "azure": {
        "display": "Azure DevOps",
        "default_host": "ssh.dev.azure.com",
        "ssh_host_alias_prefix": "azure",
        "clone_url_template": "git@{alias}:v3/{org}/{project}/{repo}",
    },
}

# ---------------------------------------------------------------------------
# Regiones de Anypoint Platform
# ---------------------------------------------------------------------------
MULE_REGIONS = {
    "us": {
        "display": "US (us1.anypoint.mulesoft.com)",
        "anypoint_url": "https://anypoint.mulesoft.com",
        "nexus_url": "https://repository.mulesoft.org/nexus/content/repositories/public/",
    },
    "eu": {
        "display": "EU (eu1.anypoint.mulesoft.com)",
        "anypoint_url": "https://eu1.anypoint.mulesoft.com",
        "nexus_url": "https://repository.mulesoft.org/nexus/content/repositories/public/",
    },
}

# ---------------------------------------------------------------------------
# Configuración de Maven para MuleSoft (settings.xml)
# ---------------------------------------------------------------------------
MAVEN_SETTINGS_TEMPLATE = """\
<?xml version="1.0" encoding="UTF-8"?>
<settings xmlns="http://maven.apache.org/SETTINGS/1.0.0"
          xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
          xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.0.0
          http://maven.apache.org/xsd/settings-1.0.0.xsd">

  <servers>
    <server>
      <id>anypoint-exchange-v3</id>
      <username>{anypoint_username}</username>
      <password>{anypoint_password}</password>
    </server>
    <server>
      <id>MuleRepository</id>
      <username>{anypoint_username}</username>
      <password>{anypoint_password}</password>
    </server>
  </servers>

  <profiles>
    <profile>
      <id>mulesoft</id>
      <repositories>
        <repository>
          <id>MuleRepository</id>
          <name>MuleSoft Repository</name>
          <url>{nexus_url}</url>
          <layout>default</layout>
        </repository>
      </repositories>
      <pluginRepositories>
        <pluginRepository>
          <id>MuleRepository</id>
          <name>MuleSoft Repository</name>
          <url>{nexus_url}</url>
          <layout>default</layout>
        </pluginRepository>
      </pluginRepositories>
    </profile>
  </profiles>

  <activeProfiles>
    <activeProfile>mulesoft</activeProfile>
  </activeProfiles>

</settings>
"""

# ---------------------------------------------------------------------------
# Configuración VS Code para MuleSoft
# ---------------------------------------------------------------------------
VSCODE_WORKSPACE_SETTINGS = {
    "java.configuration.updateBuildConfiguration": "automatic",
    "java.import.maven.enabled": True,
    "java.compile.nullAnalysis.mode": "automatic",
    "editor.formatOnSave": True,
    "editor.tabSize": 4,
    "editor.insertSpaces": True,
    "files.encoding": "utf8",
    "files.eol": "\n",
    "xml.validation.enabled": True,
    "xml.format.enabled": True,
    "yaml.validate": True,
    "git.autofetch": True,
    "git.confirmSync": False,
    "gitlens.hovers.currentLine.over": "line",
    "terminal.integrated.defaultProfile.windows": "PowerShell",
}

# ---------------------------------------------------------------------------
# Estructura de carpetas del workspace
# ---------------------------------------------------------------------------
WORKSPACE_DIRS = [
    ".mulesoft-manager",
    ".mulesoft-manager/clients",
    "tools",
    ".ssh",
    ".gitconfig",
    ".vscode-workspaces",
    "projects",
]

CLIENT_DIRS = [
    "projects/{client}",
]

# ---------------------------------------------------------------------------
# Plantilla .gitconfig por cliente
# ---------------------------------------------------------------------------
GITCONFIG_TEMPLATE = """\
[user]
    name = {git_name}
    email = {git_email}

[core]
    autocrlf = false
    safecrlf = false
    sshCommand = ssh -i "{ssh_key_path}" -F "{ssh_config_path}"

[push]
    default = simple

[pull]
    rebase = false

[init]
    defaultBranch = main
"""

# ---------------------------------------------------------------------------
# Entrada SSH config por cliente/VCS
# ---------------------------------------------------------------------------
SSH_CONFIG_ENTRY_TEMPLATE = """\
# --- {client_display} / {vcs_display} ---
Host {ssh_alias}
    HostName {ssh_host}
    User git
    IdentityFile {key_path}
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new

"""

# CodeCommit tiene user distinto
SSH_CONFIG_ENTRY_CODECOMMIT_TEMPLATE = """\
# --- {client_display} / AWS CodeCommit ({region}) ---
Host {ssh_alias}
    HostName {ssh_host}
    User {codecommit_user}
    IdentityFile {key_path}
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new

"""

# 🔧 MuleSoft Manager

Herramienta con **interfaz gráfica web** y **CLI** para normalizar la gestión de entornos
MuleSoft en consultoras con múltiples clientes, distintas regiones de Anypoint Platform
y distintas plataformas de control de versiones.

---

## ✨ Características

- **Interfaz gráfica web** — panel visual con dark theme, acceso a todas las funciones desde el navegador
- **Bilingüe ES/EN** — toggle de idioma en la GUI y opción `--lang` en la CLI
- **Workspace unificado** — una sola carpeta raíz con toda la configuración aislada por cliente
- **Multi-cliente** — cada cliente tiene su propia configuración, claves SSH e identidad Git
- **Multi-VCS** — GitHub, GitLab, Bitbucket, AWS CodeCommit, Azure DevOps
- **Multi-región** — Anypoint Platform US (`anypoint.mulesoft.com`) y EU (`eu1.anypoint.mulesoft.com`)
- **Acceso directo** — botones para abrir el repositorio VCS y Anypoint Platform de cada cliente
- **SSH automático** — genera claves ed25519/RSA y actualiza `~/.ssh/config` con alias por cliente
- **Git aislado** — `includeIf` en `~/.gitconfig` para separar identidades git por cliente
- **VS Code** — crea automáticamente un `.code-workspace` con Java, Maven y Git configurados
- **Maven** — genera `settings.xml` con credenciales Anypoint por cliente y región
- **Autocompletado de formularios** — los campos se sugieren automáticamente al escribir el nombre del cliente
- **Instalación de herramientas** — Java (Temurin), Maven, VS Code y extensiones via winget

---

## 📋 Requisitos previos

- **Python 3.10+** instalado
- **Git para Windows** (incluye `ssh-keygen` y `git-bash`)
- **Windows 10/11**

---

## 🚀 Instalación

### Con soporte GUI (recomendado)

```powershell
cd mulesoft-manager

# Instalar dependencias con Flask
pip install -r requirements-gui.txt

# Lanzar la interfaz gráfica
python start_gui.py
```

### Solo CLI

```powershell
pip install -r requirements.txt

# O instalar como paquete global
pip install -e .
mulesoft-manager --help
```

---

## 🖥️ Interfaz gráfica web (GUI)

### Arranque

```powershell
python start_gui.py
```

El servidor arranca en `http://127.0.0.1:5000` y abre el navegador automáticamente.
La página muestra los datos del primer cliente nada más abrirse: no hay pantallas vacías.

```powershell
python start_gui.py --port 8080      # Puerto personalizado
python start_gui.py --no-browser     # Sin abrir el navegador
python start_gui.py --debug          # Modo debug con recarga automática
```

### Cambio de idioma

El botón **`🌐 EN / 🌐 ES`** en la barra superior cambia el idioma al instante.
La preferencia se guarda en el navegador entre sesiones.

### Secciones

| Sección | Qué hace |
|---|---|
| **🏠 Dashboard** | Estadísticas del workspace, tabla de clientes con botones de acceso rápido |
| **👥 Clientes** | Panel dividido: lista filtrable + detalle con 4 pestañas. Al abrirse muestra el primer cliente |
| **🔧 Herramientas** | Estado de Java, Maven, VS Code y Git; instalación via winget con log en tiempo real |
| **🔑 SSH / Git** | Tabla de claves SSH, visualización de clave pública, regeneración |
| **⚙️ Ajustes** | Configuración global de Java, Maven, VS Code, SSH y Git |

### Botones de acceso directo por cliente

En la tabla de clientes (Dashboard) y en el panel de detalle (Clientes) aparecen dos botones:

- **`🐙 GitHub`** / **`🦊 GitLab`** / **`🪣 Bitbucket`** / etc. → abre la página de la organización en el VCS
- **`☁️ Anypoint US`** / **`☁️ Anypoint EU`** → abre Anypoint Platform en la región configurada del cliente

### Estructura de archivos GUI

```
mulesoft-manager/
├── start_gui.py                          ← Launcher
├── requirements-gui.txt                  ← click + rich + PyYAML + flask
└── mulesoft_manager/gui/
    ├── app.py                            ← Backend Flask + API REST completa
    ├── static/
    │   └── i18n.js                       ← Diccionario de traducciones ES/EN (~300 claves)
    └── templates/
        ├── base.html                     ← Layout, dark theme, sidebar, toggle idioma
        ├── dashboard.html                ← Panel principal
        ├── clients.html                  ← Gestión completa de clientes
        ├── tools.html                    ← Herramientas
        ├── ssh.html                      ← Claves SSH
        └── settings.html                 ← Ajustes globales
```

---

## 📁 Estructura del workspace

Al ejecutar `init`, se crea esta estructura (ej: `C:\MuleSoft`):

```
C:\MuleSoft\
├── .mulesoft-manager\          # Configuración del gestor
│   ├── config.yaml             # Config global (Java, Maven, VS Code, SSH)
│   └── clients\                # Config por cliente
│       ├── acme.yaml
│       └── globex.yaml
├── .ssh\                       # Claves SSH por cliente
│   ├── config                  # SSH config con Host aliases por cliente
│   ├── acme_github             # Clave privada (NO subir a Git)
│   ├── acme_github.pub         # Clave pública → registrar en GitHub
│   ├── globex_gitlab
│   └── globex_gitlab.pub
├── .gitconfig\                 # .gitconfig específico por cliente
│   ├── acme.gitconfig
│   └── globex.gitconfig
├── .vscode-workspaces\         # Workspaces VS Code por cliente
│   ├── acme.code-workspace
│   └── globex.code-workspace
├── .maven\                     # settings.xml Maven por cliente
│   ├── acme\
│   │   └── settings.xml        # Credenciales Anypoint ACME
│   └── globex\
│       └── settings.xml
├── tools\                      # Herramientas instaladas localmente
│   ├── java\
│   └── maven\
└── projects\                   # Código fuente por cliente
    ├── acme\
    │   ├── api-clientes\       # Repo clonado
    │   └── api-pedidos\
    └── globex\
        └── integration-api\
```

---

## 💻 Interfaz de línea de comandos (CLI)

### Idioma

```powershell
# Español (por defecto)
mulesoft-manager client add

# English
mulesoft-manager --lang en client add
```

### Inicialización

```powershell
mulesoft-manager init
mulesoft-manager init --path C:/MuleSoft --install-tools --install-extensions
```

### Gestión de clientes

```powershell
# Añadir cliente (asistente interactivo con sugerencias automáticas)
mulesoft-manager client add
mulesoft-manager client add --from-file mi_cliente.yaml

# Listar / ver detalle
mulesoft-manager client list
mulesoft-manager client show acme

# Abrir en VS Code
mulesoft-manager client open acme

# Sincronizar repositorios
mulesoft-manager client sync acme           # git pull en repos existentes
mulesoft-manager client sync acme --full    # clonar los que faltan + pull

# Actualizar cliente (menú interactivo)
mulesoft-manager client update acme --interactive

# Cambios directos por flags
mulesoft-manager client update acme --vcs-type gitlab --vcs-host git.empresa.com --regen-key
mulesoft-manager client update acme --region eu
mulesoft-manager client update acme --add-repo
mulesoft-manager client update acme --remove-repo nombre_repo
mulesoft-manager client update acme --anypoint-user nuevo@email.com --anypoint-pass pass

# Eliminar cliente
mulesoft-manager client remove acme             # conserva el código
mulesoft-manager client remove acme --remove-files
```

### SSH

```powershell
mulesoft-manager ssh generate acme             # genera clave SSH
mulesoft-manager ssh generate acme --force     # regenera (sobreescribe)
mulesoft-manager ssh show acme                 # muestra clave pública
```

### Herramientas

```powershell
mulesoft-manager tools check                   # verifica estado
mulesoft-manager tools install --all           # instala todo
mulesoft-manager tools install --java
mulesoft-manager tools install --maven
mulesoft-manager tools install --vscode
mulesoft-manager tools install --extensions
```

### Árbol del workspace

```powershell
mulesoft-manager tree
```

---

## 📄 Configuración de cliente por YAML

Plantilla disponible en `templates/client_template.yaml`:

```yaml
name: "acme"
display_name: "ACME Corporation"
mule_region: "eu"           # us | eu

anypoint:
  username: "dev@acme.com"
  password: "mi_password"   # ⚠ no subas a Git

vcs:
  type: "github"            # github | gitlab | bitbucket | codecommit | azure
  host: "github.com"
  username: "acme-dev"
  git_name: "ACME Developer"
  email: "dev@acme.com"
  organization: "acme-org"

repositories:
  - name: "api-clientes"
    url: "git@github.com:acme-org/api-clientes.git"
    branch: "main"
  - name: "api-pedidos"
    branch: "develop"       # url vacía = construye automáticamente del alias SSH
```

```powershell
mulesoft-manager client add --from-file acme.yaml
```

---

## 🔐 Cómo funciona el aislamiento SSH/Git

### SSH — alias de host

Cada cliente tiene su propia clave SSH. El archivo `~/.ssh/config` contiene
un **alias de host** por cliente/VCS para poder tener múltiples cuentas en el mismo servidor:

```
# ~/.ssh/config (generado automáticamente)
Include C:/MuleSoft/.ssh/config

# === BEGIN ACME ===
Host github-acme
    HostName github.com
    User git
    IdentityFile C:/MuleSoft/.ssh/acme_github
    IdentitiesOnly yes
    StrictHostKeyChecking accept-new

# === BEGIN GLOBEX ===
Host gitlab-globex
    HostName gitlab.com
    User git
    IdentityFile C:/MuleSoft/.ssh/globex_gitlab
    IdentitiesOnly yes
```

Las URLs de clonado usan el alias SSH:
`git@github-acme:acme-org/mi-repo.git`

### Git — identidades por proyecto

Cada cliente tiene su `.gitconfig`. El `~/.gitconfig` global usa **`includeIf`**
para aplicar el config correcto según la carpeta donde se trabaje:

```gitconfig
# ~/.gitconfig (generado automáticamente)
[includeIf "gitdir:C:/MuleSoft/projects/acme/"]
    path = C:/MuleSoft/.gitconfig/acme.gitconfig

[includeIf "gitdir:C:/MuleSoft/projects/globex/"]
    path = C:/MuleSoft/.gitconfig/globex.gitconfig
```

---

## 🌍 Regiones Anypoint Platform

| Región | URL | Nota |
|---|---|---|
| US | `https://anypoint.mulesoft.com` | Región por defecto |
| EU | `https://eu1.anypoint.mulesoft.com` | Unión Europea |

---

## ⚠ Seguridad

- **Nunca** subas `.ssh/`, `settings.xml` ni archivos con contraseñas a Git
- El `.gitignore` de la raíz del workspace ya excluye estos archivos
- Usa contraseñas o tokens con el mínimo permiso necesario en Anypoint
- Para producción, considera un gestor de secretos en lugar de YAML plano

---

## 🛠 Flujos de trabajo típicos

### Primera configuración en un PC nuevo

```powershell
# 1. Instalar Python 3.10+ y Git para Windows

# 2. Instalar mulesoft-manager
pip install -r requirements-gui.txt

# 3A. Usar la interfaz gráfica (recomendado)
python start_gui.py
# → En la GUI: Dashboard → Nuevo cliente → sigue el formulario

# 3B. O usar la CLI
mulesoft-manager init --path C:/MuleSoft --install-tools --install-extensions
mulesoft-manager client add

# 4. Registrar la clave pública SSH en el VCS del cliente
#    GUI: Clientes → pestaña SSH → Ver clave pública
mulesoft-manager ssh show nombre_cliente

# 5. Clonar repositorios
mulesoft-manager client sync nombre_cliente --full
# GUI: Clientes → Sync → Clonar pendientes

# 6. Abrir VS Code
mulesoft-manager client open nombre_cliente
# GUI: Clientes → VS Code
```

### Añadir un nuevo cliente

```powershell
# CLI
mulesoft-manager client add            # asistente con sugerencias automáticas
mulesoft-manager ssh show nuevo_cliente
mulesoft-manager client sync nuevo_cliente --full

# GUI: Dashboard → Nuevo cliente
```

### Cambiar el VCS de un cliente (ej: GitHub → GitLab)

```powershell
# CLI
mulesoft-manager client update acme --vcs-type gitlab --vcs-host git.empresa.com --regen-key
mulesoft-manager ssh show acme        # copiar nueva clave pública en GitLab

# GUI: Clientes → seleccionar cliente → General → Editar VCS
```

### Añadir nuevos repositorios

```powershell
# CLI
mulesoft-manager client update acme --add-repo
mulesoft-manager client sync acme --full

# GUI: Clientes → seleccionar cliente → Repositorios → Añadir repo
```

### Cambiar región Mule (US → EU)

```powershell
# CLI
mulesoft-manager client update acme --region eu

# GUI: Clientes → seleccionar cliente → General → Cambiar región
# El botón ☁️ Anypoint cambiará automáticamente a eu1.anypoint.mulesoft.com
```

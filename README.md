# 🔧 MuleSoft Manager

Herramienta CLI + **interfaz gráfica web** para normalizar la gestión de entornos
MuleSoft en consultoras con múltiples clientes, distintas regiones de Anypoint
y distintas plataformas de control de versiones.

---

## ✨ Características

- **Workspace unificado**: una sola carpeta raíz con toda la configuración
- **Multi-cliente**: cada cliente tiene su propia configuración aislada
- **Multi-VCS**: GitHub, GitLab, Bitbucket, AWS CodeCommit, Azure DevOps
- **Multi-región**: Anypoint Platform US (`us1`) y EU (`eu1`)
- **SSH automático**: genera claves ed25519/RSA y actualiza `~/.ssh/config`
- **Git aislado**: `includeIf` en `~/.gitconfig` para separar identidades por cliente
- **VS Code**: crea automáticamente un `.code-workspace` con Java, Maven y Git configurados
- **Maven**: genera `settings.xml` con las credenciales Anypoint por cliente
- **Instalación de herramientas**: Java (Temurin), Maven, VS Code y extensiones via winget
- **GUI web**: interfaz visual completa accesible desde el navegador

---

## 📋 Requisitos previos

- **Python 3.10+** instalado
- **Git para Windows** instalado (incluye `ssh-keygen` y `git`)
- **Windows 10/11** (la herramienta está optimizada para Windows)

---

## 🚀 Instalación

### Opción A: Instalar como paquete (recomendado)

```powershell
# 1. Clonar o descargar este repositorio
cd mulesoft-manager

# 2. Instalar dependencias y el paquete
pip install -e .

# 3. Ya disponible como comando global
mulesoft-manager --help
```

### Opción B: Ejecutar directamente con Python

```powershell
# Instalar dependencias (solo CLI)
pip install -r requirements.txt

# Ejecutar
python main.py <comando>
# o
python -m mulesoft_manager <comando>
```

---

## 🖥️ Interfaz gráfica web (GUI)

La GUI es una aplicación web local (Flask) que se abre automáticamente en el
navegador. Proporciona acceso visual completo a todas las funciones de la herramienta.

### Instalación y arranque

```powershell
# Instalar dependencias con soporte GUI (añade Flask)
pip install -r requirements-gui.txt

# Lanzar la interfaz gráfica
python start_gui.py
```

El launcher inicia el servidor en `http://127.0.0.1:5000` y abre el navegador
automáticamente. Opciones adicionales:

```powershell
python start_gui.py --port 8080      # Puerto personalizado
python start_gui.py --no-browser     # Sin abrir el navegador
python start_gui.py --debug          # Modo debug con recarga automática
```

### Secciones de la interfaz

| Sección | Descripción |
|---|---|
| **🏠 Dashboard** | Stats del workspace, tabla de clientes, acciones rápidas |
| **👥 Clientes** | Panel dividido: lista filtrable + detalle con 4 pestañas |
| **🔧 Herramientas** | Estado en tiempo real, instalación via winget, log en vivo |
| **🔑 SSH / Git** | Tabla de claves, visualización de clave pública, regeneración |
| **⚙️ Ajustes** | Configuración global de Java, Maven, VS Code, SSH y Git |

### Estructura de archivos de la GUI

```
mulesoft-manager/
├── start_gui.py                      ← Launcher (abre el navegador solo)
├── requirements-gui.txt              ← Dependencias CLI + Flask
└── mulesoft_manager/gui/
    ├── app.py                        ← Backend Flask + API REST completa
    └── templates/
        ├── base.html                 ← Layout, dark theme, sidebar, JS global
        ├── dashboard.html            ← Panel principal con estadísticas
        ├── clients.html              ← Gestión completa de clientes
        ├── tools.html                ← Estado e instalación de herramientas
        ├── ssh.html                  ← Gestión de claves SSH
        └── settings.html             ← Ajustes globales
```

---

## 📁 Estructura del workspace

Al ejecutar `init`, se crea esta estructura en la ruta elegida (ej: `C:\MuleSoft`):

```
C:\MuleSoft\
│
├── .mulesoft-manager\          # Configuración del gestor
│   ├── config.yaml             # Config global (Java, Maven, VS Code)
│   └── clients\                # Config por cliente
│       ├── acme.yaml
│       └── globex.yaml
│
├── .ssh\                       # Claves SSH por cliente
│   ├── config                  # SSH config con Host aliases
│   ├── acme_github             # Clave privada (NO subir a Git)
│   ├── acme_github.pub         # Clave pública
│   ├── globex_gitlab           # Clave privada
│   └── globex_gitlab.pub
│
├── .gitconfig\                 # .gitconfig específico por cliente
│   ├── acme.gitconfig
│   └── globex.gitconfig
│
├── .vscode-workspaces\         # Workspaces VS Code por cliente
│   ├── acme.code-workspace
│   └── globex.code-workspace
│
├── .maven\                     # settings.xml Maven por cliente
│   ├── acme\
│   │   └── settings.xml        # Credenciales Anypoint ACME
│   └── globex\
│       └── settings.xml
│
├── tools\                      # Herramientas instaladas localmente
│   ├── java\
│   └── maven\
│
└── projects\                   # Código fuente por cliente
    ├── acme\
    │   ├── api-clientes\       # Repo clonado
    │   └── api-pedidos\
    └── globex\
        └── integration-api\
```

---

## 💻 Comandos CLI

### Inicialización

```powershell
# Inicializar workspace (asistente interactivo)
mulesoft-manager init

# Inicializar con ruta específica e instalar herramientas
mulesoft-manager init --path C:/MuleSoft --install-tools --install-extensions
```

### Gestión de clientes

```powershell
# Añadir cliente (asistente interactivo)
mulesoft-manager client add

# Añadir cliente desde archivo YAML
mulesoft-manager client add --from-file mi_cliente.yaml

# Listar todos los clientes
mulesoft-manager client list

# Ver detalle de un cliente
mulesoft-manager client show acme

# Abrir workspace VS Code del cliente
mulesoft-manager client open acme

# Sincronizar repositorios (git pull)
mulesoft-manager client sync acme

# Clonar repos que faltan + pull en los existentes
mulesoft-manager client sync acme --full

# Actualizar cliente (menú interactivo)
mulesoft-manager client update acme --interactive

# Cambiar VCS (ej: de GitHub a GitLab)
mulesoft-manager client update acme --vcs-type gitlab --vcs-host git.empresa.com --regen-key

# Cambiar región Mule
mulesoft-manager client update acme --region eu

# Añadir repositorio
mulesoft-manager client update acme --add-repo

# Eliminar repositorio
mulesoft-manager client update acme --remove-repo nombre_repo

# Actualizar credenciales Anypoint
mulesoft-manager client update acme --anypoint-user nuevo@email.com --anypoint-pass nuevapass

# Eliminar cliente (conserva el código)
mulesoft-manager client remove acme

# Eliminar cliente y su código
mulesoft-manager client remove acme --remove-files
```

### SSH

```powershell
# Generar clave SSH para un cliente
mulesoft-manager ssh generate acme

# Regenerar (sobreescribir clave existente)
mulesoft-manager ssh generate acme --force

# Mostrar clave pública para copiar en GitHub/GitLab/etc.
mulesoft-manager ssh show acme
```

### Herramientas

```powershell
# Ver estado de todas las herramientas
mulesoft-manager tools check

# Instalar todas las herramientas
mulesoft-manager tools install --all

# Instalar individualmente
mulesoft-manager tools install --java
mulesoft-manager tools install --maven
mulesoft-manager tools install --vscode
mulesoft-manager tools install --extensions
```

### Visualización

```powershell
# Ver árbol de carpetas del workspace
mulesoft-manager tree
```

---

## 📄 Configuración de cliente por YAML

Para añadir un cliente sin el asistente interactivo, crea un archivo YAML
basado en la plantilla `templates/client_template.yaml`:

```yaml
name: "acme"
display_name: "ACME Corporation"
mule_region: "eu"

anypoint:
  username: "dev@acme.com"
  password: "mi_password"

vcs:
  type: "github"
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
    branch: "develop"
```

```powershell
mulesoft-manager client add --from-file acme.yaml
```

---

## 🔐 Cómo funciona el aislamiento SSH/Git

### SSH

Cada cliente tiene su propia clave SSH. El archivo `~/.ssh/config` contiene
un **alias de host** por cliente, lo que permite tener múltiples cuentas en
el mismo servidor:

```
# .ssh/config (generado automáticamente)
Host github-acme
    HostName github.com
    User git
    IdentityFile C:/MuleSoft/.ssh/acme_github
    IdentitiesOnly yes

Host github-globex
    HostName github.com
    User git
    IdentityFile C:/MuleSoft/.ssh/globex_github
    IdentitiesOnly yes
```

Las URLs de los repos se clonan usando el alias:
`git@github-acme:acme-org/mi-repo.git`

### Git identity

Cada cliente tiene su propio `.gitconfig`. El `~/.gitconfig` global contiene
**includeIf** que aplica el config del cliente solo dentro de su carpeta:

```gitconfig
# ~/.gitconfig (generado automáticamente)
[includeIf "gitdir:C:/MuleSoft/projects/acme/"]
    path = C:/MuleSoft/.gitconfig/acme.gitconfig

[includeIf "gitdir:C:/MuleSoft/projects/globex/"]
    path = C:/MuleSoft/.gitconfig/globex.gitconfig
```

---

## ⚠ Seguridad

- **Nunca** subas `.ssh/`, `settings.xml` ni archivos con contraseñas a Git
- El `.gitignore` de la raíz del workspace ya excluye estos archivos
- Usa contraseñas o tokens con el mínimo permiso necesario en Anypoint
- Para producción, considera usar gestores de secretos en lugar de YAML plano

---

## 🛠 Flujo de trabajo típico

### Primera configuración (PC nuevo)

```powershell
# 1. Instalar Python 3.10+ y Git para Windows

# 2. Instalar mulesoft-manager con soporte GUI
pip install -r requirements-gui.txt

# 3A. Arrancar la interfaz gráfica (recomendado)
python start_gui.py

# 3B. O usar la CLI directamente
mulesoft-manager init --path C:/MuleSoft --install-tools --install-extensions

# 4. Añadir primer cliente
mulesoft-manager client add
# (o desde la GUI: Dashboard → Nuevo cliente)

# 5. Registrar la clave pública SSH en GitHub/GitLab/etc.
mulesoft-manager ssh show nombre_cliente
# (o desde la GUI: SSH → Ver clave pública)

# 6. Clonar repositorios
mulesoft-manager client sync nombre_cliente --full
# (o desde la GUI: Clientes → Sync)

# 7. Abrir VS Code con el workspace del cliente
mulesoft-manager client open nombre_cliente
# (o desde la GUI: Clientes → VS Code)
```

### Añadir un nuevo cliente

```powershell
# CLI
mulesoft-manager client add
mulesoft-manager ssh show nuevo_cliente
mulesoft-manager client sync nuevo_cliente --full

# GUI: Dashboard → Nuevo cliente → sigue el formulario
python start_gui.py
```

### Cambiar de GitHub a GitLab para un cliente

```powershell
# CLI
mulesoft-manager client update acme --vcs-type gitlab --vcs-host git.empresa.com --regen-key
mulesoft-manager ssh show acme

# GUI: Clientes → seleccionar cliente → pestaña General → Editar VCS
```

### Añadir nuevos repositorios a un cliente

```powershell
# CLI
mulesoft-manager client update acme --add-repo
mulesoft-manager client sync acme --full

# GUI: Clientes → seleccionar cliente → pestaña Repositorios → Añadir repo
```

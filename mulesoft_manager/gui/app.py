"""
app.py
Aplicación Flask que sirve la interfaz gráfica web del MuleSoft Manager.
API REST + Server-Sent Events para operaciones en tiempo real.
"""

from __future__ import annotations

import json
import os
import queue
import subprocess
import sys
import threading
from pathlib import Path
from typing import Optional

from flask import (
    Flask, render_template, jsonify, request,
    redirect, url_for, Response, stream_with_context
)

# Añadir el directorio raíz del paquete al path
_pkg_root = Path(__file__).parent.parent.parent
if str(_pkg_root) not in sys.path:
    sys.path.insert(0, str(_pkg_root))

from mulesoft_manager.config import (
    GlobalConfig, ClientConfig,
    find_workspace_root, save_workspace_pointer, list_clients
)
from mulesoft_manager.constants import VCS_TYPES, MULE_REGIONS, VSCODE_EXTENSIONS
from mulesoft_manager.workspace import (
    create_workspace_structure, ensure_workspace_exists
)
from mulesoft_manager.tools import (
    check_java, check_maven, check_vscode, check_git, check_ssh_keygen
)
from mulesoft_manager.git_manager import (
    generate_ssh_key, update_ssh_config, create_gitconfig,
    clone_repositories, pull_repositories
)
from mulesoft_manager.vscode import (
    create_workspace_file, create_maven_settings
)
from mulesoft_manager.client import (
    setup_client, update_client_vcs, update_client_region,
    update_anypoint_credentials, remove_client
)

# ---------------------------------------------------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = "mulesoft-manager-gui-secret"

# Cola para SSE (Server-Sent Events)
_event_queues: dict[str, queue.Queue] = {}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _workspace() -> Optional[tuple[Path, GlobalConfig]]:
    root = find_workspace_root()
    if root is None:
        return None
    return root, GlobalConfig(root)


def _client_data(client: ClientConfig) -> dict:
    """Serializa un ClientConfig a dict para JSON/template."""
    repos = client.repositories
    repos_with_status = []
    for r in repos:
        repo_dir = client.project_dir / r.get("name", "")
        repos_with_status.append({
            **r,
            "cloned": (repo_dir / ".git").exists(),
            "path": str(repo_dir),
        })

    vcs_info = VCS_TYPES.get(client.vcs_type, {})
    region_info = MULE_REGIONS.get(client.mule_region, {})

    return {
        "name": client.name,
        "display_name": client.display_name,
        "mule_region": client.mule_region,
        "mule_region_display": region_info.get("display", client.mule_region),
        "anypoint_url": region_info.get("anypoint_url", ""),
        "anypoint_username": client.anypoint_username,
        "vcs_type": client.vcs_type,
        "vcs_display": vcs_info.get("display", client.vcs_type),
        "vcs_host": client.vcs_host,
        "vcs_username": client.vcs_username,
        "vcs_email": client.vcs_email,
        "vcs_organization": client.vcs_organization,
        "ssh_alias": client.ssh_alias,
        "ssh_key_name": client.ssh_key_name,
        "ssh_key_exists": client.ssh_key_path.exists(),
        "pub_key_path": str(client.ssh_key_path) + ".pub",
        "pub_key_exists": (Path(str(client.ssh_key_path) + ".pub")).exists(),
        "gitconfig_exists": client.gitconfig_path.exists(),
        "workspace_exists": client.workspace_file_path.exists(),
        "maven_settings_exists": client.maven_settings_path.exists(),
        "workspace_file": str(client.workspace_file_path),
        "project_dir": str(client.project_dir),
        "repositories": repos_with_status,
        "repo_count": len(repos),
        "cloned_count": sum(1 for r in repos_with_status if r["cloned"]),
    }


def _send_event(session_id: str, event_type: str, data: dict) -> None:
    """Envía un evento SSE a una sesión."""
    q = _event_queues.get(session_id)
    if q:
        q.put({"type": event_type, "data": data})


# ---------------------------------------------------------------------------
# Páginas principales
# ---------------------------------------------------------------------------

@app.route("/")
def dashboard():
    ws = _workspace()
    if ws is None:
        return render_template("dashboard.html",
                               initialized=False,
                               vcs_types=VCS_TYPES,
                               mule_regions=MULE_REGIONS)

    root, cfg = ws
    clients = list_clients(root)

    total_repos = sum(len(c.repositories) for c in clients)
    cloned_repos = sum(
        sum(1 for r in c.repositories
            if (c.project_dir / r.get("name", "") / ".git").exists())
        for c in clients
    )

    tools_ok = sum([
        check_java(cfg.java_home)[0],
        check_maven(cfg.maven_home)[0],
        check_vscode()[0],
        check_git()[0],
    ])

    return render_template("dashboard.html",
                           initialized=True,
                           root=str(root),
                           clients=[_client_data(c) for c in clients],
                           client_count=len(clients),
                           total_repos=total_repos,
                           cloned_repos=cloned_repos,
                           tools_ok=tools_ok,
                           vcs_types=VCS_TYPES,
                           mule_regions=MULE_REGIONS)


@app.route("/clients")
def clients_page():
    ws = _workspace()
    if ws is None:
        return redirect(url_for("dashboard"))
    root, cfg = ws
    all_clients = list_clients(root)
    clients = [_client_data(c) for c in all_clients]

    # QoL: si no hay cliente seleccionado explícitamente, pre-seleccionar el primero
    selected = request.args.get("selected")
    if not selected and all_clients:
        selected = all_clients[0].name

    return render_template("clients.html",
                           clients=clients,
                           selected=selected,
                           vcs_types=VCS_TYPES,
                           mule_regions=MULE_REGIONS)


@app.route("/tools")
def tools_page():
    ws = _workspace()
    if ws is None:
        return redirect(url_for("dashboard"))
    root, cfg = ws
    return render_template("tools.html",
                           java_home=str(cfg.java_home or ""),
                           maven_home=str(cfg.maven_home or ""),
                           java_version=cfg.get("java", "version", default="17"),
                           maven_version=cfg.get("maven", "version", default="3.9.9"))


@app.route("/ssh")
def ssh_page():
    ws = _workspace()
    if ws is None:
        return redirect(url_for("dashboard"))
    root, cfg = ws
    clients = list_clients(root)
    ssh_keys = []
    for c in clients:
        priv = c.ssh_key_path
        pub = Path(str(priv) + ".pub")
        ssh_keys.append({
            "client": c.name,
            "client_display": c.display_name,
            "vcs": c.vcs_type,
            "vcs_display": VCS_TYPES.get(c.vcs_type, {}).get("display", c.vcs_type),
            "key_name": c.ssh_key_name,
            "alias": c.ssh_alias,
            "priv_exists": priv.exists(),
            "pub_exists": pub.exists(),
            "pub_path": str(pub),
        })
    return render_template("ssh.html", ssh_keys=ssh_keys,
                           clients=[_client_data(c) for c in clients])


@app.route("/settings")
def settings_page():
    ws = _workspace()
    if ws is None:
        return redirect(url_for("dashboard"))
    root, cfg = ws
    return render_template("settings.html",
                           cfg=cfg.data,
                           root=str(root),
                           extensions=cfg.extensions,
                           default_extensions=VSCODE_EXTENSIONS)


# ---------------------------------------------------------------------------
# API: Workspace
# ---------------------------------------------------------------------------

@app.route("/api/workspace/init", methods=["POST"])
def api_init_workspace():
    data = request.json or {}
    path = data.get("path", "C:/MuleSoft")
    root = Path(path).expanduser().resolve()
    try:
        create_workspace_structure(root)
        cfg = GlobalConfig.create_new(root)
        save_workspace_pointer(root)
        return jsonify({"ok": True, "root": str(root)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/workspace/tree")
def api_workspace_tree():
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False, "error": "No inicializado"})
    root, cfg = ws

    def scan(path: Path, depth: int = 0) -> dict:
        if depth > 3:
            return None
        is_dir = path.is_dir()
        node = {
            "name": path.name,
            "type": "dir" if is_dir else "file",
            "children": []
        }
        if is_dir and depth < 3:
            try:
                for child in sorted(path.iterdir()):
                    if child.name.startswith("__pycache__"):
                        continue
                    sub = scan(child, depth + 1)
                    if sub:
                        node["children"].append(sub)
            except PermissionError:
                pass
        return node

    tree = scan(root)
    return jsonify({"ok": True, "tree": tree})


# ---------------------------------------------------------------------------
# API: Clientes
# ---------------------------------------------------------------------------

@app.route("/api/clients", methods=["GET"])
def api_clients_list():
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False, "error": "No inicializado"})
    root, cfg = ws
    clients = [_client_data(c) for c in list_clients(root)]
    return jsonify({"ok": True, "clients": clients})


@app.route("/api/clients", methods=["POST"])
def api_clients_add():
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False, "error": "Workspace no inicializado"}), 400
    root, cfg = ws

    data = request.json or {}
    try:
        client_cfg = ClientConfig.from_dict(root, data)
        errors = client_cfg.validate()
        if errors:
            return jsonify({"ok": False, "errors": errors}), 400

        generate_key = data.pop("generate_key", True)
        clone_repos = data.pop("clone_repos", False)

        setup_client(root, client_cfg, cfg,
                     generate_key=generate_key,
                     clone_repos=clone_repos,
                     install_ext=False)

        return jsonify({"ok": True, "client": _client_data(client_cfg)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/clients/<name>", methods=["GET"])
def api_client_get(name: str):
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False, "error": "No inicializado"}), 400
    root, cfg = ws
    c = ClientConfig(root, name)
    if not c.exists():
        return jsonify({"ok": False, "error": "Cliente no encontrado"}), 404
    return jsonify({"ok": True, "client": _client_data(c)})


@app.route("/api/clients/<name>", methods=["PUT"])
def api_client_update(name: str):
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False}), 400
    root, cfg = ws
    c = ClientConfig(root, name)
    if not c.exists():
        return jsonify({"ok": False, "error": "Cliente no encontrado"}), 404

    data = request.json or {}
    action = data.get("action", "update_vcs")

    try:
        if action == "update_vcs":
            update_client_vcs(root, c, cfg,
                              new_vcs_type=data.get("vcs_type"),
                              new_vcs_host=data.get("vcs_host"),
                              new_username=data.get("username"),
                              new_email=data.get("email"),
                              regenerate_key=data.get("regen_key", False))
        elif action == "update_region":
            update_client_region(root, c, cfg, data["region"])
        elif action == "update_anypoint":
            update_anypoint_credentials(root, c, data["username"], data["password"])
        elif action == "add_repo":
            from mulesoft_manager.git_manager import add_repository
            add_repository(root, c, data["repo"])
            create_workspace_file(root, c, cfg)
        elif action == "remove_repo":
            from mulesoft_manager.git_manager import remove_repository
            remove_repository(root, c, data["repo_name"])
            create_workspace_file(root, c, cfg)
        elif action == "rebuild":
            update_ssh_config(root, c)
            create_gitconfig(root, c)
            create_workspace_file(root, c, cfg)
            create_maven_settings(root, c)

        return jsonify({"ok": True, "client": _client_data(c)})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/clients/<name>", methods=["DELETE"])
def api_client_delete(name: str):
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False}), 400
    root, cfg = ws
    c = ClientConfig(root, name)
    if not c.exists():
        return jsonify({"ok": False, "error": "Cliente no encontrado"}), 404

    remove_files = request.args.get("remove_files", "false").lower() == "true"
    try:
        remove_client(root, c, remove_files=remove_files)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/clients/<name>/sync", methods=["POST"])
def api_client_sync(name: str):
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False}), 400
    root, cfg = ws
    c = ClientConfig(root, name)
    if not c.exists():
        return jsonify({"ok": False, "error": "Cliente no encontrado"}), 404

    full = request.json.get("full", False) if request.json else False
    try:
        if full:
            results = clone_repositories(root, c)
        else:
            results = pull_repositories(root, c)
        return jsonify({
            "ok": True,
            "results": {k: {"ok": v[0], "msg": v[1]} for k, v in results.items()}
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/clients/<name>/open", methods=["POST"])
def api_client_open(name: str):
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False}), 400
    root, cfg = ws
    c = ClientConfig(root, name)
    if not c.exists():
        return jsonify({"ok": False}), 404

    ws_path = c.workspace_file_path
    if not ws_path.exists():
        return jsonify({"ok": False, "error": "Workspace VS Code no encontrado"}), 400

    try:
        import shutil
        code = shutil.which("code") or "code"
        subprocess.Popen([code, str(ws_path)])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ---------------------------------------------------------------------------
# API: Herramientas
# ---------------------------------------------------------------------------

@app.route("/api/tools/status")
def api_tools_status():
    ws = _workspace()
    cfg = ws[1] if ws else None
    java_home = cfg.java_home if cfg else None
    maven_home = cfg.maven_home if cfg else None

    java_ok, java_ver = check_java(java_home)
    maven_ok, maven_ver = check_maven(maven_home)
    vscode_ok, vscode_ver = check_vscode()
    git_ok, git_ver = check_git()
    ssh_ok, ssh_ver = check_ssh_keygen()

    return jsonify({
        "ok": True,
        "tools": {
            "java": {"installed": java_ok, "version": java_ver},
            "maven": {"installed": maven_ok, "version": maven_ver},
            "vscode": {"installed": vscode_ok, "version": vscode_ver},
            "git": {"installed": git_ok, "version": git_ver},
            "ssh_keygen": {"installed": ssh_ok, "version": ssh_ver},
        }
    })


@app.route("/api/tools/install/<tool>", methods=["POST"])
def api_tools_install(tool: str):
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False, "error": "Workspace no inicializado"}), 400
    root, cfg = ws

    session_id = request.json.get("session_id", "default") if request.json else "default"
    q: queue.Queue = queue.Queue()
    _event_queues[session_id] = q

    def run_install():
        import io
        from contextlib import redirect_stdout
        try:
            tools_dir = root / "tools"
            if tool == "java":
                from mulesoft_manager.tools import install_java
                install_java(cfg, tools_dir)
            elif tool == "maven":
                from mulesoft_manager.tools import install_maven
                install_maven(cfg, tools_dir)
            elif tool == "vscode":
                from mulesoft_manager.tools import install_vscode
                install_vscode(cfg)
            elif tool == "extensions":
                from mulesoft_manager.tools import install_vscode_extensions
                install_vscode_extensions(cfg.extensions)
            q.put({"type": "done", "data": {"ok": True}})
        except Exception as e:
            q.put({"type": "done", "data": {"ok": False, "error": str(e)}})

    threading.Thread(target=run_install, daemon=True).start()
    return jsonify({"ok": True, "session_id": session_id})


# ---------------------------------------------------------------------------
# API: SSH
# ---------------------------------------------------------------------------

@app.route("/api/ssh/<name>/generate", methods=["POST"])
def api_ssh_generate(name: str):
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False}), 400
    root, cfg = ws
    c = ClientConfig(root, name)
    if not c.exists():
        return jsonify({"ok": False, "error": "Cliente no encontrado"}), 404

    force = (request.json or {}).get("force", False)
    try:
        key_path = generate_ssh_key(root, c, key_type=cfg.ssh_key_type,
                                    bits=cfg.ssh_key_bits, force=force)
        if key_path:
            update_ssh_config(root, c)
            pub = Path(str(key_path) + ".pub")
            pub_key = pub.read_text(encoding="utf-8").strip() if pub.exists() else ""
            return jsonify({"ok": True, "pub_key": pub_key})
        return jsonify({"ok": False, "error": "Error generando clave"})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/ssh/<name>/public-key")
def api_ssh_public_key(name: str):
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False}), 400
    root, cfg = ws
    c = ClientConfig(root, name)
    if not c.exists():
        return jsonify({"ok": False, "error": "Cliente no encontrado"}), 404

    pub = Path(str(c.ssh_key_path) + ".pub")
    if not pub.exists():
        return jsonify({"ok": False, "error": "Clave pública no encontrada"})

    pub_key = pub.read_text(encoding="utf-8").strip()
    vcs_instructions = {
        "github": "https://github.com/settings/ssh/new",
        "gitlab": "https://gitlab.com/-/user_settings/ssh_keys",
        "bitbucket": "https://bitbucket.org/account/settings/ssh-keys/",
        "codecommit": "IAM → Usuario → Security credentials → SSH keys for AWS CodeCommit",
        "azure": "https://dev.azure.com → User settings → SSH public keys",
    }
    return jsonify({
        "ok": True,
        "pub_key": pub_key,
        "instructions": vcs_instructions.get(c.vcs_type, "Añade la clave en tu proveedor VCS"),
    })


# ---------------------------------------------------------------------------
# API: Configuración global
# ---------------------------------------------------------------------------

@app.route("/api/config", methods=["GET"])
def api_config_get():
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False, "error": "No inicializado"}), 400
    root, cfg = ws
    return jsonify({"ok": True, "config": cfg.data})


@app.route("/api/config", methods=["PUT"])
def api_config_put():
    ws = _workspace()
    if ws is None:
        return jsonify({"ok": False}), 400
    root, cfg = ws

    data = request.json or {}
    try:
        # Actualizar campos permitidos
        allowed = ["java", "maven", "vscode", "git", "ssh"]
        for key in allowed:
            if key in data:
                cfg.set(data[key], key)
        cfg.save()
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


# ---------------------------------------------------------------------------
# SSE — eventos en tiempo real
# ---------------------------------------------------------------------------

@app.route("/api/events/<session_id>")
def api_events(session_id: str):
    q: queue.Queue = queue.Queue()
    _event_queues[session_id] = q

    def generate():
        while True:
            try:
                event = q.get(timeout=30)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("type") == "done":
                    break
            except queue.Empty:
                yield "data: {\"type\": \"ping\"}\n\n"

    return Response(
        stream_with_context(generate()),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )

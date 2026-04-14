/**
 * i18n.js — Sistema de internacionalización para MuleSoft Manager GUI
 * Idiomas: Español (es) · English (en)
 *
 * Uso en HTML:  <span data-i18n="nav.clients">Clientes</span>
 * Uso en JS:    t('common.cancel')  →  "Cancel" / "Cancelar"
 */

/* ============================================================
   DICCIONARIO DE TRADUCCIONES
   ============================================================ */
const TRANSLATIONS = {

  /* ── ESPAÑOL ──────────────────────────────────────────────── */
  es: {
    // Sidebar
    'sidebar.main':          'Principal',
    'sidebar.config':        'Configuración',
    'sidebar.cli':           'Windows · Python CLI',
    'nav.dashboard':         'Dashboard',
    'nav.clients':           'Clientes',
    'nav.tools':             'Herramientas',
    'nav.ssh':               'SSH / Git',
    'nav.settings':          'Ajustes',

    // Topbar / común
    'common.cancel':         'Cancelar',
    'common.confirm':        'Confirmar',
    'common.save':           'Guardar',
    'common.delete':         'Eliminar',
    'common.add':            'Añadir',
    'common.close':          'Cerrar',
    'common.copy':           '📋 Copiar',
    'common.loading':        'Cargando…',
    'common.yes':            'Sí',
    'common.no':             'No',
    'common.optional':       'opcional',
    'common.suggested':      'sugerido',
    'common.exists':         '✓ Existe',
    'common.missing':        '✗ Falta',
    'common.rebuild':        '🔄 Reconstruir todo',
    'common.open_explorer':  '📂 Abrir en Explorer',
    'common.copy_path':      '📋 Copiar ruta',
    'common.see_all':        'Ver todos →',
    'common.discard':        '↺ Descartar',
    'common.save_all':       '💾 Guardar todos los cambios',

    // Modal de confirmación
    'modal.confirm_title':   'Confirmar acción',
    'modal.confirm_btn':     'Confirmar',

    // Dashboard
    'dashboard.title':           'Dashboard',
    'dashboard.workspace_chip':  'Workspace activo',
    'dashboard.new_client_btn':  '＋ Nuevo cliente',
    'dashboard.stat_clients':    'Clientes configurados',
    'dashboard.stat_repos':      'Repos clonados',
    'dashboard.stat_tools':      'Herramientas instaladas',
    'dashboard.stat_add':        'Nuevo cliente',
    'dashboard.stat_add_sub':    'Añadir configuración',
    'dashboard.card_clients':    'Clientes',
    'dashboard.quick_actions':   '⚡ Acciones rápidas',
    'dashboard.btn_manage':      '👥 Gestionar clientes',
    'dashboard.btn_tools':       '🔧 Herramientas',
    'dashboard.btn_ssh':         '🔑 SSH / Git',
    'dashboard.tools_card':      '🔧 Herramientas',
    'dashboard.col_client':      'Cliente',
    'dashboard.col_vcs':         'VCS',
    'dashboard.col_region':      'Región',
    'dashboard.col_repos':       'Repos',
    'dashboard.col_status':      'Estado',
    'dashboard.badge_ready':     '✓ Listo',
    'dashboard.badge_incomplete':'⚠ Incompleto',
    'dashboard.empty_clients':   'Sin clientes',
    'dashboard.empty_clients_sub':'Añade tu primer cliente para empezar',
    'dashboard.add_btn':         '➕ Añadir cliente',
    'dashboard.tip_detail':      'Ver detalle',
    'dashboard.tip_sync':        'Sincronizar repos',
    'dashboard.tip_vscode':      'Abrir VS Code',

    // Welcome / init
    'welcome.title':     'Bienvenido a MuleSoft Manager',
    'welcome.subtitle':  'Gestión normalizada de entornos MuleSoft para consultoras con múltiples clientes, distintas regiones de Anypoint y distintas plataformas de control de versiones.',
    'welcome.btn':       '🚀 Inicializar Workspace',
    'welcome.creates':   'Lo que se creará',
    'welcome.c1':        'Árbol de carpetas normalizado',
    'welcome.c2':        'Gestión de claves SSH',
    'welcome.c3':        'Git config aislado por cliente',
    'welcome.c4':        'Workspaces VS Code automáticos',
    'welcome.c5':        'Java + Maven configurados',
    'welcome.c6':        'Maven settings por región Mule',
    'modal.init_title':  'Inicializar Workspace',
    'modal.init_path':   'Ruta raíz del workspace',
    'modal.init_hint':   'Se creará la estructura de carpetas en esta ruta',
    'modal.init_btn':    '🚀 Inicializar',
    'modal.init_warn':   '⚠️ Asegúrate de tener Python 3.10+, Git para Windows y permisos de escritura en la ruta indicada.',

    // Clients
    'clients.title':         'Clientes',
    'clients.new_btn':       '➕ Nuevo cliente',
    'clients.search':        'Buscar cliente…',
    'clients.empty':         'Sin clientes',
    'clients.empty_sub':     'Añade tu primer cliente',
    'clients.add_btn':       '➕ Añadir',
    'clients.hint_title':    'Selecciona un cliente',
    'clients.hint_sub':      'Haz clic en un cliente de la lista para ver su detalle',
    'clients.tab_general':   'General',
    'clients.tab_repos':     'Repositorios',
    'clients.tab_config':    'Configuración',
    'clients.tab_anypoint':  'Anypoint',
    'clients.sync_btn':      '🔄 Sync',
    'clients.vscode_btn':    '🖥️ VS Code',
    'clients.badge_ready':   '✓ Configurado',
    'clients.badge_inc':     '⚠ Incompleto',
    'clients.vcs_card':      '🌐 VCS',
    'clients.anypoint_card': '☁️ Anypoint Platform',
    'clients.edit_vcs':      '✏️ Editar VCS',
    'clients.change_region': '🌍 Cambiar región',
    'clients.credentials':   '🔐 Credenciales',
    'clients.clone_pending': '🔄 Clonar pendientes',
    'clients.add_repo_btn':  '➕ Añadir repo',
    'clients.no_repos':      'Sin repositorios',
    'clients.no_repos_sub':  'Añade los repos de código de este cliente',
    'clients.config_files':  '📄 Archivos de configuración',
    'clients.paths_card':    '📁 Rutas',
    'clients.show_pubkey':   '🔑 Ver clave pública SSH',
    'clients.regen_key':     '🔐 Regenerar clave SSH',
    'clients.save_creds':    '💾 Guardar credenciales',
    'clients.anypoint_warn': '⚠️ Las credenciales se guardan en settings.xml local. No las subas a Git.',
    'clients.col_repo':      'Repositorio',
    'clients.col_branch':    'Rama',
    'clients.col_url':       'URL',
    'clients.col_status':    'Estado',
    'clients.cloned':        '✓ Clonado',
    'clients.pending':       '⬜ Pendiente',
    'clients.autofill_hint': 'Los campos en azul se sugieren al escribir el nombre',
    'clients.id_hint':       'Escribe el nombre y el resto se autocompleta',
    'clients.region_label':  'Región Anypoint',

    // Form new client
    'form.id':            'ID interno',
    'form.display':       'Nombre completo',
    'form.vcs_type':      'Tipo de VCS',
    'form.region':        'Región Mule',
    'form.host':          'Host del servidor',
    'form.username':      'Usuario git',
    'form.email':         'Email git',
    'form.org':           'Organización / namespace',
    'form.git_name':      'Nombre real (para commits)',
    'form.ap_user':       'Usuario Anypoint',
    'form.ap_pass':       'Password Anypoint',
    'form.aws_region':    'Región AWS',
    'form.cc_user':       'CodeCommit SSH User ID',
    'form.repo_name':     'Nombre del repositorio',
    'form.repo_url':      'URL SSH',
    'form.repo_url_hint': 'Opcional. Si está vacío se construye automáticamente usando el alias SSH.',
    'form.branch':        'Rama principal',
    'form.description':   'Descripción',
    'form.force_regen':   'Forzar regeneración (sobreescribir si ya existe)',

    // Modales clientes
    'modal.new_client':     'Nuevo cliente MuleSoft',
    'modal.create_btn':     '➕ Crear cliente',
    'modal.add_repo':       'Añadir repositorio',
    'modal.add_repo_btn':   'Añadir',
    'modal.pub_key':        'Clave pública SSH',
    'modal.gen_key':        'Generar clave SSH',
    'modal.gen_key_btn':    '🔐 Generar',
    'modal.info_ssh':       'Se generará automáticamente la clave SSH. Podrás añadir repositorios después desde la sección Clientes.',
    'modal.section_id':     'Identificación',
    'modal.section_vcs':    'Control de versiones (VCS)',
    'modal.section_ap':     'Credenciales Anypoint Platform (opcional)',

    // Tools
    'tools.title':         'Herramientas',
    'tools.install_all':   '⬇️ Instalar todo',
    'tools.check_btn':     '🔄 Verificar',
    'tools.installed':     '✓ Instalado',
    'tools.not_found':     '✗ No encontrado',
    'tools.install_btn':   '⬇️ Instalar (winget)',
    'tools.reinstall_btn': '🔄 Reinstalar',
    'tools.install_ext':   '🧩 Instalar extensiones',
    'tools.config_path':   '📁 Configurar ruta',
    'tools.download':      '⬇️ Descargar',
    'tools.log_title':     '📋 Log de instalación',
    'tools.log_clear':     'Limpiar',
    'tools.log_hint':      'Los mensajes de instalación aparecerán aquí…',
    'tools.java_path':     'Configurar ruta de Java',
    'tools.maven_path':    'Configurar ruta de Maven',
    'tools.java_home':     'JAVA_HOME',
    'tools.maven_home':    'MAVEN_HOME',
    'tools.java_hint':     'Ruta al directorio raíz del JDK instalado',
    'tools.maven_hint':    'Ruta al directorio raíz de Maven',

    // SSH
    'ssh.title':         'SSH / Git',
    'ssh.gen_key_btn':   '🔐 Generar clave SSH',
    'ssh.info_title':    'Cómo funciona el aislamiento SSH/Git',
    'ssh.info_text':     'Cada cliente tiene su propia clave SSH. El alias de host en ~/.ssh/config enruta cada repo al par de claves correcto. El ~/.gitconfig global usa includeIf para aplicar la identidad del cliente dentro de su carpeta de proyectos.',
    'ssh.keys_title':    '🔑 Claves SSH por cliente',
    'ssh.col_client':    'Cliente',
    'ssh.col_vcs':       'VCS',
    'ssh.col_key':       'Nombre de clave',
    'ssh.col_alias':     'SSH Alias',
    'ssh.col_priv':      'Clave privada',
    'ssh.col_pub':       'Clave pública',
    'ssh.col_actions':   'Acciones',
    'ssh.exists':        '✓ Existe',
    'ssh.missing':       '✗ Falta',
    'ssh.no_keys':       'Sin claves SSH',
    'ssh.no_keys_sub':   'Las claves SSH se generan automáticamente al añadir un cliente. También puedes generarlas manualmente.',
    'ssh.gen_first':     '🔐 Generar clave',
    'ssh.ssh_config':    '~/.ssh/config (estructura)',
    'ssh.git_config':    '~/.gitconfig (conditional includes)',
    'ssh.register':      '📋 Dónde registrar las claves públicas',
    'ssh.pub_key_title': 'Clave pública SSH',
    'ssh.pub_key_tip':   'Registra esta clave pública en tu proveedor VCS.',
    'ssh.regen_warn':    '¿Regenerar la clave SSH de "{name}"? La clave actual quedará invalidada en el proveedor VCS.',
    'ssh.algo_label':    'Algoritmo',
    'ssh.client_label':  'Cliente',
    'ssh.no_clients':    '(sin clientes configurados)',

    // Settings
    'settings.title':        'Ajustes globales',
    'settings.save_btn':     '💾 Guardar cambios',
    'settings.discard_btn':  '↺ Descartar',
    'settings.workspace':    'Workspace',
    'settings.ws_sub':       'Información del workspace activo',
    'settings.ws_path':      'Ruta raíz del workspace',
    'settings.ws_hint':      'Para cambiar la ruta, ejecuta mulesoft-manager init --path NUEVA_RUTA',
    'settings.java':         'Java JDK',
    'settings.java_sub':     'Configuración del Java Development Kit',
    'settings.maven':        'Apache Maven',
    'settings.maven_sub':    'Gestión de dependencias y build',
    'settings.vscode':       'Visual Studio Code',
    'settings.vscode_sub':   'Extensiones y configuración del IDE',
    'settings.ssh_sec':      'SSH',
    'settings.ssh_sub':      'Generación de claves SSH',
    'settings.git_sec':      'Git',
    'settings.git_sub':      'Configuración global de Git',
    'settings.ver_pref':     'Versión preferida',
    'settings.install_meth': 'Método de instalación',
    'settings.home_path':    'ruta manual',
    'settings.home_hint':    'Deja vacío para detección automática',
    'settings.extensions':   'Extensiones recomendadas',
    'settings.ext_hint':     'Selecciona las extensiones que se instalarán automáticamente',
    'settings.key_type':     'Tipo de clave predeterminado',
    'settings.key_hint':     'ed25519 es más seguro y compacto',
    'settings.rsa_bits':     'Bits RSA (solo RSA)',
    'settings.default_branch': 'Rama por defecto',
    'settings.autocrlf':     'autocrlf',
    'settings.autocrlf_hint':'Recomendado: false para proyectos MuleSoft',
    'settings.save_all_btn': '💾 Guardar todos los cambios',
    'settings.discard_all':  '↺ Descartar cambios',
    'settings.dirty_warn':   'Hay cambios sin guardar.',
  },

  /* ── ENGLISH ──────────────────────────────────────────────── */
  en: {
    // Sidebar
    'sidebar.main':          'Main',
    'sidebar.config':        'Configuration',
    'sidebar.cli':           'Windows · Python CLI',
    'nav.dashboard':         'Dashboard',
    'nav.clients':           'Clients',
    'nav.tools':             'Tools',
    'nav.ssh':               'SSH / Git',
    'nav.settings':          'Settings',

    // Common
    'common.cancel':         'Cancel',
    'common.confirm':        'Confirm',
    'common.save':           'Save',
    'common.delete':         'Delete',
    'common.add':            'Add',
    'common.close':          'Close',
    'common.copy':           '📋 Copy',
    'common.loading':        'Loading…',
    'common.yes':            'Yes',
    'common.no':             'No',
    'common.optional':       'optional',
    'common.suggested':      'suggested',
    'common.exists':         '✓ Exists',
    'common.missing':        '✗ Missing',
    'common.rebuild':        '🔄 Rebuild all',
    'common.open_explorer':  '📂 Open in Explorer',
    'common.copy_path':      '📋 Copy path',
    'common.see_all':        'See all →',
    'common.discard':        '↺ Discard',
    'common.save_all':       '💾 Save all changes',

    // Confirm modal
    'modal.confirm_title':   'Confirm action',
    'modal.confirm_btn':     'Confirm',

    // Dashboard
    'dashboard.title':           'Dashboard',
    'dashboard.workspace_chip':  'Workspace active',
    'dashboard.new_client_btn':  '＋ New client',
    'dashboard.stat_clients':    'Configured clients',
    'dashboard.stat_repos':      'Cloned repos',
    'dashboard.stat_tools':      'Installed tools',
    'dashboard.stat_add':        'New client',
    'dashboard.stat_add_sub':    'Add configuration',
    'dashboard.card_clients':    'Clients',
    'dashboard.quick_actions':   '⚡ Quick actions',
    'dashboard.btn_manage':      '👥 Manage clients',
    'dashboard.btn_tools':       '🔧 Tools',
    'dashboard.btn_ssh':         '🔑 SSH / Git',
    'dashboard.tools_card':      '🔧 Tools',
    'dashboard.col_client':      'Client',
    'dashboard.col_vcs':         'VCS',
    'dashboard.col_region':      'Region',
    'dashboard.col_repos':       'Repos',
    'dashboard.col_status':      'Status',
    'dashboard.badge_ready':     '✓ Ready',
    'dashboard.badge_incomplete':'⚠ Incomplete',
    'dashboard.empty_clients':   'No clients',
    'dashboard.empty_clients_sub':'Add your first client to get started',
    'dashboard.add_btn':         '➕ Add client',
    'dashboard.tip_detail':      'View detail',
    'dashboard.tip_sync':        'Sync repos',
    'dashboard.tip_vscode':      'Open VS Code',

    // Welcome / init
    'welcome.title':     'Welcome to MuleSoft Manager',
    'welcome.subtitle':  'Normalized MuleSoft environment management for consulting firms with multiple clients, different Anypoint regions and different version control platforms.',
    'welcome.btn':       '🚀 Initialize Workspace',
    'welcome.creates':   'What will be created',
    'welcome.c1':        'Normalized folder tree',
    'welcome.c2':        'SSH key management',
    'welcome.c3':        'Isolated Git config per client',
    'welcome.c4':        'Automatic VS Code workspaces',
    'welcome.c5':        'Java + Maven configured',
    'welcome.c6':        'Maven settings per Mule region',
    'modal.init_title':  'Initialize Workspace',
    'modal.init_path':   'Workspace root path',
    'modal.init_hint':   'The folder structure will be created at this path',
    'modal.init_btn':    '🚀 Initialize',
    'modal.init_warn':   '⚠️ Make sure you have Python 3.10+, Git for Windows and write permissions at the specified path.',

    // Clients
    'clients.title':         'Clients',
    'clients.new_btn':       '➕ New client',
    'clients.search':        'Search client…',
    'clients.empty':         'No clients',
    'clients.empty_sub':     'Add your first client',
    'clients.add_btn':       '➕ Add',
    'clients.hint_title':    'Select a client',
    'clients.hint_sub':      'Click a client in the list to see its details',
    'clients.tab_general':   'General',
    'clients.tab_repos':     'Repositories',
    'clients.tab_config':    'Configuration',
    'clients.tab_anypoint':  'Anypoint',
    'clients.sync_btn':      '🔄 Sync',
    'clients.vscode_btn':    '🖥️ VS Code',
    'clients.badge_ready':   '✓ Configured',
    'clients.badge_inc':     '⚠ Incomplete',
    'clients.vcs_card':      '🌐 VCS',
    'clients.anypoint_card': '☁️ Anypoint Platform',
    'clients.edit_vcs':      '✏️ Edit VCS',
    'clients.change_region': '🌍 Change region',
    'clients.credentials':   '🔐 Credentials',
    'clients.clone_pending': '🔄 Clone pending',
    'clients.add_repo_btn':  '➕ Add repo',
    'clients.no_repos':      'No repositories',
    'clients.no_repos_sub':  'Add the code repositories for this client',
    'clients.config_files':  '📄 Configuration files',
    'clients.paths_card':    '📁 Paths',
    'clients.show_pubkey':   '🔑 Show SSH public key',
    'clients.regen_key':     '🔐 Regenerate SSH key',
    'clients.save_creds':    '💾 Save credentials',
    'clients.anypoint_warn': '⚠️ Credentials are stored in local settings.xml. Do not push to Git.',
    'clients.col_repo':      'Repository',
    'clients.col_branch':    'Branch',
    'clients.col_url':       'URL',
    'clients.col_status':    'Status',
    'clients.cloned':        '✓ Cloned',
    'clients.pending':       '⬜ Pending',
    'clients.autofill_hint': 'Blue fields are auto-suggested as you type the name',
    'clients.id_hint':       'Type the name and the rest will be autocompleted',
    'clients.region_label':  'Anypoint region',

    // Form new client
    'form.id':            'Internal ID',
    'form.display':       'Full name',
    'form.vcs_type':      'VCS type',
    'form.region':        'Mule region',
    'form.host':          'Server host',
    'form.username':      'Git username',
    'form.email':         'Git email',
    'form.org':           'Organization / namespace',
    'form.git_name':      'Real name (for commits)',
    'form.ap_user':       'Anypoint user',
    'form.ap_pass':       'Anypoint password',
    'form.aws_region':    'AWS region',
    'form.cc_user':       'CodeCommit SSH User ID',
    'form.repo_name':     'Repository name',
    'form.repo_url':      'SSH URL',
    'form.repo_url_hint': 'Optional. If empty it is built automatically using the SSH alias.',
    'form.branch':        'Main branch',
    'form.description':   'Description',
    'form.force_regen':   'Force regeneration (overwrite if already exists)',

    // Client modals
    'modal.new_client':  'New MuleSoft client',
    'modal.create_btn':  '➕ Create client',
    'modal.add_repo':    'Add repository',
    'modal.add_repo_btn':'Add',
    'modal.pub_key':     'SSH public key',
    'modal.gen_key':     'Generate SSH key',
    'modal.gen_key_btn': '🔐 Generate',
    'modal.info_ssh':    'SSH key will be generated automatically. You can add repositories later from the Clients section.',
    'modal.section_id':  'Identification',
    'modal.section_vcs': 'Version control (VCS)',
    'modal.section_ap':  'Anypoint Platform credentials (optional)',

    // Tools
    'tools.title':         'Tools',
    'tools.install_all':   '⬇️ Install all',
    'tools.check_btn':     '🔄 Check',
    'tools.installed':     '✓ Installed',
    'tools.not_found':     '✗ Not found',
    'tools.install_btn':   '⬇️ Install (winget)',
    'tools.reinstall_btn': '🔄 Reinstall',
    'tools.install_ext':   '🧩 Install extensions',
    'tools.config_path':   '📁 Configure path',
    'tools.download':      '⬇️ Download',
    'tools.log_title':     '📋 Installation log',
    'tools.log_clear':     'Clear',
    'tools.log_hint':      'Installation messages will appear here…',
    'tools.java_path':     'Configure Java path',
    'tools.maven_path':    'Configure Maven path',
    'tools.java_home':     'JAVA_HOME',
    'tools.maven_home':    'MAVEN_HOME',
    'tools.java_hint':     'Path to the installed JDK root directory',
    'tools.maven_hint':    'Path to the Maven root directory',

    // SSH
    'ssh.title':         'SSH / Git',
    'ssh.gen_key_btn':   '🔐 Generate SSH key',
    'ssh.info_title':    'How SSH/Git isolation works',
    'ssh.info_text':     'Each client has its own SSH key. The host alias in ~/.ssh/config routes each repo to the correct key pair. The global ~/.gitconfig uses includeIf to apply the client identity inside its project folder.',
    'ssh.keys_title':    '🔑 SSH Keys per client',
    'ssh.col_client':    'Client',
    'ssh.col_vcs':       'VCS',
    'ssh.col_key':       'Key name',
    'ssh.col_alias':     'SSH Alias',
    'ssh.col_priv':      'Private key',
    'ssh.col_pub':       'Public key',
    'ssh.col_actions':   'Actions',
    'ssh.exists':        '✓ Exists',
    'ssh.missing':       '✗ Missing',
    'ssh.no_keys':       'No SSH keys',
    'ssh.no_keys_sub':   'SSH keys are automatically generated when adding a client. You can also generate them manually.',
    'ssh.gen_first':     '🔐 Generate key',
    'ssh.ssh_config':    '~/.ssh/config (structure)',
    'ssh.git_config':    '~/.gitconfig (conditional includes)',
    'ssh.register':      '📋 Where to register public keys',
    'ssh.pub_key_title': 'SSH public key',
    'ssh.pub_key_tip':   'Register this public key with your VCS provider.',
    'ssh.regen_warn':    'Regenerate SSH key for "{name}"? The current key will be invalidated on the VCS provider.',
    'ssh.algo_label':    'Algorithm',
    'ssh.client_label':  'Client',
    'ssh.no_clients':    '(no clients configured)',

    // Settings
    'settings.title':        'Global settings',
    'settings.save_btn':     '💾 Save changes',
    'settings.discard_btn':  '↺ Discard',
    'settings.workspace':    'Workspace',
    'settings.ws_sub':       'Active workspace information',
    'settings.ws_path':      'Workspace root path',
    'settings.ws_hint':      'To change the path, run mulesoft-manager init --path NEW_PATH',
    'settings.java':         'Java JDK',
    'settings.java_sub':     'Java Development Kit configuration',
    'settings.maven':        'Apache Maven',
    'settings.maven_sub':    'Dependency management and build',
    'settings.vscode':       'Visual Studio Code',
    'settings.vscode_sub':   'Extensions and IDE configuration',
    'settings.ssh_sec':      'SSH',
    'settings.ssh_sub':      'SSH key generation',
    'settings.git_sec':      'Git',
    'settings.git_sub':      'Global Git configuration',
    'settings.ver_pref':     'Preferred version',
    'settings.install_meth': 'Installation method',
    'settings.home_path':    'manual path',
    'settings.home_hint':    'Leave empty for automatic detection',
    'settings.extensions':   'Recommended extensions',
    'settings.ext_hint':     'Select the extensions that will be installed automatically',
    'settings.key_type':     'Default key type',
    'settings.key_hint':     'ed25519 is more secure and compact',
    'settings.rsa_bits':     'RSA bits (RSA only)',
    'settings.default_branch':'Default branch',
    'settings.autocrlf':     'autocrlf',
    'settings.autocrlf_hint':'Recommended: false for MuleSoft projects',
    'settings.save_all_btn': '💾 Save all changes',
    'settings.discard_all':  '↺ Discard changes',
    'settings.dirty_warn':   'You have unsaved changes.',
  },
};

/* ============================================================
   MOTOR DE TRADUCCIÓN
   ============================================================ */

/** Idioma activo (persiste en localStorage) */
let _lang = localStorage.getItem('mulesoft-lang') || 'es';

/**
 * Devuelve la traducción para una clave.
 * Si no existe, devuelve el fallback o la propia clave.
 */
function t(key, fallback) {
  return (TRANSLATIONS[_lang] || {})[key]
      || (TRANSLATIONS['es'] || {})[key]
      || fallback
      || key;
}

/** Aplica data-i18n y data-i18n-placeholder a todos los elementos del DOM */
function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const val = t(el.dataset.i18n);
    if (val !== el.dataset.i18n) el.textContent = val;
  });
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    const val = t(el.dataset.i18nHtml);
    if (val !== el.dataset.i18nHtml) el.innerHTML = val;
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
    const val = t(el.dataset.i18nPlaceholder);
    if (val !== el.dataset.i18nPlaceholder) el.placeholder = val;
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    const val = t(el.dataset.i18nTitle);
    if (val !== el.dataset.i18nTitle) el.title = val;
  });
  // Actualizar el botón toggle
  _updateLangBtn();
}

/** Cambia el idioma activo y aplica traducciones */
function setLang(lang) {
  _lang = lang;
  localStorage.setItem('mulesoft-lang', lang);
  applyTranslations();
  // Disparar evento por si algún componente necesita reaccionar
  document.dispatchEvent(new CustomEvent('langchange', { detail: { lang } }));
}

/** Devuelve el idioma activo */
function getLang() { return _lang; }

/** Actualiza el aspecto del botón toggle */
function _updateLangBtn() {
  const btn = document.getElementById('lang-toggle-btn');
  if (!btn) return;
  btn.textContent = _lang === 'es' ? '🌐 EN' : '🌐 ES';
  btn.title = _lang === 'es' ? 'Switch to English' : 'Cambiar a Español';
}

/* Aplicar traducciones al cargar el DOM */
document.addEventListener('DOMContentLoaded', applyTranslations);

"""
Draft manual test checklist, written from current SEIM features. Seeded with
``manage.py seed_test_scenarios`` (idempotent; edit here or in Django admin).

Each entry: code, area, role, route_name, en title/steps/expected, es title/steps/expected.
"""

S = []


def add(
    code, area, role, route, title, steps, expected, title_es, steps_es, expected_es
):
    S.append(
        {
            "code": code,
            "area": area,
            "role": role,
            "route_name": route,
            "title": title,
            "steps": steps,
            "expected": expected,
            "title_es": title_es,
            "steps_es": steps_es,
            "expected_es": expected_es,
        }
    )


# --- Accounts & access ---------------------------------------------------------
add(
    "AUTH-01",
    "Accounts",
    "",
    "Login",
    "Sign in and sign out",
    "Sign in with your tester account. Sign out from the user menu.",
    "Dashboard loads after sign-in; sign-out returns to the login page.",
    "Iniciar y cerrar sesión",
    "Inicia sesión con tu cuenta de tester. Cierra sesión desde el menú de usuario.",
    "El tablero carga al iniciar sesión; al cerrar sesión vuelves al inicio de sesión.",
)
add(
    "AUTH-02",
    "Accounts",
    "",
    "Register",
    "Register a new student",
    "Sign out. Register with a new address (e.g. yourname+1@…). Open the verification email in the tester Outbox and follow the link.",
    "Account is created inactive, the verification email arrives in the Outbox, and the link activates the account.",
    "Registrar un estudiante nuevo",
    "Cierra sesión. Regístrate con un correo nuevo. Abre el correo de verificación en la Bandeja de correos y sigue el enlace.",
    "La cuenta se crea inactiva, el correo llega a la Bandeja y el enlace activa la cuenta.",
)
add(
    "AUTH-03",
    "Accounts",
    "",
    "PasswordReset",
    "Password reset email",
    "Request a password reset for a demo student. Open the email in the Outbox.",
    "Reset email is captured; the link opens the reset form. (Do not change demo passwords.)",
    "Correo para restablecer contraseña",
    "Solicita restablecer la contraseña de un estudiante demo. Abre el correo en la Bandeja.",
    "El correo se captura y el enlace abre el formulario. (No cambies contraseñas demo.)",
)
add(
    "AUTH-04",
    "Accounts",
    "",
    "Settings",
    "Language switch (English / Spanish)",
    "Switch the interface language in Settings or the top bar. Visit several pages.",
    "All visible text changes language; no raw translation keys (like qa.menu.label) appear.",
    "Cambio de idioma (inglés / español)",
    "Cambia el idioma en Configuración o en la barra superior. Recorre varias páginas.",
    "Todo el texto cambia de idioma; no aparecen claves sin traducir.",
)
add(
    "AUTH-05",
    "Accounts",
    "student",
    "Profile",
    "Complete the student profile",
    "As student.new@test.com, open Profile and fill in the required fields. Save.",
    "Profile saves; the dashboard shows the account as ready to apply.",
    "Completar el perfil del estudiante",
    "Como student.new@test.com, abre Perfil y llena los campos obligatorios. Guarda.",
    "El perfil se guarda; el tablero indica que la cuenta puede postularse.",
)

# --- Student -------------------------------------------------------------------
add(
    "STU-01",
    "Student",
    "student",
    "Dashboard",
    "Student dashboard overview",
    "As student@test.com open the dashboard.",
    "Applications, deadlines and notifications widgets load without errors.",
    "Tablero del estudiante",
    "Como student@test.com abre el tablero.",
    "Cargan las solicitudes, fechas límite y notificaciones sin errores.",
)
add(
    "STU-02",
    "Student",
    "student",
    "ProgramCompare",
    "Browse and compare programs",
    "Open programs, filter by country/term, add 2–3 programs to compare.",
    "Filters work; the comparison shows eligibility, deadlines and destinations side by side.",
    "Explorar y comparar programas",
    "Abre programas, filtra por país/periodo y agrega 2–3 programas a comparar.",
    "Los filtros funcionan; la comparación muestra elegibilidad, fechas y destinos.",
)
add(
    "STU-03",
    "Student",
    "student",
    "ApplicationNew",
    "Start and save an application draft",
    "Start a new application for an open program. Fill part of the form and save as draft. Leave and come back.",
    "Draft is saved and can be resumed with the entered data.",
    "Iniciar y guardar un borrador de solicitud",
    "Inicia una solicitud para un programa abierto. Llena parte del formulario y guarda el borrador. Sal y regresa.",
    "El borrador se guarda y se puede retomar con los datos capturados.",
)
add(
    "STU-04",
    "Student",
    "student",
    "ApplicationEdit",
    "Submit an application",
    "Complete the application, upload required documents (use the sample PDF from the Tester hub) and submit.",
    "Submission succeeds; status becomes Submitted; a confirmation notification/email appears.",
    "Enviar una solicitud",
    "Completa la solicitud, sube los documentos requeridos (usa el PDF de ejemplo del Centro de pruebas) y envía.",
    "El envío funciona; el estado cambia a Enviada; aparece una notificación/correo de confirmación.",
)
add(
    "STU-05",
    "Student",
    "student",
    "ApplicationNew",
    "Eligibility blocks ineligible students",
    "Try to apply to a program whose eligibility rules you do not meet (e.g. GPA/language).",
    "A clear message explains why you cannot apply; nothing is submitted.",
    "La elegibilidad bloquea a estudiantes no elegibles",
    "Intenta postularte a un programa cuyos requisitos no cumples (p. ej. promedio/idioma).",
    "Un mensaje claro explica por qué no puedes postularte; no se envía nada.",
)
add(
    "STU-06",
    "Documents",
    "student",
    "Documents",
    "Upload, replace and delete documents",
    "Upload the sample PDF and image. Replace one. Try an unsupported file type.",
    "Valid files upload with progress; unsupported/oversized files are rejected with a message.",
    "Subir, reemplazar y eliminar documentos",
    "Sube el PDF y la imagen de ejemplo. Reemplaza uno. Intenta un tipo de archivo no permitido.",
    "Los archivos válidos se suben; los no permitidos o muy grandes se rechazan con un mensaje.",
)
add(
    "STU-07",
    "Student",
    "student",
    "ApplicationDetail",
    "Application timeline and comments",
    "As student.review@test.com open an application under review. Read the timeline and add a comment.",
    "Timeline shows status history; the comment is posted and visible to staff.",
    "Línea de tiempo y comentarios de la solicitud",
    "Como student.review@test.com abre una solicitud en revisión. Revisa la línea de tiempo y agrega un comentario.",
    "La línea de tiempo muestra el historial; el comentario se publica y lo ve el personal.",
)
add(
    "STU-08",
    "Student",
    "student",
    "ApplicationDetail",
    "Withdraw an application",
    "Withdraw a submitted application.",
    "You are asked to confirm; status becomes Cancelled/Withdrawn and staff see it.",
    "Retirar una solicitud",
    "Retira una solicitud enviada.",
    "Se pide confirmación; el estado cambia a Cancelada/Retirada y el personal lo ve.",
)
add(
    "STU-09",
    "Student",
    "student",
    "DeadlinesCalendar",
    "Deadlines calendar",
    "Open the deadlines calendar and switch months.",
    "Program deadlines appear on the correct dates in your time zone.",
    "Calendario de fechas límite",
    "Abre el calendario y cambia de mes.",
    "Las fechas límite aparecen en el día correcto según tu zona horaria.",
)
add(
    "STU-10",
    "Student",
    "student",
    "ToeflPractice",
    "TOEFL practice history",
    "Open TOEFL practice. Review previous attempts.",
    "History loads; launching works when the sidecar is available or shows a friendly message otherwise.",
    "Historial de práctica TOEFL",
    "Abre la práctica TOEFL y revisa intentos anteriores.",
    "El historial carga; el inicio funciona si el servicio está disponible o muestra un mensaje claro.",
)
add(
    "STU-11",
    "Student",
    "student",
    "Notifications",
    "Notifications center",
    "Open notifications, mark one as read, mark all as read.",
    "Unread count updates in the top bar; links open the related page.",
    "Centro de notificaciones",
    "Abre notificaciones, marca una como leída y luego todas.",
    "El contador se actualiza; los enlaces abren la página relacionada.",
)

# --- Coordinator ---------------------------------------------------------------
add(
    "COO-01",
    "Coordinator",
    "coordinator",
    "CoordinatorReviewQueue",
    "Review queue filters and navigation",
    "As coordinator@test.com open the review queue. Filter by program/status. Open an application and use next/previous.",
    "Filters apply; next/previous moves through the filtered list.",
    "Cola de revisión: filtros y navegación",
    "Como coordinator@test.com abre la cola de revisión. Filtra por programa/estado. Abre una solicitud y usa siguiente/anterior.",
    "Los filtros se aplican; siguiente/anterior recorre la lista filtrada.",
)
add(
    "COO-02",
    "Coordinator",
    "coordinator",
    "ApplicationDetail",
    "Approve / reject an application",
    "Move an application through review to approved; reject another with a reason.",
    "Statuses change according to the workflow; the student gets a notification and email (Outbox).",
    "Aprobar / rechazar una solicitud",
    "Lleva una solicitud de revisión a aprobada; rechaza otra con un motivo.",
    "Los estados cambian según el flujo; el estudiante recibe notificación y correo (Bandeja).",
)
add(
    "COO-03",
    "Documents",
    "coordinator",
    "DocumentDetail",
    "Review documents",
    "Open a student document, preview it, approve one and request a resubmission for another.",
    "Preview works; status changes are visible to the student.",
    "Revisar documentos",
    "Abre un documento, revisa la vista previa, aprueba uno y solicita reenvío de otro.",
    "La vista previa funciona; los cambios de estado los ve el estudiante.",
)
add(
    "COO-04",
    "Coordinator",
    "coordinator",
    "Nominations",
    "Nominations and allocations",
    "Open nominations. Allocate a student to a destination and nominate.",
    "Allocation saves; nominated student appears in the partner portal for acknowledgement.",
    "Nominaciones y asignaciones",
    "Abre nominaciones. Asigna un estudiante a un destino y nomínalo.",
    "La asignación se guarda; el estudiante aparece en el portal del socio.",
)
add(
    "COO-05",
    "Coordinator",
    "coordinator",
    "CoordinatorWorkload",
    "Workload dashboard",
    "Open the workload view.",
    "Counts per coordinator/status match the review queue.",
    "Panel de carga de trabajo",
    "Abre la vista de carga de trabajo.",
    "Los conteos por coordinador/estado coinciden con la cola de revisión.",
)
add(
    "COO-06",
    "Coordinator",
    "coordinator",
    "StaffExchangeAgreements",
    "Exchange agreements and documents",
    "Open exchange agreements, view one, upload an agreement document (sample PDF).",
    "Agreement details load; the document is attached and downloadable.",
    "Convenios de intercambio y documentos",
    "Abre convenios, revisa uno y sube un documento de convenio (PDF de ejemplo).",
    "Los detalles cargan; el documento queda adjunto y se puede descargar.",
)
add(
    "COO-07",
    "Coordinator",
    "coordinator",
    "AnalyticsForecasts",
    "Analytics and forecasts",
    "Open analytics. Change filters and export if available.",
    "Charts render with demo data; exports download.",
    "Analítica y pronósticos",
    "Abre analítica. Cambia filtros y exporta si está disponible.",
    "Las gráficas muestran datos demo; las exportaciones se descargan.",
)

# --- Partner -------------------------------------------------------------------
add(
    "PAR-01",
    "Partner",
    "partner",
    "PartnerPortal",
    "Partner portal acknowledgement",
    "As partner@test.com open the partner portal and acknowledge student.nominated@test.com.",
    "Acknowledgement saves; the coordinator sees the updated nomination.",
    "Portal del socio: confirmar nominación",
    "Como partner@test.com abre el portal y confirma a student.nominated@test.com.",
    "La confirmación se guarda; el coordinador ve la nominación actualizada.",
)
add(
    "PAR-02",
    "Partner",
    "partner",
    "PartnerPortal",
    "Partner sees only own students",
    "Browse the partner portal lists.",
    "Only students nominated to this partner are visible.",
    "El socio solo ve a sus estudiantes",
    "Recorre las listas del portal.",
    "Solo aparecen los estudiantes nominados a este socio.",
)

# --- Admin ---------------------------------------------------------------------
add(
    "ADM-01",
    "Admin",
    "admin",
    "AdminPrograms",
    "Create and edit a program",
    "As admin@test.com create a program with destinations, deadlines and eligibility. Edit it.",
    "Program saves and appears for students when open.",
    "Crear y editar un programa",
    "Como admin@test.com crea un programa con destinos, fechas y elegibilidad. Edítalo.",
    "El programa se guarda y aparece para estudiantes cuando está abierto.",
)
add(
    "ADM-02",
    "Admin",
    "admin",
    "AdminUsers",
    "Manage users and roles",
    "Search users, change a demo student's role, deactivate and reactivate.",
    "Changes save; the user's access changes accordingly.",
    "Administrar usuarios y roles",
    "Busca usuarios, cambia el rol de un estudiante demo, desactívalo y reactívalo.",
    "Los cambios se guardan y el acceso del usuario cambia.",
)
add(
    "ADM-03",
    "Admin",
    "admin",
    "AdminWorkflows",
    "Workflow editor",
    "Open a workflow, view the states/transitions, make a small change and save.",
    "Editor loads; saved changes apply to new applications.",
    "Editor de flujos",
    "Abre un flujo, revisa estados/transiciones, haz un cambio pequeño y guarda.",
    "El editor carga; los cambios aplican a nuevas solicitudes.",
)
add(
    "ADM-04",
    "Admin",
    "admin",
    "AdminDynformEditor",
    "Dynamic form builder",
    "Create a form with text, choice and file fields. Attach it to a program and fill it as a student.",
    "Form renders for the student and answers are stored.",
    "Constructor de formularios dinámicos",
    "Crea un formulario con campos de texto, opción y archivo. Asígnalo a un programa y llénalo como estudiante.",
    "El formulario se muestra al estudiante y las respuestas se guardan.",
)
add(
    "ADM-05",
    "Admin",
    "admin",
    "AdminDocuments",
    "Document types",
    "Create a document type with allowed formats and size; require it on a program.",
    "Students are asked for it; restrictions are enforced on upload.",
    "Tipos de documento",
    "Crea un tipo de documento con formatos y tamaño permitidos; hazlo obligatorio en un programa.",
    "Se solicita a los estudiantes y las restricciones se aplican al subir.",
)
add(
    "ADM-06",
    "Admin",
    "admin",
    "AdminFeatures",
    "Feature toggles",
    "Turn an institution feature (e.g. scholarships) off and on.",
    "Related menus/pages hide and reappear; the Tester hub flags reflect the change.",
    "Activar/desactivar funciones",
    "Desactiva y activa una función de la institución (p. ej. becas).",
    "Los menús/páginas relacionados se ocultan y reaparecen; el Centro de pruebas lo refleja.",
)
add(
    "ADM-07",
    "Admin",
    "admin",
    "AdminDataManagement",
    "Data management exports",
    "Run an export from data management.",
    "Export completes and downloads; logs show the action.",
    "Exportaciones de gestión de datos",
    "Ejecuta una exportación desde gestión de datos.",
    "La exportación termina y se descarga; la bitácora registra la acción.",
)
add(
    "ADM-08",
    "Admin",
    "admin",
    "ScholarshipScoringRulesets",
    "Scholarship scoring",
    "Open scholarship scoring rulesets, adjust a weight and preview ranking.",
    "Ranking updates according to the new weights.",
    "Puntaje de becas",
    "Abre las reglas de puntaje, ajusta un peso y revisa el ranking.",
    "El ranking cambia según los nuevos pesos.",
)

# --- Cross-cutting -------------------------------------------------------------
add(
    "X-01",
    "General",
    "",
    "HelpCenter",
    "Help center",
    "Open Help, search for an article and open it.",
    "Search returns relevant articles; articles render in your language.",
    "Centro de ayuda",
    "Abre Ayuda, busca un artículo y ábrelo.",
    "La búsqueda devuelve artículos relevantes en tu idioma.",
)
add(
    "X-02",
    "General",
    "",
    "Dashboard",
    "Mobile layout",
    "Use a phone (or narrow the browser to ~375 px). Navigate main pages and open menus.",
    "Layout adapts; nothing is cut off; menus and dialogs are usable.",
    "Vista en móvil",
    "Usa un teléfono (o reduce el navegador a ~375 px). Navega y abre menús.",
    "El diseño se adapta; nada se corta; menús y diálogos son usables.",
)
add(
    "X-03",
    "General",
    "",
    "Dashboard",
    "Keyboard and accessibility basics",
    "Navigate a form using only the keyboard (Tab/Shift+Tab/Enter). Try the skip link.",
    "Focus is visible and logical; all actions are reachable by keyboard.",
    "Teclado y accesibilidad básica",
    "Navega un formulario solo con teclado (Tab/Shift+Tab/Enter). Prueba el enlace para saltar al contenido.",
    "El foco es visible y lógico; todas las acciones son accesibles con teclado.",
)
add(
    "X-04",
    "General",
    "",
    "Dashboard",
    "Dark mode / display preferences",
    "Change theme and display preferences in Settings.",
    "Preferences apply immediately and persist after sign-out/sign-in.",
    "Modo oscuro / preferencias de visualización",
    "Cambia el tema y preferencias en Configuración.",
    "Se aplican de inmediato y se conservan al volver a iniciar sesión.",
)
add(
    "X-05",
    "Tester toolkit",
    "",
    "TesterAccounts",
    "Role switcher round trip",
    "Switch into each demo role from Test accounts and return to your account.",
    "Banner shows the acting account; Return restores your own session every time.",
    "Cambio de rol ida y vuelta",
    "Cambia a cada rol demo desde Cuentas de prueba y vuelve a tu cuenta.",
    "El aviso muestra la cuenta activa; Volver restaura tu sesión siempre.",
)
add(
    "X-06",
    "Tester toolkit",
    "",
    "TesterReports",
    "Report an issue with a screenshot",
    "Report a test issue with a captured, annotated screenshot.",
    "The report appears in My reports with the annotated image and diagnostics.",
    "Reportar un problema con captura",
    "Envía un reporte de prueba con una captura anotada.",
    "El reporte aparece en Mis reportes con la imagen anotada y el diagnóstico.",
)

SCENARIOS = S

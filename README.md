# Proyecto Unidad 3 – Portal de Anime (Django)

Este proyecto fue desarrollado como parte del proyecto final de la materia de desarrollo web profesional.  
Se trata de una **aplicacion web de animes** donde los usuarios pueden registrarse, iniciar sesión, recuperar contraseñas y navegar por distintos animes y episodios.  
Incluye integración de seguridad con **Google ReCAPTCHA**, gestión de perfiles y secciones de contacto y ayuda.

---

## ✨ Funcionalidades principales
- Registro e inicio de sesión de usuarios.
- Recuperación de contraseñas con flujo completo (reset + confirmación).
- Validación de formularios con **Google ReCAPTCHA**.
- Vista de detalle de **animes y episodios** con imágenes.
- Sistema de perfiles de usuario.
- Páginas adicionales: ayuda, contacto, chat.
- Gestión de archivos multimedia (imágenes de animes y videos).

---

## ⚙️ Tecnologías utilizadas
- **Backend:** Django, Python
- **Base de datos:** SQLite  
- **Frontend:** HTML5, CSS3, JavaScript, plantillas de Django  
- **Seguridad:** ReCAPTCHA, validaciones de formularios, sesiones de Django  
- **Control de versiones:** Git / GitHub  

---

## 📂 Estructura del proyecto
obregonmorinadrianjesusUnidad3/
├── config/                 # Configuración del proyecto (settings, urls, wsgi, asgi)
├── main/                   # App principal
│   ├── admin.py            # Registro en panel de administración
│   ├── apps.py
│   ├── forms.py            # Formularios con validaciones
│   ├── models.py           # Modelos de datos
│   ├── urls.py             # Rutas del proyecto
│   ├── views.py            # Controladores de vistas
│   ├── templates/          # Plantillas HTML (login, signup, profile, anime, episodios, etc.)
│   ├── templatetags/       # Filtros personalizados (form_filters.py)
│   └── utils/recaptcha.py  # Integración de Google ReCAPTCHA
├── media/                  # Archivos multimedia (imágenes de animes y episodios)
├── db.sqlite3              # Base de datos local
└── manage.py               # Script principal de Django

## 📌 Estado del proyecto
Este sistema fue creado como proyecto académico en la UTC.
Características de valor profesional:
- Autenticación segura
- Validación de formularios
- Gestión de multimedia
- Arquitectura MTV de Django

👤 Autor
**Adrián Obregón**

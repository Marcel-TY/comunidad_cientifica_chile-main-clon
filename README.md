# Comunidad Científica Chile

Portal del proyecto BSM de Vinculación con el Medio de IPCHILE, desarrollado con metodología A+S. Esta versión conserva el portal Django existente y agrega un catálogo científico Angular para proyectos, investigadores y publicaciones, administrado y persistido por Django y PostgreSQL.

## Requerimientos considerados

La pauta de evaluación compartida fue usada como fuente para estas mejoras. No se adjuntaron actas ni acuerdos de las reuniones con el centro, por lo que la tabla recoge una propuesta de adaptación y debe contrastarse con esas observaciones antes de afirmar que representa acuerdos textuales del socio.

| Mejora propuesta | Necesidad que atiende | Implementación |
|---|---|---|
| Catálogo de proyectos con área, estado, resumen y equipo | Presentar líneas y avances de investigación | `research.ResearchProject` y componente Angular de proyecto |
| Directorio de investigadores con institución y especialidad | Identificar capacidades y facilitar colaboración | `research.Researcher` y componente Angular de investigador |
| Registro de publicaciones relacionado con autores y proyectos | Mostrar producción científica y su contexto | `research.ScientificPublication` y componente Angular de publicación |
| Selección de proyecto para filtrar su equipo y destacar publicaciones | Hacer la información navegable e interactiva | `@Input`, interpolación, property/event binding y estado local en Angular |
| Administración y persistencia en PostgreSQL | Mantener datos modificables y disponibles entre ejecuciones | Django ORM, administración y PostgreSQL como motor predeterminado |

## Arquitectura

- **Angular** (`frontend/`): aplicación standalone y componentes reutilizables con TypeScript, HTML y CSS separados.
- **Django** (`comunidad_cientifica/`): configuración del sitio, rutas, vistas, aplicación `accounts` existente y nueva aplicación `research`.
- **PostgreSQL**: base predeterminada del proyecto, configurable mediante variables de entorno.
- **Integración del catálogo**: la ruta Django `/investigacion/` consulta los modelos mediante el ORM, prepara el contexto y lo serializa en la página con `json_script`. Angular consume ese contexto y presenta los datos. No se necesita una API REST para este flujo.

### Modelos y relaciones

- `ResearchProject`: proyecto, estado, área, fechas, financiamiento y relación muchos-a-muchos con investigadores.
- `Researcher`: nombre, institución, especialidad, biografía y ORCID.
- `ScientificPublication`: publicación, revista, fecha, DOI/enlace, relación opcional con un proyecto y relación muchos-a-muchos con autores.

Los tres modelos se pueden administrar desde el sitio `/admin/`.

## Requisitos

- Python 3.12 o superior.
- PostgreSQL 14 o superior.
- Node.js 20.19 o superior y npm.

## Ejecución local en Windows PowerShell

1. Crear y activar un entorno, e instalar dependencias:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

2. Crear una base de datos y un usuario PostgreSQL para la aplicación. Luego definir las variables en la sesión PowerShell (ajustar los valores al entorno local):

   ```powershell
   $env:POSTGRES_DB = "comunidad_cientifica"
   $env:POSTGRES_USER = "comunidad_cientifica"
   $env:POSTGRES_PASSWORD = "cambiar-localmente"
   $env:POSTGRES_HOST = "localhost"
   $env:POSTGRES_PORT = "5432"
   $env:DJANGO_SECRET_KEY = "reemplazar-por-una-clave-local"
   $env:DJANGO_DEBUG = "True"
   $env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
   ```

   `.env.example` enumera las variables; Django no carga archivos `.env` automáticamente. No usar claves ni contraseñas reales en GitHub.

3. Instalar dependencias Angular, compilar a `static/angular/` y preparar la base:

   ```powershell
   npm ci --prefix frontend
   npm run build --prefix frontend
   Set-Location comunidad_cientifica
   python manage.py migrate
   python manage.py seed_research_data
   python manage.py createsuperuser
   python manage.py runserver
   ```

4. Revisar el portal en `http://127.0.0.1:8000/` y el catálogo Angular en `http://127.0.0.1:8000/investigacion/`.

`seed_research_data` crea o actualiza registros explícitamente demostrativos para probar la persistencia y las relaciones. No son datos reales del centro: deben reemplazarse por información revisada y autorizada antes de la entrega.

Para una comprobación local rápida sin PostgreSQL se puede establecer explícitamente `DB_ENGINE=django.db.backends.sqlite3`, pero esa configuración no cumple el requisito de la versión evaluada. El flujo de CI utiliza PostgreSQL.

## Pruebas y compilación

Desde la raíz del repositorio:

```powershell
npm ci --prefix frontend
npm run build --prefix frontend
Set-Location comunidad_cientifica
python manage.py check
python manage.py test accounts research
```

El workflow de GitHub Actions instala las dependencias bloqueadas de Angular con Node.js 20.19 y construye el front-end. También instala Python 3.12/3.13, inicia PostgreSQL, aplica las migraciones (incluida la inicial de `research`) y ejecuta los tests del proyecto. Los archivos generados en `static/angular/` no se versionan: se reconstruyen para cada validación o despliegue.

## Producción

Configurar `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY`, `DJANGO_ALLOWED_HOSTS` y las variables PostgreSQL en el proveedor de despliegue. Compilar Angular y recoger estáticos antes de iniciar un servidor WSGI:

```powershell
npm ci --prefix frontend
npm run build --prefix frontend
Set-Location comunidad_cientifica
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn comunidad_cientifica.wsgi:application
```

La publicación pública y la URL de evaluación aún deben configurarse en un proveedor de hosting y vincularse al repositorio GitHub del equipo. Este directorio de trabajo no incluye un repositorio `.git`, credenciales de GitHub ni credenciales de hosting; por ello, esta modificación por sí sola no crea un commit ni una URL pública.

## Estructura principal

```text
comunidad_cientifica/
  comunidad_cientifica/  # configuración general, URL raíz, WSGI
  accounts/              # cuentas y módulos existentes
  research/              # dominio científico, administración, vistas y tests
frontend/src/app/        # componentes Angular y sus archivos TS/HTML/CSS
templates/               # páginas Django
static/angular/           # salida compilada de Angular (generada)
```

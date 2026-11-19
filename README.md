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
- **Integración del catálogo**: Django sirve la aplicación Angular en `/investigacion/`. Angular consulta el catálogo mediante la API REST `/api/research/`, que lee PostgreSQL con el ORM de Django y responde JSON. La API ofrece operaciones de lectura públicas, pero limita las modificaciones a personal con sesión autenticada y permiso de administración.

### Modelos y relaciones

- `ResearchProject`: proyecto, estado, área, fechas, financiamiento y relación muchos-a-muchos con investigadores.
- `Researcher`: nombre, institución, especialidad, biografía y ORCID.
- `ScientificPublication`: publicación, revista, fecha, DOI/enlace, relación opcional con un proyecto y relación muchos-a-muchos con autores.

Los tres modelos se pueden administrar desde el sitio `/admin/`.

### API REST, JSON y XML

| Endpoint | Métodos | Acceso |
|---|---|---|
| `/api/research/` | `GET` | Público; catálogo JSON consolidado |
| `/api/research/session/` | `GET` | Informa si la sesión pertenece a personal administrador |
| `/api/research/projects/`, `/researchers/`, `/publications/` | `GET`, `POST` | Lectura pública; creación solo para personal administrador |
| `/api/research/projects/<id>/`, `/researchers/<id>/`, `/publications/<id>/` | `GET`, `PATCH`, `PUT`, `DELETE` | Lectura pública; cambios solo para personal administrador |
| `/api/research/export.xml` | `GET` | Exporta el catálogo como XML |

JSON es el formato de intercambio principal entre Angular y Django. Las operaciones de escritura usan la sesión de Django, protección CSRF y permisos de personal (`is_staff`); no requieren una API key en el navegador. El correo de investigadores se acepta al crear o editar, pero no se incluye en las respuestas públicas. Angular muestra errores de conexión/validación y vuelve a consultar el catálogo después de cada cambio exitoso.

El catálogo y la API se sirven desde el mismo origen, por lo que Angular no necesita credenciales CORS separadas. Para administrar registros, inicia sesión con una cuenta Django con permiso de personal; se puede crear una cuenta local con `python manage.py createsuperuser`. Las rutas de escritura requieren esa sesión y un token CSRF válido. La API puede probarse con `GET http://127.0.0.1:8000/api/research/` para JSON y `GET http://127.0.0.1:8000/api/research/export.xml` para XML.

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

2. Crear el usuario y la base de datos PostgreSQL. Desde PowerShell, abre la consola de PostgreSQL con un usuario administrador:

   ```powershell
   psql -U postgres -h localhost -p 5432
   ```

   En el prompt `postgres=#`, ejecuta:

   ```sql
   CREATE USER comunidad_cientifica WITH LOGIN;
   \password comunidad_cientifica
   CREATE DATABASE comunidad_cientifica OWNER comunidad_cientifica;
   \q
   ```

   `\password` solicita la contraseña sin incluirla en el comando. Si el usuario o base ya existen, no los crees de nuevo: revisa la configuración existente o actualiza el usuario con `ALTER USER` desde una sesión administradora.

3. En la misma ventana PowerShell donde ejecutarás Django, define los parámetros locales. La contraseña se solicita de forma oculta y permanece solo en la variable de entorno de esa sesión:

   ```powershell
   $env:POSTGRES_DB = "comunidad_cientifica"
   $env:POSTGRES_USER = "comunidad_cientifica"
   $env:POSTGRES_HOST = "localhost"
   $env:POSTGRES_PORT = "5432"
   $env:DJANGO_DEBUG = "True"
   $env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
   Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
   $securePassword = Read-Host "Contraseña del usuario PostgreSQL" -AsSecureString
   $env:POSTGRES_PASSWORD = [System.Net.NetworkCredential]::new("", $securePassword).Password
   ```

   `DATABASE_URL`, cuando está definida, tiene prioridad sobre `POSTGRES_*`; por eso se elimina en esta sesión para conectar con el PostgreSQL local. `.env.example` enumera las variables, pero Django no carga archivos `.env` automáticamente. Nunca escribas contraseñas o claves reales en el código ni las subas a GitHub.

4. Desde la raíz del repositorio, instala dependencias Angular, compila a `static/angular/` y prepara la base:

   ```powershell
   npm ci --prefix frontend
   npm run build --prefix frontend
   Set-Location comunidad_cientifica
   python manage.py check
   python manage.py migrate
   python manage.py seed_research_data
   python manage.py createsuperuser
   python manage.py runserver
   ```

5. Revisar el portal en `http://127.0.0.1:8000/` y el catálogo Angular en `http://127.0.0.1:8000/investigacion/`.

Al cerrar PowerShell, las variables de entorno de esa sesión desaparecen. También puedes limpiarlas manualmente al terminar:

```powershell
Remove-Item Env:POSTGRES_PASSWORD -ErrorAction SilentlyContinue
Remove-Item Env:DATABASE_URL -ErrorAction SilentlyContinue
```

`seed_research_data` crea o actualiza registros explícitamente demostrativos para probar la persistencia y las relaciones. No son datos reales del centro: deben reemplazarse por información revisada y autorizada antes de la entrega.

Para una comprobación local rápida sin PostgreSQL se puede establecer explícitamente `DB_ENGINE=django.db.backends.sqlite3`, pero esa configuración no cumple el requisito de la versión evaluada. El flujo de CI utiliza PostgreSQL.

## Prueba desde otros dispositivos de la red local

Para que el centro o el equipo pueda revisar el sitio desde otro dispositivo conectado a la misma red Wi-Fi, abre PowerShell en el equipo que ejecutará Django y configura la IP local del equipo en `DJANGO_ALLOWED_HOSTS`. La IP puede cambiar al reconectarse a la red; consulta el valor actual con `ipconfig` y busca la dirección IPv4 del adaptador Wi-Fi:

```powershell
$ip = "192.168.1.112" # Reemplazar por la dirección IPv4 actual del equipo
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1,$ip"
```

En esa misma ventana, desde la raíz del proyecto, compila Angular y levanta Django escuchando conexiones de la red:

```powershell
npm ci --prefix frontend
npm run build --prefix frontend
Set-Location comunidad_cientifica
python manage.py runserver 0.0.0.0:8000
```

Desde otro dispositivo en la misma red, abre `http://<IP-DEL-EQUIPO>:8000/investigacion/`; por ejemplo, `http://192.168.1.112:8000/investigacion/` si esa sigue siendo la IP actual. Si Windows solicita permiso de firewall, permite el acceso solo en redes privadas. Si no aparece la página, revisa que ambos dispositivos estén en la misma red y que el firewall permita conexiones entrantes al puerto 8000.

Esta dirección es **solo para pruebas en la red local**: el equipo que ejecuta Django debe permanecer encendido y el servidor activo. `runserver` es un servidor de desarrollo; no lo expongas a Internet ni configures reenvío de puertos del router. Para una URL pública permanente hace falta desplegar la aplicación en un servicio de hosting.

**Resultado de prueba:** se confirmó que el catálogo local carga desde otro equipo conectado a la misma red privada. Esta verificación no equivale a un despliegue público ni valida HTTPS; la IPv4 local puede cambiar según la asignación del router.

## Pruebas y compilación

Desde la raíz del repositorio:

```powershell
npm ci --prefix frontend
npm run build --prefix frontend
Set-Location comunidad_cientifica
python manage.py check
python manage.py test accounts research
```

El workflow de GitHub Actions instala las dependencias bloqueadas de Angular con Node.js 20.19, construye el front-end y ejecuta sus pruebas unitarias en ChromeHeadless. También instala Python 3.12/3.13, ejecuta `flake8` en la app `research` y la configuración Django, inicia PostgreSQL, aplica las migraciones (incluida la inicial de `research`) y ejecuta los tests de `accounts` y `research` con cobertura. El lint se limita a esos módulos porque el código legado de `accounts` y las vistas generales ya contienen advertencias de estilo no relacionadas con este catálogo. Los archivos generados en `static/angular/` no se versionan: se reconstruyen para cada validación o despliegue.

## Sincronizar el código con GitHub

El repositorio remoto del proyecto es `https://github.com/Marcel-TY/comunidad_cientifica_chile-main-clon.git`.

### Descargar una copia por primera vez

Si todavía no tienes el repositorio en tu equipo:

```powershell
Set-Location "$HOME\Downloads"
git clone https://github.com/Marcel-TY/comunidad_cientifica_chile-main-clon.git
Set-Location .\comunidad_cientifica_chile-main-clon
```

Si ya existe la carpeta local, no vuelvas a clonarla; entra en ella y comprueba el remoto:

```powershell
Set-Location "$HOME\Downloads\comunidad_cientifica_chile-main"
git remote -v
git status -sb
```

Si tu carpeta local tiene otro nombre o está en otra ubicación, sustituye la ruta por la carpeta raíz que contiene `.git`.

Si `git remote -v` no muestra `origin`, conéctalo una sola vez:

```powershell
git remote add origin https://github.com/Marcel-TY/comunidad_cientifica_chile-main-clon.git
git branch -M main
```

### Guardar y subir cambios posteriores

Antes de preparar el commit, revisa qué archivos cambiaron. Añade solamente los archivos intencionales; evita `git add .` si hay cambios locales o archivos sin seguimiento que no quieras publicar.

```powershell
git status --short
git diff --check
git diff -- README.md
git add -- README.md
git diff --cached --check
git diff --cached
git commit -m "Documentar conexión PostgreSQL y GitHub"
git push origin main
```

Para incluir otros archivos del mismo cambio, añádelos por nombre explícito a `git add --`. Si GitHub solicita autenticación, completa el inicio de sesión del navegador o configura Git Credential Manager; no pegues tokens ni contraseñas en el código, el README o la línea de comandos. No subas `.env`, contraseñas, `DATABASE_URL`, claves Django ni respaldos de bases de datos.

## Producción

Configurar `DJANGO_DEBUG=False`, `DJANGO_SECRET_KEY` y PostgreSQL en el proveedor de despliegue. Se puede definir la conexión mediante `DATABASE_URL` o las variables `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_HOST` y `POSTGRES_PORT`. Django reconoce automáticamente `RENDER_EXTERNAL_HOSTNAME` para `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS`; en otros proveedores, configurar esos valores explícitamente. Compilar Angular y recoger estáticos antes de iniciar un servidor WSGI:

```powershell
npm ci --prefix frontend
npm run build --prefix frontend
Set-Location comunidad_cientifica
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn comunidad_cientifica.wsgi:application
```

`DJANGO_SECRET_KEY` es obligatorio cuando `DJANGO_DEBUG=False`; la aplicación falla explícitamente al arrancar si falta. Configura una clave secreta fuerte en el proveedor y nunca la guardes en el repositorio. Detrás de un proxy HTTPS, Django confía en `X-Forwarded-Proto` y activa redirección/cookies seguras. La publicación pública y la URL de evaluación aún deben configurarse en un proveedor de hosting; subir cambios a GitHub no despliega automáticamente esta aplicación Django. Después del despliegue, registrar aquí la URL pública, la URL de la API y el commit correspondiente.

### Despliegue en Render

El repositorio incluye `render.yaml` y `build.sh` para desplegar Django, construir Angular, recoger estáticos, crear PostgreSQL y aplicar migraciones durante el predespliegue. En Render, usa **New > Blueprint**, conecta este repositorio y revisa los planes y cargos antes de seleccionar **Apply**. El Blueprint configura una base PostgreSQL persistente y una instancia web; los costos y disponibilidad dependen de los planes vigentes en la cuenta.

Después de que termine el despliegue:

1. En el Shell del servicio web, ejecuta `cd comunidad_cientifica && python manage.py createsuperuser` para crear las credenciales de administración. No guardes esas credenciales en GitHub ni las compartas en el informe público.
2. Prueba `https://<servicio>.onrender.com/investigacion/`, `https://<servicio>.onrender.com/api/research/` y `https://<servicio>.onrender.com/api/research/export.xml`.
3. Inicia sesión en `/admin/`, añade o edita un registro de prueba y vuelve a consultar el catálogo para verificar persistencia en PostgreSQL.
4. Anota en esta documentación las URL asignadas, el commit desplegado y los resultados de la prueba desde un dispositivo externo.

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

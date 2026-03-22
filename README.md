# Administrador DB

> Dashboard de administración de bases de datos MySQL con Flet (Python)

## 🌟 Descripción

Aplicación de interfaz gráfica para administrar un servidor MySQL con funciones completas: gestión de bases de datos, tablas, backups, CSV, usuarios y métricas de rendimiento.

## 🚀 Novedades y cambios recientes

- Estructura organizada en `app.py`, Servicios (`services/`) y Vistas (`views/`).
- Incorporación de `metrics_service.py` y `metrics_view.py` para monitoreo en tiempo real.
- Soporte mejorado de herramientas CSV y backup desde la UI.
- Corrección de comandos de inicio: ejecutar ahora `python app.py`.

## ✅ Características

- Gestión de bases de datos: crear, eliminar, listar
- Gestión de tablas: ver, crear y modificar tablas
- Backups: crear, listar y restaurar copias
- CSV: importación y exportación de datos
- Usuarios: crear, editar, borrar usuarios MySQL
- Métricas: estadísticas de uso y rendimiento del servidor
- Login: control de acceso inicial de la aplicación

## 🛠 Requisitos

- Python 3.7+ (recomendado 3.10+)
- MySQL Server en ejecución
- Conexión MySQL con permisos suficientes

## ⚙️ Instalación

1. Clona el repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd dab-flet
   ```

2. Instala dependencias:
   ```bash
   pip install flet mysql-connector-python
   ```

3. Configura `db_config.py`:
   ```python
   host = "localhost"
   user = "tu_usuario"
   password = "tu_contraseña"
   port = 3306
   ```
4. Configurar `.env`:
   ```python
   DB_DUMP_PATH="ruta para mariadb-dump.exe"
   DB_CLI_PATH="ruta para mariadb.exe"
   ```

## ▶️ Ejecución

```bash
python app.py
```

La UI muestra un panel lateral con las secciones:

- Bases de datos
- Tablas
- Backups
- CSV
- Usuarios
- Métricas
- Login

## 🧩 Estructura del proyecto

```
app.py
/db_config.py
/services/
  auth_service.py
  backup_service.py
  csv_service.py
  db_service.py
  metrics_service.py
  table_service.py
  user_service.py
/views/
  backup_view.py
  csv_view.py
  db_view.py
  login_view.py
  metrics_view.py
  user_view.py
```

## 💡 Consejos

- Asegúrate de tener usuario MySQL con permisos RAW (CREATE, DROP, SELECT, INSERT, UPDATE, DELETE).
- Se recomienda ejecutar la app en un entorno virtual (`venv`).
- Revisa los logs de la consola para detectar errores de conexión o permisos.

## 📚 Documentación rápida de uso

1. Iniciar sesión (Login).
2. Seleccionar sección en el menú lateral.
3. Usar botones de acción (Crear/Editar/Eliminar/Exportar/Importar).

---

### 📌 Autor
- Estudiante / Desarrollador: [Tu Nombre]
- Proyecto educativo para gestión de bases de datos con Flet.

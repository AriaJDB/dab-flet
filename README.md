# Administrador DB

Un dashboard de administración de bases de datos MySQL construido con Flet, un framework de UI moderno para Python.

## Descripción

Esta aplicación proporciona una interfaz gráfica intuitiva para gestionar bases de datos MySQL. Permite crear, eliminar y gestionar bases de datos, tablas, realizar backups, importar/exportar datos CSV, administrar usuarios y monitorear el rendimiento del servidor.

## Características

- **Gestión de Bases de Datos**: Crear, eliminar y listar bases de datos
- **Gestión de Tablas**: Ver, crear y modificar tablas dentro de las bases de datos
- **Backups**: Crear y restaurar backups de bases de datos
- **Operaciones CSV**: Importar y exportar datos en formato CSV
- **Administración de Usuarios**: Gestionar usuarios de la base de datos
- **Monitoreo de Rendimiento**: Ver estadísticas y métricas del servidor MySQL

## Requisitos Previos

- Python 3.7 o superior
- MySQL Server instalado y ejecutándose
- Acceso a una base de datos MySQL con permisos de administrador

## Instalación

1. Clona este repositorio:
   ```bash
   git clone <url-del-repositorio>
   cd dab-flet
   ```

2. Instala las dependencias:
   ```bash
   pip install flet mysql-connector-python
   ```

3. Configura la conexión a la base de datos en `db_config.py`:
   ```python
   # Modifica los valores según tu configuración
   host="localhost"
   user="tu_usuario"
   password="tu_contraseña"
   port=3306
   ```

## Uso

Ejecuta la aplicación con:
```bash
python dashboard.py
```

La aplicación se abrirá en una ventana con un panel lateral que permite navegar entre las diferentes secciones:

- **Bases de datos**: Gestiona las bases de datos del servidor
- **Tablas**: Administra las tablas dentro de una base de datos seleccionada
- **Backups**: Crea y restaura copias de seguridad
- **CSV**: Importa/exporta datos en formato CSV
- **Usuarios**: Gestiona los usuarios de la base de datos
- **Rendimiento**: Monitorea el rendimiento del servidor

## Estructura del Proyecto

```
dab-flet/
├── dashboard.py          # Archivo principal de la aplicación
├── db_config.py          # Configuración de conexión a MySQL
├── services/             # Lógica de negocio
│   ├── db_service.py     # Servicios para bases de datos
│   ├── table_service.py  # Servicios para tablas
│   ├── backup_service.py # Servicios para backups
│   ├── csv_service.py    # Servicios para operaciones CSV
│   └── user_service.py   # Servicios para usuarios
└── views/                # Interfaces de usuario
    ├── db_view.py        # Vista de bases de datos
    ├── table_view.py     # Vista de tablas
    ├── backup_view.py    # Vista de backups
    ├── csv_view.py       # Vista de CSV
    └── user_view.py      # Vista de usuarios
```
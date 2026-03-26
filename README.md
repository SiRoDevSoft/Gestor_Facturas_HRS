# Gestor de Facturas HRS 📑

Sistema de auditoría y gestión de facturación de telefonía móvil (Movistar) para **Hierrosan**. Este software automatiza el procesamiento de consumos masivos, permitiendo la asignación dinámica de costos a diferentes grupos de flota.

## 🚀 Características Principales

* **Auditoría de PDF:** Extracción de datos directamente de los resúmenes de facturación.
* **Re-mapeo Dinámico:** El sistema no depende de datos estáticos en la DB. Cruza la historia de consumos (SQLite) con la configuración actual de dueños y grupos (JSON) en tiempo real mediante **Pandas**.
* **Generación de Comprobantes:** Creación automatizada de boletos de cobro por grupo (KOPRAM, LUCARELLI, TERCEROS, etc.).
* **Gestión de Flota:** Sidebar interactivo para altas, bajas y cambios de categoría de líneas sin tocar el código.
## 🚀 Características Principales
* **Auditoría de Facturas:** Procesamiento y limpieza de datos de facturación (Movistar/Terceros).
* **Boletos de Cobro:** Generación automatizada de comprobantes en PDF con recargos configurables.
* **Pronóstico de Flujo:** Visualización de proyecciones económicas y límites operativos.
* **Persistencia en la Nube:** Gestión de usuarios y configuración mediante **PostgreSQL (Neon.tech)**.
* **Seguridad:** Sistema de autenticación con hashing SHA-256 y recuperación mediante preguntas de seguridad.

## 🛠️ Stack Tecnológico
* **Lenguaje:** Python 3.13+
* **Frontend:** Streamlit (UI Reactiva)
* **Base de Datos:** PostgreSQL (Vía SQLAlchemy + psycopg2)
* **Generación de Documentos:** FPDF2 / Pandas
* **Deployment:** Streamlit Cloud

## 📋 Configuración de Entorno (Secrets)
Para que el sistema funcione en la nube, es necesario configurar las siguientes variables en los **Secrets** de Streamlit:
*******************************************************************************


## 🛠️ Estructura del Proyecto

```text
HIERROSAN_APP/
├── main.py                 # Punto de entrada y navegación (Streamlit)
├── json/
│   ├── mapeos.json         # Maestro de Grupos y Categorías
│   └── config_lineas.json  # Mapeo Línea -> Dueño (Fuente de Verdad)
├── models/
│   └── database.py         # Capa de persistencia SQLite
└── views/
    ├── v_auditoria.py      # Procesamiento de facturas
    ├── v_abonos.py         # Motor de re-mapeo y emisión de boletos
    └── v_configuracion.py  # Gestión de parámetros del sistema
---
## 🌐 Contacto y Desarrollo

✒️ Desarrollado por
SiRoDevSoft - Soluciones de Software a medida.
San Rafael, Mendoza, Argentina.

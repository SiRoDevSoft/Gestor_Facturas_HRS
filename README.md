# Gestor de Facturas HRS 📑

Sistema de auditoría y gestión de facturación de telefonía móvil (Movistar) para **Hierrosan**. Este software automatiza el procesamiento de consumos masivos, permitiendo la asignación dinámica de costos a diferentes grupos de flota.

## 🚀 Características Principales

* **Auditoría de PDF:** Extracción de datos directamente de los resúmenes de facturación.
* **Re-mapeo Dinámico:** El sistema no depende de datos estáticos en la DB. Cruza la historia de consumos (SQLite) con la configuración actual de dueños y grupos (JSON) en tiempo real mediante **Pandas**.
* **Generación de Comprobantes:** Creación automatizada de boletos de cobro por grupo (KOPRAM, LUCARELLI, TERCEROS, etc.).
* **Gestión de Flota:** Sidebar interactivo para altas, bajas y cambios de categoría de líneas sin tocar el código.

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

# Gestor de Facturas HRS 

Sistema de auditoría y gestión de facturación de telefonía móvil (Movistar) para **Hierrosan**. Este software automatiza el procesamiento de consumos masivos, permitiendo la asignación dinámica de costos a diferentes grupos de flota.



# Auditoría de Facturación Movistar - ERP Hierrosan 📑

Sistema integral de auditoría y control de facturación de telecomunicaciones. Esta herramienta permite procesar, analizar y detectar inconsistencias en los cargos de Movistar Empresas de manera automatizada, transformando datos crudos en información estratégica para la toma de decisiones.

## Características Principales

* **Auditoría de PDF:** Extracción de datos directamente de los resúmenes de facturación.
* **Re-mapeo Dinámico:** El sistema no depende de datos estáticos en la DB. Cruza la historia de consumos (SQLite) con la configuración actual de dueños y grupos (JSON) en tiempo real mediante **Pandas**.
* **Generación de Comprobantes:** Creación automatizada de boletos de cobro por grupo (KOPRAM, LUCARELLI, TERCEROS, etc.).
* **Gestión de Flota:** Sidebar interactivo para altas, bajas y cambios de categoría de líneas sin tocar el código.

## 📁 Estructura del Proyecto

El proyecto sigue una arquitectura modular y limpia (Clean Architecture), facilitando el mantenimiento y la escalabilidad del sistema:

* **`main.py`**: Punto de entrada principal y configuración de la aplicación.
* **`views/`**: Capa de presentación (UI). Contiene los módulos de Login, Dashboard, Auditoría, Abonos, Consultas y Configuración.
* **`models/`**: Capa de datos. Gestión de autenticación (`auth_db.py`) y lógica de base de datos (`database.py`, `db.py`).
* **`json/`**: Configuración dinámica. Contiene los mapeos, índices y márgenes para la lógica de auditoría sin necesidad de recompilar código.
* **`utils/`**: Funciones auxiliares y herramientas de soporte técnico.
* **`requirements.txt`**: Dependencias necesarias para el entorno de ejecución.

## Funcionalidades Clave

* **Gestión de Accesos:** Sistema de login seguro con validación de usuarios en base de datos.
* **Motor de Auditoría:** Procesamiento de archivos de texto crudos (`auditoria_juegos_crudo.txt`) y validación contra reglas de negocio.
* **Dashboards de Control:** Visualización interactiva de métricas, cargos fijos y variables.
* **Mapeo Dinámico:** Uso de archivos JSON para actualizar índices de precios y configuraciones de líneas en tiempo real.
* **Interfaz Corporativa:** UI personalizada para **Hierrosan**, eliminando elementos nativos de la plataforma para una experiencia "White-label".

## Tecnologías Utilizadas

* **Lenguaje:** Python 3.10+
* **Frontend:** Streamlit (Personalizado con CSS inyectado para branding).
* **Persistencia:** SQL / Modelos de datos estructurados.
* **Configuración:** JSON para mapeos dinámicos de facturación.
* **Control de Versiones:** Git.

## UI & UX (Custom Branding)

Se aplicó una capa de personalización avanzada para ofrecer una estética de software propietario:
* Limpieza de headers y footers nativos mediante selectores CSS específicos (`.st-emotion-cache`).
* Sidebar colapsable con persistencia de estado para optimizar el espacio de trabajo.
* Identidad visual adaptada a la marca **Hierrosan**.

## Instalación y Uso

1. **Clonar el repositorio:**
   ```bash
   git clone [https://github.com/tu-usuario/nombre-del-repo.git](https://github.com/tu-usuario/nombre-del-repo.git)
---
---

## 🌐 Contacto y Desarrollo

**Desarrollado por [SiRoDevSoft](https://sirodevsoft.github.io)** *Soluciones de Software a Medida | Especialistas en Gestión de Datos*

[![Website](https://img.shields.io/badge/Website-SiRoDevSoft-blue?style=for-the-badge&logo=google-chrome)](https://sirodevsoft.github.io)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Profile-0077B5?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/silviojonrojas)

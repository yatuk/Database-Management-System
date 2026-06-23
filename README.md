# Database Management System

<div align="center">

**A comprehensive web-based database management and visualization platform for analyzing World Development Indicators (WDI) data across multiple domains**

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-2.0+-green?style=flat-square)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange?style=flat-square)](https://www.mysql.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&style=flat-square)](https://getbootstrap.com/)
[![Chart.js](https://img.shields.io/badge/Chart.js-4.4-FF6384?logo=chart.js&style=flat-square)](https://www.chartjs.org/)
[![License](https://img.shields.io/badge/License-Educational-yellow?style=flat-square)](LICENSE)

*Developed as a term project for **BLG-317E (Database Systems)** course*

</div>

<br />

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Database Schema](#database-schema)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Step-by-Step Setup](#step-by-step-setup)
  - [Environment Configuration](#environment-configuration)
  - [Data Loading](#data-loading)
- [Role-Based Access Control](#role-based-access-control)
- [Data Domains](#data-domains)
- [API Endpoints](#api-endpoints)
- [Usage](#usage)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

This **Database Management System** provides an interactive platform for exploring, analyzing, and managing multi-domain indicator data from the World Development Indicators (WDI) dataset published by the World Bank. The system enables users to browse country-level and regional data, visualize trends through interactive charts and maps, perform cross-country comparisons, and manage data through role-based CRUD operations with full audit logging.

| Capability | Description |
|---|---|
| **Multi-Domain Data Management** | Support for 6 data domains: Countries, Health, GHG Emissions, Energy, Freshwater, Sustainability |
| **Interactive Dashboards** | Overview dashboards with key metrics and visualizations |
| **Advanced Filtering** | Filter data by country, region, year, and indicator |
| **Trend Analysis** | Automatic calculation of percentage changes and trends over time |
| **Data Visualization** | Interactive line charts, global trend visualizations, regional comparisons, sparkline indicators |
| **Geographic Visualization** | Interactive world map with country-level data |
| **Data Export** | CSV export functionality for filtered datasets |
| **Pagination** | Efficient handling of large datasets with configurable page sizes |
| **Role-Based Access Control** | Three distinct user roles (Admin, Editor, Viewer) with granular permissions |
| **Audit Logging** | Track data modifications with user attribution |

---

## Features

### Core Functionality

| Category | Capability | Details |
|---|---|---|
| **Data Management** | Browse, filter, search, add, edit, delete | Full CRUD with role-based restrictions |
| **Visualization** | Line charts, maps, sparklines | Built with Chart.js 4.4 |
| **Filtering** | Country, region, year, indicator | Multi-criteria with dynamic dropdowns |
| **Search** | Full-text search across countries and indicators | Case-insensitive, partial match |
| **Pagination** | Server-side pagination | 50 records per page |
| **Export** | CSV download | Export filtered datasets |
| **Trend Analysis** | Percentage change, year-over-year comparison | Automatic calculation |
| **Regional Aggregation** | Region-level statistics | AVG, MIN, MAX, country count per region |

### Security & Access Control

| Role | Permissions | Team Number |
|---|---|---|
| **Admin** | Full CRUD access, delete records, manage users | `team_no = 1` |
| **Editor** | Add and edit records, cannot delete | `team_no = 2` |
| **Viewer** | Read-only access to all dashboards and data | Default (unauthenticated) |

### User Experience

- **Responsive Design**: Works seamlessly on desktop and tablet devices
- **Smooth Animations**: Subtle UI animations for enhanced user experience
- **Tooltips & Helpers**: Contextual information throughout the interface
- **Search Functionality**: Quick search across countries and indicators

---

## Technology Stack

<table>
  <tr>
    <th>Layer</th>
    <th>Technology</th>
  </tr>
  <tr>
    <td><strong>Backend Framework</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Flask-2.0+-000000?logo=flask&logoColor=white" alt="Flask" />
      &nbsp; Blueprint-based modular route architecture
    </td>
  </tr>
  <tr>
    <td><strong>Language</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Python-3.9+-3776AB?logo=python&logoColor=white" alt="Python" />
    </td>
  </tr>
  <tr>
    <td><strong>Database</strong></td>
    <td>
      <img src="https://img.shields.io/badge/MySQL-8.0+-4479A1?logo=mysql&logoColor=white" alt="MySQL" />
      &nbsp; InnoDB, foreign key constraints, composite unique keys
    </td>
  </tr>
  <tr>
    <td><strong>Database Connector</strong></td>
    <td>
      <img src="https://img.shields.io/badge/mysql--connector--python-Latest-4479A1?logo=python&logoColor=white" alt="mysql-connector-python" />
    </td>
  </tr>
  <tr>
    <td><strong>Frontend</strong></td>
    <td>
      <img src="https://img.shields.io/badge/HTML5-E34F26?logo=html5&logoColor=white" alt="HTML5" />
      <img src="https://img.shields.io/badge/CSS3-1572B6?logo=css3&logoColor=white" alt="CSS3" />
      <img src="https://img.shields.io/badge/JavaScript-ES6+-F7DF1E?logo=javascript&logoColor=black" alt="JavaScript" />
    </td>
  </tr>
  <tr>
    <td><strong>UI Framework</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white" alt="Bootstrap 5.3" />
    </td>
  </tr>
  <tr>
    <td><strong>Charts</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Chart.js-4.4-FF6384?logo=chart.js&logoColor=white" alt="Chart.js 4.4" />
    </td>
  </tr>
  <tr>
    <td><strong>Template Engine</strong></td>
    <td>
      <img src="https://img.shields.io/badge/Jinja2-Flask-000000?logo=jinja&logoColor=white" alt="Jinja2" />
    </td>
  </tr>
  <tr>
    <td><strong>Configuration</strong></td>
    <td>
      <img src="https://img.shields.io/badge/python--dotenv-✓-ECD53F?logo=python&logoColor=white" alt="python-dotenv" />
    </td>
  </tr>
</table>

---

## Project Structure

```
Database-Management-System/
├── App/
│   ├── routes/                  # Flask Blueprint route handlers
│   │   ├── __init__.py          # Application factory (create_app)
│   │   ├── dashboard.py         # Dashboard overview with coverage stats
│   │   ├── countries.py         # Country listing, profiles, regions, map API
│   │   ├── ghg.py               # GHG emissions domain (CRUD + filtering)
│   │   ├── health.py            # Health indicators domain (CRUD + filtering)
│   │   ├── energy.py            # Energy data domain (CRUD + filtering)
│   │   ├── freshwater.py        # Freshwater resources domain (CRUD + filtering)
│   │   ├── sustainability.py    # Sustainability metrics domain (CRUD + filtering)
│   │   ├── login.py             # Authentication, RBAC decorators, session management
│   │   └── about.py             # About page with team member listing
│   ├── db.py                    # Database connection utilities (request-scoped)
│   └── db_setup.py              # Database creation and schema initialization
├── Data/                        # CSV data files
│   ├── countries.csv
│   ├── greenhouse_emissions.csv
│   ├── health_system.csv
│   ├── energy_data.csv
│   ├── freshwater_data.csv
│   ├── sustainability_data.csv
│   └── *_indicator_details.csv
├── SQL/                         # SQL scripts
│   ├── database.sql             # Full database schema (DDL)
│   └── load_*.sql               # Per-table data loading scripts
├── frontend/
│   ├── css/
│   │   ├── style.css            # Global styles (~6400 lines)
│   │   └── templates/           # Jinja2 HTML templates (19 files)
│   │       ├── base.html        # Base layout with navbar and footer
│   │       ├── dashboard.html   # Dashboard overview
│   │       ├── country_list.html
│   │       ├── country_profile.html
│   │       ├── country_no_data.html
│   │       ├── region_profile.html
│   │       ├── ghg_list.html
│   │       ├── ghg_form.html
│   │       ├── health_list.html
│   │       ├── health_form.html
│   │       ├── energy_list.html
│   │       ├── energy_form.html
│   │       ├── freshwater_list.html
│   │       ├── freshwater_form.html
│   │       ├── sustainability_list.html
│   │       ├── sustainability_form.html
│   │       ├── login.html
│   │       ├── about.html
│   │       └── index.html
├── scripts/                     # Utility scripts
│   ├── load_all.py              # Bulk CSV data loader with deduplication
│   ├── load_user.py             # Seed user accounts
│   └── load_countries.py        # Country data loader
├── main.py                      # Application entry point
├── requirements.txt             # Python dependencies
└── .env                         # Environment variables (user-created)
```

---

## Architecture

### Request Flow

```
Client (Browser)
      │
      ▼
┌─────────────┐
│  Flask App  │  main.py -> create_app()
│  :5000      │
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌──────────────┐
│  Blueprint  │────>│  Template    │
│  Routes     │     │  Rendering   │
└──────┬──────┘     └──────────────┘
       │
       ▼
┌─────────────┐
│  get_db()   │  Request-scoped connection via flask.g
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  MySQL      │  wdi_project database
│  :3306      │  13 tables, InnoDB, FK constraints
└─────────────┘
```

### Component Details

| Component | Language | Role | Key Files |
|---|---|---|---|
| **Application Factory** | Python | Flask app creation, blueprint registration, context processors | `App/routes/__init__.py` |
| **Database Layer** | Python | Connection pooling (request-scoped), teardown hooks | `App/db.py`, `App/db_setup.py` |
| **Route Handlers** | Python | Domain-specific CRUD, filtering, pagination, chart data | `App/routes/*.py` |
| **Templates** | Jinja2/HTML | Responsive UI with Bootstrap 5.3 and Chart.js 4.4 | `frontend/css/templates/` |
| **Data Loader** | Python | CSV ingestion with deduplication, foreign key remapping | `scripts/load_all.py` |
| **MySQL Database** | SQL | Schema, constraints, relationships | `SQL/database.sql` |

---

## Database Schema

### Entity-Relationship Overview

```
┌───────────┐       ┌──────────────────────────┐
│  students │       │      audit_logs           │
├───────────┤       ├──────────────────────────┤
│ PK student_id────>│ FK student_id             │
│    student_number │    action_type             │
│    full_name      │    table_name              │
│    team_no        │    record_id               │
└───────────┘       │    action_timestamp        │
                    └──────────────────────────┘

┌───────────┐       ┌──────────────────────────┐
│ countries │       │   health_system           │
├───────────┤       ├──────────────────────────┤
│ PK country_id────>│ FK country_id             │
│    country_name   │ FK health_indicator_id────┐
│    country_code   │    indicator_value         │
│    region         │    year                    │
└───────────┘       │    source_notes            │
        │           └──────────────────────────┘
        │           ┌──────────────────────────┐
        │           │ health_indicator_details  │
        │           ├──────────────────────────┤
        ├──────────>│ PK health_indicator_id────┘
        │           │    indicator_name
        │           │    indicator_description
        │           │    unit_symbol
        │           └──────────────────────────┘
        │
        │           ┌──────────────────────────┐
        │           │   greenhouse_emissions    │
        │           ├──────────────────────────┤
        ├──────────>│ FK country_id             │
        │           │ FK ghg_indicator_id───────┐
        │           │    indicator_value         │
        │           │    share_of_total_pct      │
        │           │    uncertainty_pct         │
        │           │    year                    │
        │           │    source_notes            │
        │           └──────────────────────────┘
        │           ┌──────────────────────────┐
        │           │  ghg_indicator_details    │
        │           ├──────────────────────────┤
        │           │ PK ghg_indicator_id───────┘
        │           │    indicator_name
        │           │    indicator_description
        │           │    unit_symbol
        │           └──────────────────────────┘
        │
        │   (same pattern repeats for energy_data, freshwater_data,
        │    sustainability_data with their respective indicator_detail tables)
        │
        └──────────> (energy_data + energy_indicator_details)
        └──────────> (freshwater_data + freshwater_indicator_details)
        └──────────> (sustainability_data + sustainability_indicator_details)
```

### Core Tables

| Table | Description | Key Constraints |
|---|---|---|
| `countries` | Country information (name, code, region) | `country_name` UNIQUE, `country_code` UNIQUE |
| `students` | User accounts with role assignments | `student_number` UNIQUE |
| `audit_logs` | Track data modifications with user attribution | FK to `students` |

### Domain Tables

Each domain follows a consistent normalized pattern: a fact table referencing `countries` and a detail table storing indicator metadata.

| Domain | Fact Table | Detail Table | Unique Constraint |
|---|---|---|---|
| Health | `health_system` | `health_indicator_details` | `(country_id, health_indicator_id, year)` |
| GHG Emissions | `greenhouse_emissions` | `ghg_indicator_details` | `(country_id, ghg_indicator_id, year)` |
| Energy | `energy_data` | `energy_indicator_details` | `(country_id, energy_indicator_id, year)` |
| Freshwater | `freshwater_data` | `freshwater_indicator_details` | `(country_id, freshwater_indicator_id, year)` |
| Sustainability | `sustainability_data` | `sustainability_indicator_details` | `(country_id, sus_indicator_id, year)` |

See `SQL/database.sql` for the complete schema definition with all relationships and constraints.

---

## Installation

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** -- [Download Python](https://www.python.org/downloads/)
- **MySQL 8.0 or higher** -- [Download MySQL](https://dev.mysql.com/downloads/mysql/)
- **pip** -- Python package manager (included with Python)
- **Git** -- [Download Git](https://git-scm.com/downloads)

### Step-by-Step Setup

#### Step 1: Clone the Repository

```bash
git clone https://github.com/yatuk/Database-Management-System.git
cd Database-Management-System
```

#### Step 2: Create Virtual Environment

Create and activate a virtual environment to isolate project dependencies:

**Windows:**
```bash
python -m venv venv
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

> **Note**: If you encounter execution policy issues on Windows PowerShell, run:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```

#### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

#### Step 4: Set Up MySQL Database

1. **Start MySQL Server** (if not already running)

2. **Create the Database:**
   ```sql
   CREATE DATABASE wdi_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
   ```

3. **Run the Database Schema Script:**
   ```bash
   # Windows
   mysql -u root -p wdi_project < SQL/database.sql

   # Linux/Mac
   mysql -u root -p wdi_project < SQL/database.sql
   ```

### Environment Configuration

Create a `.env` file in the project root directory with your database credentials:

```env
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=wdi_project
DB_PORT=3306
SECRET_KEY=your_secret_key_here
```

The application automatically loads these environment variables using `python-dotenv`.

### Data Loading

Data loading must be performed in the correct order for the application to work properly.

#### Step 5: Load All Data (Run First)

This script creates the database schema and loads all CSV data files. **This must be run BEFORE loading users.**

```bash
# Using venv Python (recommended)
python scripts/load_all.py
```

**What this script does:**
- Drops and recreates the database schema
- Loads all CSV files from the `Data/` directory:
  - Countries data
  - GHG emissions data and indicators
  - Health system data and indicators
  - Energy data and indicators
  - Freshwater data and indicators
  - Sustainability data and indicators
- Handles data deduplication and foreign key relationships
- Disables foreign key checks during bulk loading for performance

#### Step 6: Load User Accounts (Run Second)

After loading all data, seed the user accounts. **This must be run AFTER load_all.py.**

```bash
python scripts/load_user.py
```

**What this script does:**
- Creates user accounts in the `students` table
- Sets up admin users (`team_no = 1`):
  - `820230313` - Salih Sefer
  - `820230334` - Atahan Evintan
  - `820230326` - Fatih Serdar Cakmak
  - `820230314` - Muhammet Tuncer
  - `150210085` - Gulbahar Karabas
- Sets up editor user (`team_no = 2`):
  - `5454` - Editor User

> **Why this order matters:**
> `load_all.py` creates the database schema and loads all domain data. `load_user.py` requires the database and tables to exist. Running them in reverse order will fail.

---

## Role-Based Access Control

The system uses the `team_no` field in the `students` table to determine user roles. Authentication is based on student number only for this educational project.

### Role Definitions

| Role | `team_no` | Create | Read | Update | Delete | Notes |
|---|---|---|---|---|---|---|
| **Admin** | `1` | Yes | Yes | Yes | Yes | Full system access |
| **Editor** | `2` | Yes | Yes | Yes | No | Cannot delete records |
| **Viewer** | Default | No | Yes | No | No | Read-only, unauthenticated users |

### Implementation

```python
# Route protection decorators (App/routes/login.py)

@editor_required   # Requires team_no in (1, 2)
def add_record():
    ...

@admin_required    # Requires team_no == 1
def delete_record():
    ...
```

The current user's role is injected into all templates via `@app.context_processor`, making `current_role`, `is_admin`, `is_editor`, and `is_viewer` available in every Jinja2 template for UI-level access control.

---

## Data Domains

### 1. Countries
- Country profiles with comprehensive statistics across all domains
- Regional aggregations with AVG, MIN, MAX, and country counts
- Interactive world map visualization with data availability indicators
- ISO2-to-ISO3 code mapping for geographic lookups
- Country comparison tools

### 2. GHG Emissions
- CO2 total emissions (`ghg_indicator_id = 5`)
- CO2 per capita (`ghg_indicator_id = 6`)
- Total greenhouse gas emissions (`ghg_indicator_id = 1`)
- Trend analysis with percentage changes
- Global CO2 per capita trend visualization
- Share of total percentage and uncertainty metrics

### 3. Health
- Health system indicators and population health metrics
- Cross-country health comparisons
- Indicator-specific year range filtering

### 4. Energy
- Energy consumption and production data
- Multiple energy indicators with measurement units
- Renewable energy indicators via `energy_indicator_details`

### 5. Freshwater
- Freshwater resource availability and usage metrics
- Water quality indicators
- Source notes for traceability

### 6. Sustainability
- Environmental sustainability metrics
- Resource management indicators
- Long-term sustainability trends
- Indicator codes for programmatic access

---

## API Endpoints

### Authentication

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/auth/login` | None | Login page |
| `POST` | `/auth/login` | None | Authenticate with student number |
| `GET` | `/auth/logout` | None | Clear session and redirect to login |

### Dashboard

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/dashboard` | None | Main dashboard with domain coverage stats |

### Countries

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/countries/` | None | List all countries with search and data availability |
| `GET` | `/countries/profile/<id>` | None | Country profile with all domain data |
| `GET` | `/countries/region/<name>` | None | Region profile with aggregated statistics |
| `GET` | `/countries/resolve/<iso2>` | None | Resolve ISO2 code to country profile |
| `GET` | `/countries/api/stats` | None | Global statistics (JSON) |
| `GET` | `/countries/api/region-stats` | None | Region statistics (JSON) |
| `GET` | `/countries/api/has-data/<iso2>` | None | Data availability check (JSON) |

### Domain CRUD Endpoints

Each domain (GHG, Health, Energy, Freshwater, Sustainability) follows a consistent pattern:

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/<domain>/` | None | List records with filtering and pagination |
| `GET` | `/<domain>/api/get/<id>` | None | Get single record (JSON) |
| `POST` | `/<domain>/api/add` | Editor/Admin | Add new record |
| `POST` | `/<domain>/api/edit/<id>` | Editor/Admin | Edit existing record |
| `POST` | `/<domain>/api/delete/<id>` | Admin | Delete record |

### About

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/about` | None | About page with team member listing |

---

## Usage

### Starting the Application

```bash
# Activate virtual environment first (if not already activated)
.\venv\Scripts\activate    # Windows
source venv/bin/activate    # Linux/Mac

# Run the application
python main.py
```

The application will start and be available at: **http://localhost:5000**

### Default Login Credentials

After running `load_user.py`, you can log in with any of these accounts (no password required):

**Admin Accounts** (Full CRUD access):

| Student Number | Name |
|---|---|
| `820230326` | Fatih Serdar Cakmak |
| `820230313` | Salih Sefer |
| `820230334` | Atahan Evintan |
| `820230314` | Muhammet Tuncer |
| `150210085` | Gulbahar Karabas |

**Editor Account** (Add/Edit only):

| Student Number | Name |
|---|---|
| `5454` | Editor User |

### Navigation

| Section | Path | Description |
|---|---|---|
| **Dashboard** | `/dashboard` | Overview of key indicators and trends |
| **Countries** | `/countries` | Browse countries and regional data |
| **Health** | `/health` | Health indicators and statistics |
| **GHG Emissions** | `/ghg` | Greenhouse gas emissions by country and year |
| **Energy** | `/energy` | Energy consumption and production data |
| **Freshwater** | `/freshwater` | Freshwater resources and usage |
| **Sustainability** | `/sustainability` | Sustainability metrics and environmental indicators |

---

## Troubleshooting

### Common Issues

**1. Database Connection Error**
- Verify MySQL server is running
- Check `.env` file exists and has correct credentials
- Ensure database `wdi_project` exists

**2. Import Errors**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**3. Script Execution Order Error**
- **Always run `load_all.py` BEFORE `load_user.py`**
- If you ran them in wrong order, drop database and start over:
  ```sql
  DROP DATABASE wdi_project;
  CREATE DATABASE wdi_project CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
  ```
  Then run scripts in correct order again.

**4. PowerShell Execution Policy Error (Windows)**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**5. Module Not Found Errors**
- Ensure you are in the project root directory
- Verify virtual environment is activated
- Check that all dependencies are installed

**6. Port Already in Use**
- Flask default port is 5000; if occupied, set `FLASK_RUN_PORT` in `.env` or modify `main.py`

---

## License

This project is developed for **educational purposes** as part of the **BLG-317E Database Systems** course at Istanbul Technical University.

---

## Acknowledgments

- **World Bank** for providing the World Development Indicators (WDI) dataset
- **Flask** and **Bootstrap** communities for excellent documentation
- **Chart.js** for powerful visualization capabilities
- Course instructors and teaching assistants at ITU

---

## Links

| Resource | Location |
|---|---|
| **Database Schema** | `SQL/database.sql` |
| **Data Loading Script** | `scripts/load_all.py` |
| **User Seeding Script** | `scripts/load_user.py` |
| **Application Entry Point** | `main.py` |
| **Route Handlers** | `App/routes/` |
| **HTML Templates** | `frontend/css/templates/` |
| **CSV Data Files** | `Data/` |

<br />

<div align="center">
  <sub>Built by Team 1 for BLG-317E Database Systems</sub>
</div>

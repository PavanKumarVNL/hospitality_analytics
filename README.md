# 🏨 Hospitality Analytics Platform

An end-to-end data analytics project designed to monitor hotel performance across operations, revenue, guest experience, and workforce management.

The platform uses Python, MySQL, Pandas, and Streamlit to generate historical hospitality data, transform it into business-focused aggregate tables, and present actionable insights through an interactive dashboard.

---

## 📌 Project Overview

The hospitality industry relies on several operational and business metrics to evaluate hotel performance. Monitoring occupancy, room revenue, guest satisfaction, and employee turnover helps management identify performance gaps and make informed decisions.

This project simulates a hospitality analytics environment covering **8 hotels over 5 years (2021–2025)**.

The solution follows a data workflow:

1. Design a relational database using MySQL.
2. Generate realistic sample data using Python and Faker.
3. Load and validate the generated data.
4. Create monthly aggregate tables using SQL.
5. Build an interactive dashboard using Streamlit and Plotly.
6. Analyze historical trends and seasonal variations.

## 🎯 Business Objectives

The project focuses on answering important business questions:

- How efficiently are hotels utilizing their available rooms?
- How much revenue is generated per occupied and available room?
- How does guest satisfaction change over time?
- Which hotels experience higher employee turnover?
- How do seasonal patterns influence hotel performance?
- Which hotels contribute the most to overall room revenue?

## 📊 Key Performance Indicators (KPIs)

The dashboard tracks five primary business KPIs.

| KPI | Description | Calculation |
|---|---|---|
| Occupancy Rate | Percentage of available room nights occupied | Occupied Room Nights / Available Room Nights × 100 |
| ADR | Average revenue earned per occupied room night | Room Revenue / Occupied Room Nights |
| RevPAR | Revenue generated per available room night | Room Revenue / Available Room Nights |
| Guest Satisfaction | Average guest feedback rating | Weighted Average of Guest Ratings |
| Employee Turnover Rate | Percentage of average workforce leaving | Employees Exited / Average Headcount × 100 |

## 🏗️ Project Architecture

The project follows a relational data model with a SQL aggregation layer.

```text
              Python Data Generation
                 (Faker + Pandas)
                        |
                        v
                  MySQL Database
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
      Hotels          Guests          Employees
      Rooms          Bookings
                     Feedback
                        |
                        v
                  SQL Aggregation
                        |
        +---------------+----------------+
        |               |                |
        v               v                v
   Hotel Monthly   Guest Satisfaction   Employee
   Performance        Aggregates        Turnover
        |               |                |
        +---------------+----------------+
                        |
                        v
                CSV Aggregate Tables
                        |
                        v
                Streamlit Dashboard
                        |
                        v
                 Business Insights
```

## 🗄️ Database Design

The MySQL database contains six relational tables.

| Table | Purpose |
|---|---|
| `hotels` | Stores hotel information |
| `rooms` | Stores room details and room types |
| `guests` | Stores guest information |
| `bookings` | Stores booking and reservation records |
| `employees` | Stores employee and employment information |
| `guest_feedback` | Stores guest ratings and feedback |

UUIDs are used as primary identifiers, with foreign keys maintaining relationships between entities.

## ⚙️ Data Generation

Sample data is generated using Python, Pandas, and Faker.

**Dataset coverage: 2021–2025**

| Table | Generated Records |
|---|---:|
| Hotels | 8 |
| Rooms | 320 |
| Guests | 15,000 |
| Employees | 520 |
| Bookings | 73,920 |
| Guest Feedback | 43,035 |
| **Total** | **132,803** |

The generated dataset incorporates business variations such as:

- Seasonal booking demand.
- Peak-season and off-season room pricing.
- Annual room-rate trends.
- Hotel-specific demand variations.
- Guest satisfaction variations.

## 🔄 SQL Aggregation Layer

Three monthly aggregate tables are created using SQL.

| Aggregate Table | Purpose |
|---|---|
| `agg_hotel_monthly_performance` | Occupancy, ADR, RevPAR and room revenue |
| `agg_guest_satisfaction` | Average ratings and positive feedback |
| `agg_employee_turnover` | Opening headcount, closing headcount, employee exits and turnover |

Each aggregate table contains **480 records** (8 hotels × 60 months).

The aggregation layer converts transactional data into a format suitable for business reporting and dashboard analysis.

## 📈 Interactive Dashboard

The dashboard is developed using Streamlit and Plotly.

### 1. Executive Overview
- Five primary KPI cards.
- Previous-period KPI comparisons.
- Dynamic reporting period.

### 2. Operations & Revenue
- Monthly occupancy rate.
- ADR vs RevPAR trends.
- Room revenue by hotel.
- Occupancy rate by hotel.

### 3. Guest Experience
- Monthly guest satisfaction.
- Positive feedback rate.
- Guest feedback volume by hotel.
- Occupancy vs guest satisfaction.

### 4. Workforce Performance
- Monthly employee turnover rate.
- Monthly employee exits.
- Employee exits by hotel.
- Opening vs closing headcount.

### 5. Seasonal Analysis
- Occupancy rate by season.
- ADR vs RevPAR by season.
- Guest satisfaction by season.
- Employee turnover by season.

### Dashboard Filters

The sidebar provides interactive filters for:

- Hotel selection.
- Reporting date range.
- Season selection.

All dashboard KPIs and visualizations respond to the selected filters.

## 🛠️ Technology Stack

| Technology | Usage |
|---|---|
| Python | Data generation and application development |
| MySQL | Relational database and data storage |
| SQL | Data aggregation and KPI calculations |
| Pandas | Data manipulation and processing |
| Faker | Synthetic data generation |
| Streamlit | Interactive dashboard development |
| Plotly | Data visualization |

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- MySQL Server
- Git

### 1. Clone the repository

```bash
git clone https://github.com/PavanKumarVNL/hospitality_analytics.git
cd hospitality_analytics
```

### 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Prepare the data

Place the following aggregate CSV files inside the project's `data/` directory:

```text
data/
├── agg_hotel_monthly_performance.csv
├── agg_guest_satisfaction.csv
└── agg_employee_turnover.csv
```

These files are used directly by the Streamlit dashboard.

### 5. Run the dashboard

```bash
streamlit run app.py
```

The dashboard will be available locally at:

```text
http://localhost:8501
```

## 📁 Project Structure

```text
hospitality_analytics/
│
├── app.py
├── generate_data.py
├── requirements.txt
├── README.md
│
├── data/
│   ├── agg_hotel_monthly_performance.csv
│   ├── agg_guest_satisfaction.csv
│   └── agg_employee_turnover.csv
│
└── .gitignore
```

*Additional SQL scripts and database setup files can be included alongside these files.*

## 💡 Business Value

This project demonstrates how raw operational data can be transformed into meaningful business metrics.

By consolidating hotel performance into a single dashboard, management can:

- Monitor room utilization and revenue performance.
- Identify seasonal demand patterns.
- Compare hotel-level performance.
- Track guest satisfaction trends.
- Monitor workforce stability.
- Support data-driven operational decisions.

## ⚠️ Project Scope

This is an analytics project built using synthetically generated historical data. The dataset represents simulated hotel operations and does not contain actual customer or hotel business records.

The dashboard currently reads precomputed aggregate CSV files. It does not automatically synchronize with a live hotel management system or production database.

---

## 👨‍💻 Author

**Pavan Kumar V.**

GitHub: [PavanKumarVNL](https://github.com/PavanKumarVNL)

**Project:** Hospitality Analytics Platform

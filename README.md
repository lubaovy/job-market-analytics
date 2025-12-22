# Job Market Analytics – Vietnam IT Jobs 🇻🇳

A data analytics pipeline that collects, normalizes, and analyzes IT job postings
from major Vietnamese job platforms to identify **top skills, salary trends, and market demand**.

## 🎯 Project Objective
Build an end-to-end data pipeline to answer questions such as:
- What are the most in-demand IT skills in Vietnam?
- Which skills are associated with higher salaries?
- Skill trends across platforms (ITViec, TopCV, VietnamWorks)

This project is designed as a **data/analytics portfolio project**.

---

## 🧱 Data Sources
| Platform | Type | Tech |
|--------|------|------|
| ITViec | IT-focused job board | Selenium |
| TopCV | Multi-industry job board | Selenium |
| VietnamWorks | Multi-industry job board | Selenium |

---

## 🏗️ Project Structure

JOB-MARKET-ANALYTICS/
│
├── raw_data/ # Raw scraped data (ignored in git)
│ ├── itviec_raw.jsonl
│ ├── topcv_raw.jsonl
│ └── vietnamworks_raw.jsonl
│
├── scrapers/ # Scraping logic
│ ├── base_scraper.py
│ ├── itviec_scraper.py
│ ├── topcv_scraper.py
│ └── vietnamworks_scraper.py
│
├── run_raw_scraper.py # Crawl & store raw job data
├── normalize_jobs.py # Normalize raw jobs into unified schema
├── extract_skills.py # Extract skills for analytics
├── requirements.txt
└── README.md

yaml
Sao chép mã

---

## ⚙️ Tech Stack
- Python
- BeautifulSoup
- Selenium
- JSONL
- (Next steps: PostgreSQL, dbt, Metabase)

---

## 🔄 Data Pipeline

1. **Scraping**
   - Crawl IT job listings from 3 platforms
   - Store raw data in JSONL format

2. **Normalization**
   - Convert platform-specific fields into a unified schema
   - Clean salary, location, and description fields

3. **Skill Extraction**
   - Extract technical skills from job descriptions
   - Aggregate skill frequency for dashboards

---

## 📊 Example Use Cases
- Dashboard: **Top IT Skills in Vietnam (2025)**
- Salary analysis by skill
- Platform comparison

---

## ⚠️ Notes
- Raw data is excluded from GitHub due to size and scraping policies.
- This project is for **educational & portfolio purposes only**.

---

## 🚀 Future Improvements
- Store data in PostgreSQL
- Orchestrate pipeline using Airflow
- Build dashboard with Metabase / Power BI
- Salary prediction using ML

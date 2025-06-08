<p align="center">
  <img src="assets/banner.png" alt="Paris Urban Activity Analysis Banner" />
</p>

<p align="center">
  <a href="https://github.com/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy/stargazers">
    <img src="https://img.shields.io/github/stars/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy?style=flat-square" alt="GitHub Stars"/>
  </a>
  <a href="https://github.com/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy/network/members">
    <img src="https://img.shields.io/github/forks/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy?style=flat-square" alt="GitHub Forks"/>
  </a>
  <a href="https://github.com/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy/issues">
    <img src="https://img.shields.io/github/issues/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy?style=flat-square" alt="GitHub Issues"/>
  </a>
  <a href="https://github.com/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy/commits">
    <img src="https://img.shields.io/github/commit-activity/t/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy?style=flat-square" alt="Commit Activity"/>
  </a>
  <a href="https://github.com/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy">
    <img src="https://img.shields.io/github/languages/top/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy?style=flat-square" alt="Top Language"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License"/>
  </a>
</p>

# Paris Urban Activity Analysis for Commercial Location Strategy

## Table of Contents
- [About](#about)
- [Features](#features)
- [Demo](#demo)
- [Technologies](#technologies)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## About
This repository provides a comprehensive exploratory and spatial analysis of Paris urban activity—combining pedestrian zones, bike counters, and commercial data—to identify optimal locations for new business ventures and marketing campaigns.

---

## Features
- **Automated ETL Pipeline**  
  Extracts, transforms, and loads multiple Paris open datasets into a unified format.
- **Geo-Spatial Analysis**  
  Maps pedestrian zones, bike traffic, and retail points to uncover spatial patterns.
- **Interactive Dashboards**  
  Power BI reports for ad-hoc exploration and presentation-ready visuals.
- **Reproducible Environment**  
  Dockerized setup ensures consistent dependencies across systems.

---

## Demo
<p align="center">
  <img src="assets/dashboard_preview.png" alt="Dashboard Preview" width="700"/>
</p>

---

## Technologies
- **Python 3.8+** — Jupyter, Pandas, GeoPandas  
- **Power BI** — Interactive reporting  
- **Docker** — Containerization for reproducible analysis  
- **GitHub Actions** — CI checks (future)

---

## Project Structure
```
Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy/
├── assets/                # Images for README & dashboard previews
├── ETL/                   # Extract, Transform, Load scripts
│   ├── extract.py
│   ├── transform.py
│   └── load.py
├── analysis/              # Jupyter notebooks
│   ├── 01_data_overview.ipynb
│   ├── 02_spatial_analysis.ipynb
│   └── 03_dashboard_prep.ipynb
├── docker/                # Dockerfile & supporting scripts
├── dashboard.pbix         # Power BI dashboard file
├── requirements.txt       # Python dependencies
└── README.md              # This file
```

---

## Installation

1. **Clone the repository**  
   ```bash
   git clone https://github.com/HamzaChaieb-git/Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy.git
   cd Paris-Urban-Activity-Analysis-for-Commercial-Location-Strategy
   ```

2. **Create & activate a virtual environment** (Python 3.8+)  
   ```bash
   python -m venv venv
   source venv/bin/activate      # macOS/Linux
   venv\Scripts\activate       # Windows
   ```

3. **Install dependencies**  
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. **Run the ETL pipeline**  
   ```bash
   python ETL/extract.py && python ETL/transform.py && python ETL/load.py
   ```

2. **Launch Jupyter Notebooks**  
   ```bash
   jupyter notebook
   ```
   Explore notebooks under the `analysis/` directory.

3. **Open the Power BI dashboard**  
   - Directly in Power BI Desktop by opening `dashboard.pbix`, or  
   - Build & serve via Docker:  
     ```bash
     docker build -t paris-urban-analysis .
     docker run -p 8888:8888 paris-urban-analysis
     ```

---

## Contributing
Contributions are welcome!  

1. Fork this repository  
2. Create a branch:  
   ```bash
   git checkout -b feature/YourFeatureName
   ```
3. Commit your changes:  
   ```bash
   git commit -m "Add awesome feature"
   ```
4. Push to your fork:  
   ```bash
   git push origin feature/YourFeatureName
   ```
5. Open a Pull Request  

---

## License
This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Contact
**Hamza Chaieb**  
- GitHub: [@HamzaChaieb-git](https://github.com/HamzaChaieb-git)  
- Email: hamza.chaieb@example.com  


# 🔬 Automated Biomedical Data Analysis Pipeline

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://biomedical-analysis-pipeline-dadamaryoluwatobi.streamlit.app/)
)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A fully automated, end-to-end statistical analysis and reporting pipeline designed for biomedical researchers, pharmacologists, and biologists. 

Upload your raw experimental data (CSV), and this tool will automatically check statistical assumptions, run the correct tests, generate publication-grade plots, and compile everything into a beautifully written Microsoft Word document.

## ✨ Key Features

* **🧠 Smart Test Selection:** Automatically runs Shapiro-Wilk (normality) and Levene's (homogeneity) tests. Routes data to One-Way ANOVA (if assumptions pass) or Kruskal-Wallis (if assumptions fail).
**📊 Comprehensive Post-Hocs:** Performs Tukey HSD (parametric) or Dunn's Test with Holm correction (non-parametric) and calculates Cohen's *d* effect sizes.
**🌋 Global Treatment Effects:** Automatically calculates Log2 Fold Change and p-values relative to your designated Control group to generate global **Volcano Plots**.
**📝 Automated Narratives:** Translates raw p-values and effect sizes into publication-ready, plain-English paragraphs. No more digging through massive stats tables!
**📈 Publication-Grade Visuals:** Generates annotated bar plots (with 95% CIs), box/swarm plots, and correlation heatmaps with automated significance brackets (*, **, ***).
* **📄 One-Click Word Export:** Compiles all statistical narratives, tables, and high-res images into a cleanly formatted `.docx` file.

## 🚀 Live Web App
You don't need to install any code to use this tool! You can access the live web interface here:
**👉(https://biomedical-analysis-pipeline-dadamaryoluwatobi.streamlit.app/)**

## 💻 Running Locally

If you prefer to run the pipeline on your local machine (for sensitive or HIPAA-compliant offline data), follow these steps:

**1. Clone the repository:**
```bash
git clone [https://github.com/Thorbiedee/biomedical-analysis-pipeline.git]
cd biomedical-analysis-pipeline

```

**2. Install the required dependencies:**

```bash
pip install -r requirements.txt

```

**3. Launch the Streamlit Interface:**

```bash
streamlit run app.py

```

## 📂 Data Formatting Guide

To ensure the pipeline runs smoothly, your `.csv` file should be formatted with rows as individual samples/animals, and columns as parameters.

**Required Columns:**

1. **Sample ID:** A unique identifier for the animal/sample (e.g., `Rat_01`).
2. **Treatment Group:** The group the sample belongs to (e.g., `Control`, `Dose_50mg`, `Vehicle`).
3. **Parameters:** All subsequent columns should be your numeric data (e.g., `Blood Glucose (mg/dL)`, `Weight (g)`).

*Note: The pipeline automatically strips text/units from numeric cells, so values like `120 mg/dL` will be safely processed as `120`.*

## 🏗️ Project Architecture

This project is built using a modular, Object-Oriented framework:

* `app.py`: The Streamlit web interface and user routing.
* `data_loader.py`: Handles CSV ingestion, regex cleaning, and dataframe mapping.
* `analyzer.py`: The statistical brain. Handles assumptions, ANOVAs, post-hocs, and narrative generation.
* `visualizer.py`: Generates the Matplotlib and Seaborn charts (Bar, Box, Heatmap, Volcano).
* `reporter.py`: Compiles the final Microsoft Word (`.docx`) report.
* `utils.py`: Mathematical helper functions (Effect sizes, Confidence Intervals, etc.).

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://www.google.com/search?q=../../issues).

## 📄 License

This project is open-source and available under the [MIT License](https://www.google.com/search?q=LICENSE).

```

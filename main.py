# File: main.py

import os
from data_loader import ExperimentDataLoader
from analyzer import MultiParameterAnalyzer
from reporter import create_report

# ==========================================
# CRITICAL: SET YOUR CONTROL GROUP NAME HERE
# It must match the spelling in your CSV exactly!
# ==========================================
CONTROL_GROUP = "Control"  # Change this if your CSV says "Sham", "Vehicle", etc.

if __name__ == "__main__":
    filepath = r"C:\Users\USER\Documents\Python analysis\Blood assay\Multiple glucose parameters.csv"
    
    if not os.path.exists(filepath):
        print(f"❌ Error: Could not find the file at {filepath}")
        exit()

    data_dir = os.path.dirname(filepath)
    base_name = os.path.splitext(os.path.basename(filepath))[0]
    plot_dir = os.path.join(data_dir, f"{base_name}_plots")
    os.makedirs(plot_dir, exist_ok=True)
    report_path = os.path.join(data_dir, f"{base_name}_advanced_report.docx")

    print(f"Loading data from: {filepath}...")

    loader = ExperimentDataLoader(filepath)
    data = loader.load()
    parameters = loader.get_numeric_parameters()

    if not parameters:
        print("❌ Error: No numeric columns found.")
        exit()

    print(f"Found {len(parameters)} parameters to analyze. Running statistics...")
    analyzer = MultiParameterAnalyzer(data, loader.group_col)
    
    stats_list, p_values_list, posthoc_list, results_text_list, ci_list = [], [], [], [], []
    
    for param in parameters:
        stats_df, p_val, posthoc, results_text, ci_dict = analyzer.analyze_parameter(param)
        stats_list.append(stats_df)
        p_values_list.append(p_val)
        posthoc_list.append(posthoc)
        results_text_list.append(results_text)
        ci_list.append(ci_dict)

    # Global computations
    corr_matrix, corr_narrative = analyzer.compute_correlations(parameters)
    volcano_results, volcano_narratives = analyzer.compute_volcano_data(parameters, CONTROL_GROUP)

    print("Generating Word document and plotting graphs...")
    create_report(
        analyzer=analyzer, 
        stats_list=stats_list, 
        p_values_list=p_values_list, 
        posthoc_list=posthoc_list, 
        results_text_list=results_text_list, 
        ci_list=ci_list, 
        plot_dir=plot_dir, 
        report_path=report_path, 
        corr_matrix=corr_matrix,
        corr_narrative=corr_narrative,
        volcano_results=volcano_results,
        volcano_narratives=volcano_narratives,
        control_group=CONTROL_GROUP
    )
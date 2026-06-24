# File: app.py

import streamlit as st
import pandas as pd
import os
import tempfile
from data_loader import ExperimentDataLoader
from analyzer import MultiParameterAnalyzer
from reporter import create_report

# --- UI Setup ---
st.set_page_config(page_title="Biomedical Analysis Pipeline", page_icon="🔬", layout="wide")
st.title("🔬 Automated Biomedical Data Analysis")
st.markdown("Upload your experimental data, and this pipeline will automatically check assumptions, run the appropriate statistical tests (ANOVA/Kruskal-Wallis), generate post-hoc analyses, plot the results, and compile a publication-ready Word document.")

# --- Sidebar Controls ---
st.sidebar.header("1. Upload Data")
uploaded_file = st.sidebar.file_uploader("Upload CSV File", type=['csv'])

if uploaded_file is not None:
    # Load a preview of the data to populate dropdowns
    df_preview = pd.read_csv(uploaded_file)
    
    st.sidebar.header("2. Data Mapping")
    # Let the user tell the app which column is which
    sample_col = st.sidebar.selectbox("Which column contains Sample/Animal IDs?", df_preview.columns)
    group_col = st.sidebar.selectbox("Which column contains the Treatment Groups?", df_preview.columns)
    
    # Dynamically find the unique groups so the user can select the baseline/control
    unique_groups = df_preview[group_col].dropna().unique()
    control_group = st.sidebar.selectbox("Select the Baseline/Control Group (for Volcano Plots):", unique_groups)

    st.sidebar.header("3. Run Analysis")
    run_button = st.sidebar.button("🚀 Run Pipeline", type="primary")

    # --- Main Screen Preview ---
    st.subheader("Data Preview")
    st.dataframe(df_preview.head())

    # --- Execution Logic ---
    if run_button:
        # We create a temporary directory to safely store the files while the app is running
        with tempfile.TemporaryDirectory() as temp_dir:
            
            # 1. Save the uploaded file to the temporary directory so our DataLoader can read it
            temp_csv_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_csv_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            # 2. Set up the paths for the plots and the final report
            base_name = os.path.splitext(uploaded_file.name)[0]
            plot_dir = os.path.join(temp_dir, f"{base_name}_plots")
            os.makedirs(plot_dir, exist_ok=True)
            report_path = os.path.join(temp_dir, f"{base_name}_Advanced_Report.docx")

            # 3. RUN THE PIPELINE (With a loading spinner so the user knows it's working)
            with st.spinner("Crunching the numbers... This might take a few seconds."):
                
                # Load Data
                loader = ExperimentDataLoader(temp_csv_path, sample_col=sample_col, group_col=group_col)
                data = loader.load()
                parameters = loader.get_numeric_parameters()

                if not parameters:
                    st.error("No numeric columns found to analyze. Please check your CSV.")
                    st.stop()

                # Analyze Data
                analyzer = MultiParameterAnalyzer(data, loader.group_col)
                stats_list, p_values_list, posthoc_list, results_text_list, ci_list = [], [], [], [], []
                
                # Progress bar for visual feedback
                progress_bar = st.progress(0)
                for idx, param in enumerate(parameters):
                    stats_df, p_val, posthoc, results_text, ci_dict = analyzer.analyze_parameter(param)
                    stats_list.append(stats_df)
                    p_values_list.append(p_val)
                    posthoc_list.append(posthoc)
                    results_text_list.append(results_text)
                    ci_list.append(ci_dict)
                    
                    progress_bar.progress((idx + 1) / len(parameters))

                # Global computations (Correlations & Volcano)
                corr_matrix, corr_narrative = analyzer.compute_correlations(parameters)
                volcano_results, volcano_narratives = analyzer.compute_volcano_data(parameters, control_group)

                # Generate the Word Document
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
                    control_group=control_group
                )

            # --- Results Presentation ---
            st.success("✅ Analysis Complete!")
            
            # Provide a large button to download the generated Word Document
            with open(report_path, "rb") as file:
                st.download_button(
                    label="📄 Download Advanced Word Report",
                    data=file,
                    file_name=f"{base_name}_Report.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

            # Optional: Display the Volcano Plots directly in the web app!
            if volcano_results:
                st.subheader("Global Treatment Effects")
                cols = st.columns(len(volcano_results))
                for idx, (trt, v_df) in enumerate(volcano_results.items()):
                    with cols[idx]:
                        # Load the plot image we just generated and display it in the app
                        from utils import sanitize_filename
                        safe_trt = sanitize_filename(trt)
                        volcano_img_path = os.path.join(plot_dir, f"volcano_{safe_trt}.png")
                        if os.path.exists(volcano_img_path):
                            st.image(volcano_img_path, caption=f"{trt} vs {control_group}")

else:
    st.info("👈 Please upload a CSV file in the sidebar to begin.")
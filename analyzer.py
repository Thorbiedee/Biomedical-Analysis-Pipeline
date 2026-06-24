# File: analyzer.py

import pandas as pd
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd
import scikit_posthocs as sp
from utils import (eta_squared, omega_squared, confidence_interval_mean, 
                   cohen_d, interpret_cohens_d, interpret_omega_squared, interpret_pearson_r)

class MultiParameterAnalyzer:
    def __init__(self, data, group_col):
        self.data = data
        self.group_col = group_col
        self.correlation_matrix = None

    def assumption_tests(self, df, parameter):
        normality = {}
        for group, vals in df.groupby(self.group_col)[parameter]:
            stat, p = stats.shapiro(vals)
            normality[group] = (p > 0.05, p)  

        group_arrays = [vals for name, vals in df.groupby(self.group_col)[parameter]]
        stat, p_levene = stats.levene(*group_arrays)
        homogeneity = (p_levene > 0.05) 
        return normality, homogeneity, p_levene

    def detect_outliers_iqr(self, series):
        Q1 = series.quantile(0.25) 
        Q3 = series.quantile(0.75) 
        IQR = Q3 - Q1
        lower = Q1 - 1.5 * IQR
        upper = Q3 + 1.5 * IQR
        outliers = series[(series < lower) | (series > upper)]
        return outliers.index.tolist()

    def analyze_parameter(self, parameter):
        df = self.data[[self.group_col, parameter]].dropna()
        stats_df = df.groupby(self.group_col)[parameter].agg(['mean','std','count']).reset_index()
        stats_df.rename(columns={'mean':'Mean','std':'SD','count':'n'}, inplace=True)
        stats_df['Parameter'] = parameter

        normality, homogeneity, p_levene = self.assumption_tests(df, parameter)
        outliers = self.detect_outliers_iqr(df[parameter])
        parametric = all(v[0] for v in normality.values()) and homogeneity

        groups = df[self.group_col].unique()
        group_data_dict = {g: df[df[self.group_col]==g][parameter] for g in groups}
        group_data = list(group_data_dict.values())

        narrative = f"Statistical Narrative for {parameter}:\n"
        if len(outliers) > 0: narrative += f"- Outlier Check: {len(outliers)} potential outliers were detected via the IQR method.\n"
        
        failed_shapiro = [g for g, (ok, p) in normality.items() if not ok]
        if parametric:
            narrative += "- Assumptions: Passed Shapiro-Wilk and Levene's test. Parametric One-Way ANOVA was used.\n"
        else:
            narrative += "- Assumptions: Assumptions violated. Kruskal-Wallis test was used to maintain rigor.\n"

        f_stat = p_val = omega = eta = None
        posthoc_results = [] 

        if parametric and len(groups) > 1:
            f_res = stats.f_oneway(*group_data)
            f_stat = f_res.statistic
            p_val = f_res.pvalue
            df_between = len(groups) - 1
            df_within = len(df) - len(groups)
            omega = omega_squared(f_stat, df_between, df_within, len(df))
            effect_str = interpret_omega_squared(omega)
            
            if p_val < 0.05:
                narrative += f"- Main Effect: Significant difference found (F={f_stat:.2f}, p={p_val:.4f}). Effect size: {effect_str} (ω²={omega:.3f}).\n"
                tukey = pairwise_tukeyhsd(endog=df[parameter], groups=df[self.group_col], alpha=0.05)
                narrative += "- Post-Hoc Analysis (Tukey HSD):\n"
                for res in tukey.summary().data[1:]:
                    g1, g2, meandiff, p_adj, lower, upper, reject = res
                    if reject:
                        posthoc_results.append((g1, g2, p_adj))
                        d_val = abs(cohen_d(group_data_dict[g1], group_data_dict[g2]))
                        d_interp = interpret_cohens_d(d_val)
                        narrative += f"   • {g1} vs {g2}: Significant difference (p={p_adj:.4f}), Effect Size: d={d_val:.2f} [{d_interp}].\n"
            else:
                narrative += f"- Main Effect: No significant difference between groups (F={f_stat:.2f}, p={p_val:.4f}).\n"
                
        else:
            kruskal = stats.kruskal(*group_data)
            p_val = kruskal.pvalue
            if p_val < 0.05:
                narrative += f"- Main Effect: Significant difference found (H={kruskal.statistic:.2f}, p={p_val:.4f}).\n"
                narrative += "- Post-Hoc Analysis (Dunn's Test with Holm correction):\n"
                dunn_df = sp.posthoc_dunn(df, val_col=parameter, group_col=self.group_col, p_adjust='holm')
                groups_list = list(dunn_df.columns)
                for i in range(len(groups_list)):
                    for j in range(i+1, len(groups_list)):
                        g1, g2 = groups_list[i], groups_list[j]
                        p_adj = dunn_df.loc[g1, g2]
                        if p_adj < 0.05:
                            posthoc_results.append((g1, g2, p_adj)) 
                            narrative += f"   • {g1} vs {g2}: Significant difference (p={p_adj:.4f}).\n"
            else:
                narrative += f"- Main Effect: No significant difference between groups (H={kruskal.statistic:.2f}, p={p_val:.4f}).\n"

        ci_dict = {}
        for g, vals in df.groupby(self.group_col)[parameter]:
            ci_dict[g] = confidence_interval_mean(vals)
        return stats_df, p_val, posthoc_results, narrative, ci_dict

    def compute_correlations(self, parameter_list):
        numeric_data = self.data[parameter_list].dropna()
        self.correlation_matrix = numeric_data.corr(method='pearson')
        narrative = "Correlation Analysis Narrative:\n"
        significant_pairs = []
        cols = numeric_data.columns
        for i in range(len(cols)):
            for j in range(i+1, len(cols)):
                col1, col2 = cols[i], cols[j]
                r, p_val = stats.pearsonr(numeric_data[col1], numeric_data[col2])
                if p_val < 0.05: significant_pairs.append((col1, col2, r, p_val))
        if not significant_pairs:
            narrative += "No statistically significant linear correlations were found.\n"
        else:
            significant_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            narrative += f"Found {len(significant_pairs)} significant correlation(s). The top relationships are:\n"
            for col1, col2, r, p_val in significant_pairs[:10]:
                direction = "positive" if r > 0 else "negative"
                strength = interpret_pearson_r(r)
                narrative += f"   • {col1} & {col2}: {strength} {direction} correlation (r={r:.3f}, p={p_val:.4f}).\n"
        return self.correlation_matrix, narrative

    # --- NEW: Volcano Calculator ---
    def compute_volcano_data(self, parameter_list, control_group):
        """Calculates Fold Change and P-values for every treatment against a Control anchor."""
        volcano_results = {}
        narratives = {}
        
        groups = self.data[self.group_col].unique()
        if control_group not in groups:
            return None, None # Control group wasn't found in data
            
        treatments = [g for g in groups if g != control_group]
        
        for trt in treatments:
            results = []
            upregulated, downregulated = [], []
            
            for param in parameter_list:
                df_param = self.data[[self.group_col, param]].dropna()
                ctrl_data = df_param[df_param[self.group_col] == control_group][param]
                trt_data = df_param[df_param[self.group_col] == trt][param]
                
                if len(ctrl_data) < 2 or len(trt_data) < 2: continue
                    
                mean_ctrl = ctrl_data.mean()
                mean_trt = trt_data.mean()
                
                # Math: Fold Change. Add 1e-6 to avoid dividing by absolute zero.
                fc = (mean_trt + 1e-6) / (mean_ctrl + 1e-6)
                log2fc = np.log2(fc)
                
                # Math: Independent MWU test for the specific Volcano P-value
                stat, p_val = stats.mannwhitneyu(trt_data, ctrl_data, alternative='two-sided')
                p_val = max(p_val, 1e-50) # Prevent true zero from breaking the Log10 math
                
                results.append({'Parameter': param, 'Log2FC': log2fc, 'p_value': p_val})
                
                if p_val < 0.05:
                    if log2fc > 0.58: upregulated.append(param)     # 0.58 is log2(1.5x fold change)
                    elif log2fc < -0.58: downregulated.append(param)
                        
            if not results: continue
            
            volcano_df = pd.DataFrame(results)
            volcano_results[trt] = volcano_df
            
            narrative = f"Volcano Analysis: Comparing '{trt}' globally to baseline '{control_group}':\n"
            if upregulated: narrative += f"   • Significantly Upregulated (>1.5x): {', '.join(upregulated)}\n"
            if downregulated: narrative += f"   • Significantly Downregulated (<1.5x): {', '.join(downregulated)}\n"
            if not upregulated and not downregulated: narrative += "   • No parameters were significantly up- or down-regulated beyond the 1.5x threshold.\n"
                
            narratives[trt] = narrative
            
        return volcano_results, narratives
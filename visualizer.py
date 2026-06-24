# File: visualizer.py

import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from utils import significance_stars

sns.set_theme(style="whitegrid")

def draw_significance_brackets(df, parameter, groups, posthoc_results, ax):
    if not posthoc_results: return
    y_max = df[parameter].max()
    y_base = y_max + (df[parameter].std() * 0.3)
    bracket_height = y_max * 0.02
    step_up = y_max * 0.1  
    group_list = list(groups)

    for g1, g2, p_adj in posthoc_results:
        x1 = group_list.index(g1)
        x2 = group_list.index(g2)
        plt.plot([x1, x1, x2, x2], [y_base, y_base + bracket_height, y_base + bracket_height, y_base], lw=1.5, color='black')
        plt.text((x1 + x2) * 0.5, y_base + bracket_height, significance_stars(p_adj), ha='center', va='bottom', color='black', fontsize=12)
        y_base += step_up

def plot_bar(df, parameter, group_col, save_path, p_val=None, posthoc_results=None, ci_dict=None):
    plt.figure(figsize=(max(7, len(df[group_col].unique()) * 1.0), 6))
    means = df.groupby(group_col)[parameter].mean()
    groups = df[group_col].unique()
    
    ax = sns.barplot(x=group_col, y=parameter, data=df, hue=group_col, dodge=False, palette='muted', errorbar=None, legend=False)
    
    if ci_dict:
        for i, g in enumerate(groups):
            lower_err = means[g] - ci_dict[g][0]
            upper_err = ci_dict[g][1] - means[g]
            plt.errorbar(i, means[g], yerr=[[lower_err], [upper_err]], fmt='none', color='black', capsize=5)

    if posthoc_results:
        draw_significance_brackets(df, parameter, groups, posthoc_results, ax)
    elif p_val and p_val < 0.05:
        y_top = df[parameter].max() + (df[parameter].std() * 0.5)
        plt.text(len(groups)/2 - 0.5, y_top, f"Main Effect: {significance_stars(p_val)}", ha='center', color='red', fontsize=10)

    plt.title(f'{parameter} by {group_col}')
    plt.ylabel(parameter)
    plt.xlabel(group_col)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_box(df, parameter, group_col, save_path, p_val=None, posthoc_results=None):
    plt.figure(figsize=(max(7, len(df[group_col].unique()) * 1.0), 6))
    groups = df[group_col].unique()
    
    ax = sns.boxplot(x=group_col, y=parameter, data=df, hue=group_col, dodge=False, palette='muted', legend=False)
    sns.swarmplot(x=group_col, y=parameter, data=df, color=".25", alpha=0.6, legend=False)
    
    if posthoc_results:
        draw_significance_brackets(df, parameter, groups, posthoc_results, ax)
    elif p_val and p_val < 0.05:
        y_top = df[parameter].max() + (df[parameter].std() * 0.5)
        plt.text(len(groups)/2 - 0.5, y_top, f"Main Effect: {significance_stars(p_val)}", ha='center', color='red', fontsize=10)
                 
    plt.title(f'{parameter} by {group_col} (Boxplot)')
    plt.ylabel(parameter)
    plt.xlabel(group_col)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches='tight')
    plt.close()

def plot_heatmap(corr_matrix, save_path):
    plt.figure(figsize=(max(6, corr_matrix.shape[1]), max(5, corr_matrix.shape[0])))
    sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', vmin=-1, vmax=1)
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

# --- NEW: Volcano Plot ---
def plot_volcano(df, treatment_name, control_name, save_path):
    plt.figure(figsize=(8, 6))
    
    # Calculate the Y-axis (-log10 of p-value)
    df['neg_log10_p'] = -np.log10(df['p_value'])
    
    # Thresholds: p < 0.05, Fold Change > 1.5x (Log2FC roughly 0.58)
    p_thresh = -np.log10(0.05)
    fc_thresh = 0.58 
    
    # Color mapping: Red (Up), Blue (Down), Gray (Not Significant)
    conditions = [
        (df['neg_log10_p'] >= p_thresh) & (df['Log2FC'] >= fc_thresh),
        (df['neg_log10_p'] >= p_thresh) & (df['Log2FC'] <= -fc_thresh),
        (df['neg_log10_p'] < p_thresh) | (df['Log2FC'].abs() < fc_thresh)
    ]
    choices = ['red', 'blue', 'gray']
    df['color'] = np.select(conditions, choices, default='gray')
    
    plt.scatter(df['Log2FC'], df['neg_log10_p'], c=df['color'], alpha=0.7, edgecolors='k', s=80)
    
    # Draw threshold lines
    plt.axhline(y=p_thresh, color='k', linestyle='--', alpha=0.5)
    plt.axvline(x=fc_thresh, color='k', linestyle='--', alpha=0.5)
    plt.axvline(x=-fc_thresh, color='k', linestyle='--', alpha=0.5)
    
    # Label the dots that are significant
    sig_df = df[df['color'] != 'gray']
    for idx, row in sig_df.iterrows():
        plt.text(row['Log2FC'], row['neg_log10_p'] + 0.05, row['Parameter'], ha='center', va='bottom', fontsize=9)
        
    plt.title(f'Global Effect: {treatment_name} vs {control_name}')
    plt.xlabel('Log2 Fold Change (Effect Size)')
    plt.ylabel('-Log10 p-value (Significance)')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
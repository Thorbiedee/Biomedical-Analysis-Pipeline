# File: utils.py

import re
import numpy as np
from scipy import stats

def significance_stars(p):
    if p <= 0.0001: return "****"
    elif p <= 0.001: return "***"
    elif p <= 0.01: return "**"
    elif p <= 0.05: return "*"
    else: return "ns"

def cohen_d(x1, x2):
    n1, n2 = len(x1), len(x2)
    s1, s2 = np.var(x1, ddof=1), np.var(x2, ddof=1)
    pooled_sd = np.sqrt(((n1-1)*s1 + (n2-1)*s2) / (n1+n2-2))
    return (np.mean(x1) - np.mean(x2)) / pooled_sd

def eta_squared(f_stat, df_between, df_within):
    return (f_stat * df_between) / (f_stat * df_between + df_within)

def omega_squared(f_stat, df_between, df_within, n_total):
    return (f_stat - 1) * (df_between) / (f_stat + df_within + 1e-6)

def confidence_interval_mean(x, confidence=0.95):
    n = len(x)
    mean = np.mean(x)
    se = stats.sem(x)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return mean-h, mean+h

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "_", str(name))

# --- NEW: Qualitative Interpretations ---

def interpret_cohens_d(d):
    """Translates Cohen's d into standard plain-English effect sizes."""
    abs_d = abs(d)
    if abs_d < 0.2: return "Negligible"
    elif abs_d < 0.5: return "Small"
    elif abs_d < 0.8: return "Medium"
    else: return "Large"

def interpret_omega_squared(omega):
    """Translates Omega/Eta squared into standard plain-English effect sizes."""
    if omega < 0.01: return "Negligible"
    elif omega < 0.06: return "Small"
    elif omega < 0.14: return "Medium"
    else: return "Large"

def interpret_pearson_r(r):
    """Translates Pearson correlation r-values into plain English."""
    abs_r = abs(r)
    if abs_r < 0.3: return "Negligible"
    elif abs_r < 0.5: return "Weak"
    elif abs_r < 0.7: return "Moderate"
    elif abs_r < 0.9: return "Strong"
    else: return "Very Strong"
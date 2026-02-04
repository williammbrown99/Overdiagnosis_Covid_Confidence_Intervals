import numpy as np

# ---------------------------------------------------------
# 1. INPUT DATA (Caswell-Jin et al. 2022)
# ---------------------------------------------------------
# Format: [Mean, Lower_CI, Upper_CI]
# Units: Cases per 100,000 women

# X: Pre-COVID (Baseline)
# "19.3 (95% CI 19.1–19.5)"
data_pre = {'mean': 19.3, 'lower': 19.1, 'upper': 19.5}

# During Quarantine (April–May 2020)
# "11.6 (95% CI 10.8–12.4)"
data_during = {'mean': 11.6, 'lower': 10.8, 'upper': 12.4}

# Post-Quarantine (June 2020–Feb 2021)
# "19.7 (95% CI 19.3–20.1)"
data_post = {'mean': 19.7, 'lower': 19.3, 'upper': 20.1}


# ---------------------------------------------------------
# 2. HELPER FUNCTIONS
# ---------------------------------------------------------
def get_se_from_ci(lower, upper, confidence=0.95):
    """
    Converts a 95% Confidence Interval to Standard Error.
    Assumes approximate normality: Width = 2 * 1.96 * SE
    """
    z_score = 1.96 # Approx for 95%
    width = upper - lower
    se = width / (2 * z_score)
    return se

# ---------------------------------------------------------
# 3. CALCULATE STANDARD ERRORS (SE)
# ---------------------------------------------------------
se_pre = get_se_from_ci(data_pre['lower'], data_pre['upper'])
se_during = get_se_from_ci(data_during['lower'], data_during['upper'])
se_post = get_se_from_ci(data_post['lower'], data_post['upper'])

print(f"Calculated Standard Errors:")
print(f"  SE(Pre-COVID): {se_pre:.4f}")
print(f"  SE(During):    {se_during:.4f}")
print(f"  SE(Post):      {se_post:.4f}\n")


# ---------------------------------------------------------
# 4. POINT ESTIMATE CALCULATION
# ---------------------------------------------------------
# Variables for clearer reading
X_rate = data_pre['mean']
R_during = data_during['mean']
R_post = data_post['mean']

# Step 1: Calculate Excess
# "Excess... detected after quarantine" = Post_Rate - Pre_Rate
Excess = R_post - X_rate

# Step 2: Calculate Y (Incidence in absence of screening)
# "Y = Rate during quarantine + Excess"
Y_rate = R_during + Excess

# Step 3: Calculate Overdiagnosis Rate (O)
# O = (X - Y) / X
O_rate = (X_rate - Y_rate) / X_rate

print("-" * 50)
print("POINT ESTIMATES")
print("-" * 50)
print(f"X (Screening Rate):      {X_rate:.2f}")
print(f"Y (No-Screening Rate):   {Y_rate:.2f} (derived as {R_during} + {Excess:.2f})")
print(f"Overdiagnosis Rate (O):  {O_rate:.4f} ({O_rate*100:.2f}%)")


# ---------------------------------------------------------
# 5. ERROR PROPAGATION (DELTA METHOD)
# ---------------------------------------------------------
# We need the Variance of O.
# O = (X - Y) / X 
# Substituting Y = R_during + (R_post - X):
# O = (X - (R_during + R_post - X)) / X
# O = (2X - R_during - R_post) / X
# O = 2 - (R_during / X) - (R_post / X)

# Partial Derivatives of O with respect to inputs:
# dO/dX = (R_during + R_post) / X^2
# dO/dR_during = -1 / X
# dO/dR_post = -1 / X

term_during = R_during
term_post = R_post

# 1. Partial Derivative wrt X (Pre-COVID)
dO_dX = (term_during + term_post) / (X_rate ** 2)

# 2. Partial Derivative wrt R_during
dO_dDuring = -1 / X_rate

# 3. Partial Derivative wrt R_post
dO_dPost = -1 / X_rate

# Calculate Variance of O (Sum of squared derivatives * input variances)
# Var(A) = SE(A)^2
var_X = se_pre ** 2
var_during = se_during ** 2
var_post = se_post ** 2

var_O = (dO_dX**2 * var_X) + (dO_dDuring**2 * var_during) + (dO_dPost**2 * var_post)

# Standard Error of O
se_O = np.sqrt(var_O)

# ---------------------------------------------------------
# 6. FINAL RESULTS WITH CI
# ---------------------------------------------------------
# 95% CI = Estimate +/- 1.96 * SE
ci_lower = O_rate - (1.96 * se_O)
ci_upper = O_rate + (1.96 * se_O)

print("\n" + "-" * 50)
print("FINAL RESULTS (With Error Propagation)")
print("-" * 50)
print(f"Overdiagnosis Estimate:  {O_rate*100:.2f}%")
print(f"Standard Error (SE):     {se_O*100:.2f}%")
print(f"95% Confidence Interval: ({ci_lower*100:.2f}%, {ci_upper*100:.2f}%)")
print("-" * 50)
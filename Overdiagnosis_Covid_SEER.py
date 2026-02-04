import pandas as pd
import numpy as np

# ---------------------------------------------------------
# SETUP & CONFIGURATION
# ---------------------------------------------------------
# Set display options for cleaner output
pd.options.display.float_format = '{:.2f}'.format
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

# Load the dataset
# Ensure 'SEER_DATA.csv' is in the same folder as this script
df = pd.read_csv("SEER_DATA.csv")

# Define Year Groups
baseline_years = [2016, 2017, 2018, 2019]
covid_year = 2020
rebound_years = [2021, 2022]

# ---------------------------------------------------------
# PART 1: MAIN ANALYSIS (Lead Time = 2 Years, p = 0%)
# ---------------------------------------------------------
print("=" * 80)
print("PART 1: MAIN OVERDIAGNOSIS ESTIMATES (Lead Time=2y, Avoidance=0%)")
print("=" * 80)

# 1. Baseline (X) and 2020 (Z)
df_baseline = df[df["Year"].isin(baseline_years)]
X = df_baseline.drop(columns=["Year"]).mean()
Z = df[df["Year"] == covid_year].drop(columns=["Year"]).iloc[0]

# 2. Rebound Years
rates_2021 = df[df['Year'] == 2021].drop(columns=['Year']).iloc[0]
rates_2022 = df[df['Year'] == 2022].drop(columns=['Year']).iloc[0]

# 3. Calculate Derived Metrics (M, C, T)
M = X / 12
C = Z - (M * 9)
T = C * 4

# 4. Calculate D (Decrease in 2020)
dec_2020 = X - Z
D = dec_2020.shift(-1).fillna(0)

# 5. Calculate B (Standard Increase 21+22)
inc_combined = (rates_2021 - X) + (rates_2022 - X)
B = inc_combined.shift(-1).fillna(0)

# 6. Calculate Excess (E), No-Screen Rate (Y), and Overdiagnosis (O)
E = B - D
Y = T + E
O_rate = (X - Y) / X

# 7. Construct and Print Main Table
main_results = pd.DataFrame({
    'Baseline (X)': X,
    'No-Screen Rate (Y)': Y,
    'Overdiagnosis %': O_rate * 100
})

# Add Total Row
total_X = X.sum()
total_Y = Y.sum()
total_O_pct = ((total_X - total_Y) / total_X) * 100

main_results.loc['Total'] = [total_X, total_Y, total_O_pct]
print(main_results)
print("\n")


# ---------------------------------------------------------
# PART 2: SENSITIVITY ANALYSIS (Lead Time & Avoidance)
# ---------------------------------------------------------
print("=" * 80)
print("PART 2: SENSITIVITY ANALYSIS")
print("=" * 80)

lead_times = [2, 4, 7]         # Years
avoidance_rates = [0.00, 0.05, 0.12] # 0%, 5%, 12%

sensitivity_rows = []

for lt in lead_times:
    for p in avoidance_rates:
        
        # A. Calculate Excess (E) based on Lead Time
        if lt == 2:
            # Standard: E = B - D
            E_sens = B - D
        else:
            # Extended: E(LT) = N + K * (LT - 1) - D
            inc_2021 = rates_2021 - X
            N = inc_2021.shift(-1).fillna(0)
            
            inc_2022 = rates_2022 - X
            K = inc_2022.shift(-1).fillna(0)
            
            E_sens = N + (K * (lt - 1)) - D
            
        # B. Calculate Y (No-Screen Rate)
        Y_raw = T + E_sens
        
        # C. Adjust for Healthcare Avoidance (p)
        # Y(p) = (X - Y) * p + Y
        Y_adj = (X - Y_raw) * p + Y_raw
        
        # D. Calculate Overdiagnosis Rates for this scenario
        O_series = (X - Y_adj) / X
        
        # E. Calculate TOTAL Overdiagnosis for this scenario
        sum_X = X.sum()
        sum_Y_adj = Y_adj.sum()
        total_scenario_O = (sum_X - sum_Y_adj) / sum_X
        
        # F. Format Row for Display
        row_data = {
            'Lead Time': f"{lt} years",
            'Avoidance (p)': f"{p*100:.0f}%",
            '< 1cm': O_series['< 1cm'] * 100,
            '1 - 1.9 cm': O_series['1 - 1.9 cm'] * 100,
            '2 - 2.9 cm': O_series['2 - 2.9 cm'] * 100,
            '3 - 3.9 cm': O_series['3 - 3.9 cm'] * 100,
            '4 - 4.9 cm': O_series['4 - 4.9 cm'] * 100,
            '5+ cm': O_series['5+ cm'] * 100,
            'Total': total_scenario_O * 100
        }
        sensitivity_rows.append(row_data)

sensitivity_df = pd.DataFrame(sensitivity_rows)
sensitivity_df = sensitivity_df.set_index(['Lead Time', 'Avoidance (p)'])
print(sensitivity_df)
print("\n")


# ---------------------------------------------------------
# PART 3: BOOTSTRAP CONFIDENCE INTERVAL (For Main Estimate)
# ---------------------------------------------------------
print("=" * 80)
print(f"PART 3: BOOTSTRAP ANALYSIS (Target: {total_O_pct:.2f}%)")
print("Running 10,000 iterations (resampling baseline & rebound years)...")
print("=" * 80)

n_iterations = 10000
bootstrap_estimates = []
np.random.seed(42)  # Fixed seed for reproducibility

for i in range(n_iterations):
    # 1. Resample Baseline Years (4 years with replacement)
    resampled_base = np.random.choice(baseline_years, size=4, replace=True)
    rows_base = [df[df['Year'] == y] for y in resampled_base]
    df_boot_base = pd.concat(rows_base)
    
    # Calculate X_boot (Rounded to 3 decimals)
    X_boot = df_boot_base.drop(columns=["Year"]).mean().round(3)
    
    # 2. Resample Rebound Years (2 years with replacement)
    resampled_rebound = np.random.choice(rebound_years, size=2, replace=True)
    
    # 3. Recompute Derived Quantities
    M_boot = X_boot / 12
    C_boot = Z - (M_boot * 9) # Z is fixed
    T_boot = C_boot * 4
    
    # Calculate D_boot
    dec_2020_boot = X_boot - Z
    D_boot = dec_2020_boot.shift(-1).fillna(0)
    
    # Calculate B_boot (Sum of increases in resampled rebound years)
    inc_combined_boot = 0
    for year in resampled_rebound:
        rates_y = df[df['Year'] == year].drop(columns=['Year']).iloc[0]
        inc_combined_boot += (rates_y - X_boot)
    
    B_boot = inc_combined_boot.shift(-1).fillna(0)
    
    # Calculate E and Y
    E_boot = B_boot - D_boot
    Y_boot = T_boot + E_boot
    
    # 4. Calculate Total Overdiagnosis for this replicate
    total_X_boot = X_boot.sum()
    total_Y_boot = Y_boot.sum()
    
    if total_X_boot != 0:
        val = ((total_X_boot - total_Y_boot) / total_X_boot) * 100
        bootstrap_estimates.append(val)

# Calculate CI
lower_ci = np.percentile(bootstrap_estimates, 2.5)
upper_ci = np.percentile(bootstrap_estimates, 97.5)

print(f"Primary Estimate:      {total_O_pct:.2f}%")
print(f"95% Confidence Interval: ({lower_ci:.2f}%, {upper_ci:.2f}%)")
print("=" * 80)
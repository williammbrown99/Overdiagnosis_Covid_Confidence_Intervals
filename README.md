Breast Cancer Overdiagnosis Estimation (COVID-19 Natural Experiment)

This repository contains the data and Python code used to estimate breast cancer overdiagnosis rates by leveraging the COVID-19 pandemic as a natural experiment. The analysis uses the "Excess Incidence" approach, comparing tumor size distributions before, during, and after the pandemic-related screening pause.
Repository Contents
1. Data File

    SEER_DATA.csv

        Contains annual breast cancer incidence rates (per 100,000) stratified by tumor size (cm) from 2016 to 2022.

        Source: Surveillance, Epidemiology, and End Results (SEER) Program.

        Columns: Year, < 1cm, 1 - 1.9 cm, 2 - 2.9 cm, 3 - 3.9 cm, 4 - 4.9 cm, 5+ cm.

2. Analysis Scripts
A. Overdiagnosis_Covid_SEER.py (Main Analysis)

This script performs the primary size-specific overdiagnosis estimation using SEER data. It includes:

    Main Estimation: Calculates overdiagnosis for each tumor size category using the excess incidence formula (E=B−D).

    Sensitivity Analysis: Evaluates robustness against:

        Healthcare Avoidance (p): Adjusts for residual avoidance (0%, 5%, 12%).

        Lead Time (LT): Tests extended lead times (2, 4, and 7 years).

    Bootstrapping: Generates 95% Confidence Intervals (CIs) using 10,000 resampled iterations of baseline (2016–2019) and rebound (2021–2022) years.

B. Overdiagnosis_Covid_Caswell.py (Validation Analysis)

This script provides an alternative aggregate overdiagnosis estimate using published monthly incidence data from Caswell-Jin et al. (2022).

    Method: Calculates the "No-Screening" baseline (Y) by combining incidence rates during the quarantine period with the post-quarantine "excess."

    Uncertainty: Uses the Delta Method for error propagation to derive Standard Errors and 95% CIs from the published summary statistics.

Methodology

The core premise of this analysis is that the COVID-19 screening pause (2020) created a temporary "absence of screening" state.

    The "Missing" Cases (D): The drop in incidence in 2020 represents cancers not detected due to the pause.

    The "Excess" Cases (B): The surge in diagnoses in 2021–2022 represents these missing cases surfacing clinically or via delayed screening.

    Overdiagnosis (O): If the "Excess" is smaller than the "Missing" count (after adjusting for lead time), the difference represents cancers that were overdiagnosed (i.e., they would not have presented clinically without screening).

Formula:
O=(X - Y)/X​

Where X is the baseline incidence with screening, and Y is the estimated incidence in the absence of screening (Y=T+E).
Usage
Prerequisites

    Python 3.x

    pandas

    numpy

Bash

pip install pandas numpy

Running the Analysis

    Ensure SEER_DATA.csv is in the same directory as the scripts.

    Run the main SEER analysis:
    Bash

    python Overdiagnosis_Covid_SEER.py 

    Run the Caswell-Jin validation estimator:
    Bash

    python Overdiagnosis_Covid_Caswell.py

References

    Data Source: Surveillance, Epidemiology, and End Results (SEER) Program (www.seer.cancer.gov).

    Comparative Study: Caswell-Jin, J. L., et al. (2022). Change in Breast Cancer Stage at Diagnosis During the COVID-19 Pandemic in the US. JAMA Oncology.

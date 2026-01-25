import numpy as np

years_baseline = [2016, 2017, 2018, 2019]
years_rebound  = [2021, 2022]

rates = {
    2016: [68.0, 95.6, 52.4, 24.2, 14.0, 23.1],
    2017: [68.3, 94.9, 52.5, 26.9, 13.3, 24.4],
    2018: [68.0, 96.8, 54.7, 26.8, 13.2, 22.4],
    2019: [70.6, 99.6, 52.8, 26.9, 14.2, 24.2],
    2020: [61.3, 86.4, 49.3, 24.0, 12.8, 23.7],
    2021: [73.5,102.9, 56.5, 26.7, 15.2, 26.3],
    2022: [71.9, 97.7, 53.5, 27.1, 14.0, 25.6],
}

# next-larger mapping
next_larger = {0:1, 1:2, 2:3, 3:4, 4:5}

def round3(x):
    return np.round(x, 3)

def compute_total_overdiagnosis_with_rounding(baseline_years, rebound_years):
    X_list = []
    Y_list = []

    # Precompute baseline means for all bins
    X_baseline = []
    for s in range(6):
        Xs = np.mean([rates[y][s] for y in baseline_years])
        Xs = round3(Xs)                # <<< your key rounding step
        X_baseline.append(Xs)

    for s in range(6):
        X_s = X_baseline[s]
        Z_s = rates[2020][s]

        # C, T
        M_s = X_s / 12.0
        C_s = Z_s - 9.0 * M_s
        T_s = 4.0 * C_s

        # Excess term
        if s in next_larger:
            L = next_larger[s]
            X_L = X_baseline[L]
            Z_L = rates[2020][L]

            # increases
            incs = []
            for y in rebound_years:
                inc = rates[y][L] - X_L
                incs.append(round3(inc))

            B = round3(sum(incs))
            D = round3(abs(Z_L - X_L))
            E = round3(B - D)
        else:
            E = 0.0

        Y_s = T_s + E

        X_list.append(X_s)
        Y_list.append(Y_s)

    X_tot = np.sum(X_list)
    Y_tot = np.sum(Y_list)
    O = (X_tot - Y_tot) / X_tot

    return O, X_tot, Y_tot, X_list, Y_list

O_point, Xtot, Ytot, Xs, Ys = compute_total_overdiagnosis_with_rounding(
    years_baseline, years_rebound
)

print("X_tot:", Xtot)
print("Y_tot:", Ytot)
print("O:", O_point, "=", 100*O_point, "%")

def bootstrap_ci_with_rounding(B=100000, seed=1):
    rng = np.random.default_rng(seed)
    O_samples = np.empty(B)

    for b in range(B):
        baseline_sample = rng.choice(years_baseline, size=4, replace=True)
        rebound_sample  = rng.choice(years_rebound,  size=2, replace=True)

        O_b, _, _, _, _ = compute_total_overdiagnosis_with_rounding(
            baseline_sample, rebound_sample
        )

        O_samples[b] = O_b

    lo, hi = np.percentile(O_samples, [2.5, 97.5])
    return O_samples, lo, hi

O_samples, lo, hi = bootstrap_ci_with_rounding(B=100000, seed=2)

print("Point estimate:", 100*O_point)
print("95% CI:", 100*lo, "to", 100*hi)


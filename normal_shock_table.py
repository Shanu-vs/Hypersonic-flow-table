"""
===============================================================
  NORMAL SHOCK PROPERTY TABLE
  Hypersonic Flow Assignment
  Calorically perfect gas, constant gamma, steady 1-D normal shock
===============================================================

Station 1 = upstream (supersonic),  Station 2 = downstream (subsonic)

Relations used:
    M2^2      = [1 + (g-1)/2 * M1^2] / [g*M1^2 - (g-1)/2]
    p2/p1     = 1 + 2g/(g+1) * (M1^2 - 1)
    rho2/rho1 = (g+1)*M1^2 / [(g-1)*M1^2 + 2]
    T2/T1     = (p2/p1) * (rho1/rho2)
    p02/p01   = (rho2/rho1)^(g/(g-1)) * [(g+1)/(2g*M1^2 - (g-1))]^(1/(g-1))
    p02/p1    = (p02/p01) * (p01/p1)        <-- Rayleigh Pitot formula
    ds/R      = -ln(p02/p01)
    T02/T01   = 1                            (flow is adiabatic)
"""

import math

# ----------------------------------------------------------------
#  1. INPUT PARAMETERS  (edit these)
# ----------------------------------------------------------------
GAMMA = 1.4          # ratio of specific heats (1.4 for air, 1.667 monatomic)

# Mach ranges as (start, stop, step).
# Uniform sweep: M1 = 1.00 -> 20.00 in steps of 0.05  (381 rows)
MACH_RANGES = [
    (1.00, 20.00, 0.05),
]

SAVE_CSV = True                        # also write the table to a .csv file
CSV_NAME = "normal_shock_table.csv"


# ----------------------------------------------------------------
#  2. CORE CALCULATION
# ----------------------------------------------------------------
def normal_shock(M1, g=GAMMA):
    """Return all downstream-to-upstream property ratios across a normal
    shock for upstream Mach number M1 and specific heat ratio g."""

    if M1 < 1.0:
        raise ValueError(
            f"M1 = {M1} is subsonic. A normal shock requires M1 >= 1 "
            "(an expansion shock violates the second law of thermodynamics)."
        )

    M2 = math.sqrt((1.0 + 0.5 * (g - 1.0) * M1**2) /
                   (g * M1**2 - 0.5 * (g - 1.0)))

    p2_p1     = 1.0 + (2.0 * g / (g + 1.0)) * (M1**2 - 1.0)
    rho2_rho1 = (g + 1.0) * M1**2 / ((g - 1.0) * M1**2 + 2.0)
    T2_T1     = p2_p1 / rho2_rho1

    p02_p01 = (rho2_rho1) ** (g / (g - 1.0)) * \
              ((g + 1.0) / (2.0 * g * M1**2 - (g - 1.0))) ** (1.0 / (g - 1.0))

    p01_p1 = (1.0 + 0.5 * (g - 1.0) * M1**2) ** (g / (g - 1.0))
    p02_p1 = p02_p01 * p01_p1                 # Pitot pressure ratio

    ds_R = -math.log(p02_p01) + 0.0           # entropy rise, (s2-s1)/R (+0 kills -0.0)

    return {
        "M1": M1, "M2": M2,
        "p2/p1": p2_p1, "rho2/rho1": rho2_rho1, "T2/T1": T2_T1,
        "p02/p01": p02_p01, "p02/p1": p02_p1,
        "T02/T01": 1.0, "ds/R": ds_R,
    }


def limiting_values(g=GAMMA):
    """M1 -> infinity limits."""
    return {
        "M2":        math.sqrt((g - 1.0) / (2.0 * g)),
        "rho2/rho1": (g + 1.0) / (g - 1.0),
        "p2/p1":     float("inf"),
        "T2/T1":     float("inf"),
        "p02/p01":   0.0,
    }


# ----------------------------------------------------------------
#  3. BUILD THE MACH LIST
# ----------------------------------------------------------------
def build_mach_list(ranges):
    machs = []
    for start, stop, step in ranges:
        n = int(round((stop - start) / step))
        for i in range(n + 1):
            M = round(start + i * step, 6)
            if M <= stop + 1e-9 and M not in machs:
                machs.append(M)
    return sorted(machs)


# ----------------------------------------------------------------
#  4. OUTPUT
# ----------------------------------------------------------------
HEADER = ("{:>7} {:>9} {:>12} {:>12} {:>11} {:>11} {:>12} {:>9} {:>10}")
ROW    = ("{:>7.2f} {:>9.4f} {:>12.4f} {:>12.4f} {:>11.4f} "
          "{:>11.5f} {:>12.4f} {:>9.1f} {:>10.4f}")

COLS = ["M1", "M2", "p2/p1", "rho2/rho1", "T2/T1",
        "p02/p01", "p02/p1", "T02/T01", "ds/R"]


def print_table(machs, g=GAMMA):
    width = 100
    print("=" * width)
    print("NORMAL SHOCK PROPERTIES  |  calorically perfect gas  |  "
          f"gamma = {g}".center(width))
    print("=" * width)
    print(HEADER.format(*COLS))
    print("-" * width)

    for M1 in machs:
        r = normal_shock(M1, g)
        print(ROW.format(*[r[c] for c in COLS]))

    lim = limiting_values(g)
    print("-" * width)
    print("{:>7} {:>9.4f} {:>12} {:>12.4f} {:>11} {:>11.5f} {:>12} "
          "{:>9.1f} {:>10}".format(
              "inf", lim["M2"], "inf", lim["rho2/rho1"], "inf",
              lim["p02/p01"], "inf", 1.0, "inf"))
    print("=" * width)
    print(f"Hypersonic limits (M1 -> inf):  M2 -> {lim['M2']:.4f},   "
          f"rho2/rho1 -> {lim['rho2/rho1']:.4f}")
    print("Note: the density ratio saturates, while p2/p1 and T2/T1 "
          "grow without bound.")


def save_csv(machs, filename=CSV_NAME, g=GAMMA):
    import csv
    with open(filename, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow([f"gamma = {g}"])
        w.writerow(COLS)
        for M1 in machs:
            r = normal_shock(M1, g)
            w.writerow([f"{r[c]:.6f}" for c in COLS])
    print(f"\nTable also written to '{filename}'")


# ----------------------------------------------------------------
#  5. SINGLE-POINT QUERY
# ----------------------------------------------------------------
def single_point():
    """Interactive mode: properties for one user-supplied Mach number."""
    try:
        M1 = float(input("\nEnter an upstream Mach number (or Enter to skip): "))
    except (ValueError, EOFError):
        return
    try:
        r = normal_shock(M1, GAMMA)
    except ValueError as e:
        print(e)
        return
    print(f"\nNormal shock properties at M1 = {M1}, gamma = {GAMMA}")
    print("-" * 40)
    for k in COLS[1:]:
        print(f"  {k:<12s} = {r[k]:.6f}")


# ----------------------------------------------------------------
if __name__ == "__main__":
    mach_list = build_mach_list(MACH_RANGES)
    print_table(mach_list, GAMMA)
    if SAVE_CSV:
        save_csv(mach_list)
    single_point()

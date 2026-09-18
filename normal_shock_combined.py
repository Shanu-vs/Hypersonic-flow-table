import sys

GAMMA = 1.4  # specific heat ratio for air


def compute_ratios(M0, gamma=GAMMA):
    """Return a dict of normal shock ratios for a given upstream Mach number."""
    if M0 <= 1.0:
        raise ValueError("Mach number must be greater than 1 for a normal shock to exist.")

    g = gamma
    M0_sq = M0 ** 2

    M1_sq = ((g - 1) * M0_sq + 2) / (2 * g * M0_sq - (g - 1))
    M1 = M1_sq ** 0.5

    p_ratio = (2 * g * M0_sq - (g - 1)) / (g + 1)

    T_ratio = ((2 * g * M0_sq - (g - 1)) * ((g - 1) * M0_sq + 2)) / (((g + 1) ** 2) * M0_sq)

    rho_ratio = ((g + 1) * M0_sq) / ((g - 1) * M0_sq + 2)

    term1 = (((g + 1) * M0_sq) / ((g - 1) * M0_sq + 2)) ** (g / (g - 1))
    term2 = ((g + 1) / (2 * g * M0_sq - (g - 1))) ** (1 / (g - 1))
    pt_ratio = term1 * term2

    Tt_ratio = 1.0  # always 1 for an adiabatic normal shock

    return {
        "M0": M0,
        "M1": M1,
        "p1/p0": p_ratio,
        "pt1/pt0": pt_ratio,
        "T1/T0": T_ratio,
        "Tt1/Tt0": Tt_ratio,
        "rho1/rho0": rho_ratio,
    }


def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Invalid number, please try again.")


def run_single_mach_mode():
    """Mode 1: single Mach number, with optional actual downstream values."""
    while True:
        try:
            M0 = get_float("\nEnter upstream Mach number M0 (> 1): ")
            ratios = compute_ratios(M0)
        except ValueError as e:
            print(f"Error: {e}")
            continue

        print(f"\n--- Results for M0 = {M0} ---")
        print(f"Downstream Mach number, M1     : {ratios['M1']:.6f}")
        print(f"Static pressure ratio, p1/p0    : {ratios['p1/p0']:.6f}")
        print(f"Total pressure ratio, pt1/pt0   : {ratios['pt1/pt0']:.6f}")
        print(f"Static temperature ratio, T1/T0 : {ratios['T1/T0']:.6f}")
        print(f"Total temperature ratio, Tt1/Tt0: {ratios['Tt1/Tt0']:.6f}")
        print(f"Density ratio, rho1/rho0        : {ratios['rho1/rho0']:.6f}")

        check = input("\nDo you want to enter upstream p, T, rho to compute downstream values? (y/n): ").strip().lower()
        if check == 'y':
            p0 = get_float("Enter upstream static pressure p0: ")
            T0 = get_float("Enter upstream static temperature T0: ")
            rho0 = get_float("Enter upstream density rho0: ")

            p1 = p0 * ratios['p1/p0']
            T1 = T0 * ratios['T1/T0']
            rho1 = rho0 * ratios['rho1/rho0']

            print("\n--- Downstream (Zone 1) Values ---")
            print(f"p1   = {p1:.6f}")
            print(f"T1   = {T1:.6f}")
            print(f"rho1 = {rho1:.6f}")

        again = input("\nDo you want to calculate for another Mach number? (y = continue, n = exit): ").strip().lower()
        if again != 'y':
            break


def run_table_mode():
    """Mode 2: table of ratios from starting Mach to ending Mach with a step."""
    while True:
        M_start = get_float("\nEnter starting Mach number (> 1): ")
        M_end = get_float("Enter ending Mach number: ")
        M_step = get_float("Enter step size: ")

        if M_start <= 1.0:
            print("Error: starting Mach number must be greater than 1. Try again.")
            continue
        elif M_step <= 0:
            print("Error: step size must be positive. Try again.")
            continue
        elif M_end < M_start:
            print("Error: ending Mach number must be >= starting Mach number. Try again.")
            continue
        else:
            break

    header = f"{'M0':>8} | {'M1':>10} | {'p1/p0':>12} | {'pt1/pt0':>12} | {'T1/T0':>12} | {'rho1/rho0':>12}"
    print("\n" + header)
    print("-" * len(header))

    M = M_start
    epsilon = M_step / 1000.0  # to include the end value despite floating point drift
    while M <= M_end + epsilon:
        ratios = compute_ratios(M)
        print(f"{ratios['M0']:8.4f} | {ratios['M1']:10.6f} | {ratios['p1/p0']:12.6f} | "
              f"{ratios['pt1/pt0']:12.6f} | {ratios['T1/T0']:12.6f} | {ratios['rho1/rho0']:12.6f}")
        M += M_step

    print("\nDone.")


def main():
    print("=" * 70)
    print(" Normal Shock Wave Calculator (gamma = {:.2f})".format(GAMMA))
    print("=" * 70)

    while True:
        print("\nChoose a mode:")
        print("  1. Single Mach number (with optional actual p, T, rho lookup)")
        print("  2. Table of ratios over a Mach number range")
        print("  3. Exit")
        choice = input("Enter choice (1/2/3): ").strip()

        if choice == '1':
            run_single_mach_mode()
        elif choice == '2':
            run_table_mode()
        elif choice == '3':
            print("\nExiting program. Goodbye!")
            sys.exit(0)
        else:
            print("Invalid choice, please enter 1, 2, or 3.")


if __name__ == "__main__":
    main()
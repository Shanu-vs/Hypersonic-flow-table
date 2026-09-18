

import math

print("=====================================")
print(" NORMAL SHOCK CALCULATOR (Simple)")
print("=====================================")

# ---------------------------------------------------
# STEP 1: choose gamma (type of gas)
# ---------------------------------------------------
gas = input("Enter gas type (air / monatomic): ").strip().lower()

if gas == "air":
    gamma = 1.4
elif gas == "monatomic":
    gamma = 1.667
else:
    print("Unknown gas type entered -> using air (gamma = 1.4) by default.")
    gamma = 1.4

print("Using gamma =", gamma)
print()

# ---------------------------------------------------
# STEP 2: choose what to do
# ---------------------------------------------------
print("1. Single Mach number")
print("2. Table of Mach numbers")
choice = input("Enter choice (1 or 2): ").strip()

# ===================== OPTION 1 =====================
if choice == "1":
    M1 = float(input("Enter upstream Mach number M1: "))

    if M1 < 1:
        print("Error: M1 must be >= 1 for a normal shock to exist")
        print("(an expansion shock would violate the second law).")
    else:
        M2 = math.sqrt((1 + (gamma - 1) / 2 * M1 ** 2) /
                       (gamma * M1 ** 2 - (gamma - 1) / 2))
        p2_p1 = 1 + (2 * gamma / (gamma + 1)) * (M1 ** 2 - 1)
        rho2_rho1 = ((gamma + 1) * M1 ** 2) / ((gamma - 1) * M1 ** 2 + 2)
        T2_T1 = p2_p1 / rho2_rho1
        p02_p01 = (rho2_rho1 ** (gamma / (gamma - 1))) * \
                  (((gamma + 1) / (2 * gamma * M1 ** 2 - (gamma - 1))) **
                   (1 / (gamma - 1)))

        print()
        print("Results for M1 =", M1, " gamma =", gamma)
        print("M2        =", round(M2, 4))
        print("p2/p1     =", round(p2_p1, 4))
        print("rho2/rho1 =", round(rho2_rho1, 4))
        print("T2/T1     =", round(T2_T1, 4))
        print("p02/p01   =", round(p02_p01, 5))

        # a simple if/else check just to show the branching
        if M1 >= 5:
            print("Note: M1 >= 5, this is in the hypersonic range.")
        elif M1 >= 1:
            print("Note: 1 <= M1 < 5, this is supersonic (not hypersonic).")

# ===================== OPTION 2 =====================
elif choice == "2":
    start = float(input("Start M1: "))
    stop = float(input("Stop M1: "))
    step = float(input("Step: "))

    if start < 1:
        print("Error: start must be >= 1.")
    elif step <= 0:
        print("Error: step must be positive.")
    elif stop < start:
        print("Error: stop must not be less than start.")
    else:
        print()
        print("M1      M2       p2/p1     rho2/rho1   T2/T1")
        M1 = start
        while M1 <= stop + 1e-9:
            M2 = math.sqrt((1 + (gamma - 1) / 2 * M1 ** 2) /
                           (gamma * M1 ** 2 - (gamma - 1) / 2))
            p2_p1 = 1 + (2 * gamma / (gamma + 1)) * (M1 ** 2 - 1)
            rho2_rho1 = ((gamma + 1) * M1 ** 2) / ((gamma - 1) * M1 ** 2 + 2)
            T2_T1 = p2_p1 / rho2_rho1

            print("%.2f   %.4f   %.4f   %.4f   %.4f"
                  % (M1, M2, p2_p1, rho2_rho1, T2_T1))

            M1 = M1 + step

# ===================== INVALID CHOICE =====================
else:
    print("Invalid choice. Please enter 1 or 2.")

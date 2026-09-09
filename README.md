# Normal Shock Calculator — Hypersonic Flow

Normal shock property calculator and table generator for a calorically perfect
gas (constant gamma, steady one-dimensional normal shock).

## How to run it

| I want to… | Do this |
|---|---|
| Just open the app | Double-click **`dist\NormalShockCalculator.exe`** (or the *Normal Shock Calculator* shortcut on the Desktop). No Python needed — it is self-contained. |
| Run from the source | Double-click **`Run Normal Shock Calculator.bat`** (needs Python 3 installed). |
| Print the plain-text table | `python normal_shock_table.py` |
| Rebuild the .exe after editing the code | Double-click **`build_app.bat`** |

## What the application does

**Single Mach number** — enter M1 and get M2, p2/p1, rho2/rho1, T2/T1,
p02/p01, the Pitot ratio p02/p1, T02/T01 and the entropy rise ds/R. Optionally
enter upstream p1 and T1 to also get dimensional p2, T2, rho1, rho2 and the
upstream speed of sound (R = 287 J/kg.K).

**Generate table** — sweep any Mach range and step (default 1 → 20 in steps of
0.05, i.e. 381 rows), with the M1 → infinity limit row at the bottom, and
export to CSV.

**Graphs** — plot every parameter against M1, either as eight small multiples
(one auto-scaled panel per property) or as a single overlay of the curves you
tick, with an optional log y-axis. The plot can be saved as vector PostScript.

Gamma is set in the header (1.4 for air, 1.667 for a monatomic gas).

## Relations used

    M2^2      = [1 + (g-1)/2 * M1^2] / [g*M1^2 - (g-1)/2]
    p2/p1     = 1 + 2g/(g+1) * (M1^2 - 1)
    rho2/rho1 = (g+1)*M1^2 / [(g-1)*M1^2 + 2]
    T2/T1     = (p2/p1) * (rho1/rho2)
    p02/p01   = (rho2/rho1)^(g/(g-1)) * [(g+1)/(2g*M1^2 - (g-1))]^(1/(g-1))
    p02/p1    = (p02/p01) * (p01/p1)          (Rayleigh Pitot formula)
    ds/R      = -ln(p02/p01)
    T02/T01   = 1                             (the flow is adiabatic)

M1 < 1 is rejected: an expansion shock would decrease entropy and so violates
the second law.

Hypersonic limits (gamma = 1.4): M2 → 0.3780 and rho2/rho1 → 6, while p2/p1
and T2/T1 grow without bound.

## Check against NACA Report 1135 (gamma = 1.4)

| M1 | M2 | p2/p1 | rho2/rho1 | T2/T1 | p02/p01 |
|---|---|---|---|---|---|
| 2.00 | 0.5774 | 4.5000 | 2.6667 | 1.6875 | 0.72087 |
| 5.00 | 0.4152 | 29.000 | 5.0000 | 5.8000 | 0.06172 |
| 10.00 | 0.3876 | 116.50 | 5.7143 | 20.3875 | 0.00304 |
| 20.00 | 0.3804 | 466.50 | 5.9259 | 78.7219 | 0.00011 |

## Files

    normal_shock_gui.py    the application (tkinter; standard library only)
    normal_shock_table.py  console version, prints the table and writes the CSV
    make_icon.py           draws shock.ico
    build_app.bat          rebuilds dist\NormalShockCalculator.exe (PyInstaller)
    Run ... .bat           double-click launcher for the Python source

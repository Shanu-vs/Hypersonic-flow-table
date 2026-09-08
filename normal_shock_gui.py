"""
===============================================================
  NORMAL SHOCK CALCULATOR  --  GRAPHICAL USER INTERFACE
  Hypersonic Flow Assignment
  Calorically perfect gas, constant gamma, steady 1-D normal shock
===============================================================

Station 1 = upstream (supersonic),  Station 2 = downstream (subsonic)

    M2^2      = [1 + (g-1)/2 * M1^2] / [g*M1^2 - (g-1)/2]
    p2/p1     = 1 + 2g/(g+1) * (M1^2 - 1)
    rho2/rho1 = (g+1)*M1^2 / [(g-1)*M1^2 + 2]
    T2/T1     = (p2/p1) / (rho2/rho1)
    p02/p01   = (rho2/rho1)^(g/(g-1)) * [(g+1)/(2g*M1^2 - (g-1))]^(1/(g-1))
    p02/p1    = (p02/p01) * (p01/p1)        <-- Rayleigh Pitot formula
    ds/R      = -ln(p02/p01)
    T02/T01   = 1                            (flow is adiabatic)

Standard library only (tkinter).   Run with:   python normal_shock_gui.py
"""

import csv
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox


# ================================================================
#  1. PHYSICS
# ================================================================
COLS = ["M1", "M2", "p2/p1", "rho2/rho1", "T2/T1",
        "p02/p01", "p02/p1", "T02/T01", "ds/R"]

LABELS = {
    "M2":        "M2        (downstream Mach)",
    "p2/p1":     "p2/p1     (static pressure ratio)",
    "rho2/rho1": "rho2/rho1 (density ratio)",
    "T2/T1":     "T2/T1     (static temperature ratio)",
    "p02/p01":   "p02/p01   (total pressure ratio)",
    "p02/p1":    "p02/p1    (Pitot / Rayleigh ratio)",
    "T02/T01":   "T02/T01   (total temperature ratio)",
    "ds/R":      "ds/R      (entropy rise)",
}

R_AIR = 287.0        # J/kg.K, used only for the optional dimensional block


def normal_shock(M1, g=1.4):
    """All downstream-to-upstream property ratios across a normal shock."""
    if g <= 1.0:
        raise ValueError("gamma must be greater than 1.")
    if M1 < 1.0:
        raise ValueError(
            "M1 = %g is subsonic. A normal shock requires M1 >= 1\n"
            "(an expansion shock would violate the second law)." % M1)

    M2 = math.sqrt((1.0 + 0.5 * (g - 1.0) * M1 ** 2) /
                   (g * M1 ** 2 - 0.5 * (g - 1.0)))

    p2_p1 = 1.0 + (2.0 * g / (g + 1.0)) * (M1 ** 2 - 1.0)
    rho2_rho1 = (g + 1.0) * M1 ** 2 / ((g - 1.0) * M1 ** 2 + 2.0)
    T2_T1 = p2_p1 / rho2_rho1

    p02_p01 = (rho2_rho1) ** (g / (g - 1.0)) * \
              ((g + 1.0) / (2.0 * g * M1 ** 2 - (g - 1.0))) ** (1.0 / (g - 1.0))

    p01_p1 = (1.0 + 0.5 * (g - 1.0) * M1 ** 2) ** (g / (g - 1.0))
    p02_p1 = p02_p01 * p01_p1                  # Pitot pressure ratio

    ds_R = -math.log(p02_p01) + 0.0            # +0 kills the -0.0 display

    return {"M1": M1, "M2": M2,
            "p2/p1": p2_p1, "rho2/rho1": rho2_rho1, "T2/T1": T2_T1,
            "p02/p01": p02_p01, "p02/p1": p02_p1,
            "T02/T01": 1.0, "ds/R": ds_R}


def dimensional_state(r, p1, T1, g=1.4, R=R_AIR):
    """Turn the ratios into actual upstream / downstream conditions."""
    p2 = p1 * r["p2/p1"]
    T2 = T1 * r["T2/T1"]
    rho1 = p1 / (R * T1)
    rho2 = rho1 * r["rho2/rho1"]
    a1 = math.sqrt(g * R * T1)
    u1 = r["M1"] * a1
    u2 = u1 / r["rho2/rho1"]                   # mass conservation
    return p2, T2, rho1, rho2, a1, u1, u2


def limiting_values(g=1.4):
    """M1 -> infinity limits."""
    return {"M2": math.sqrt((g - 1.0) / (2.0 * g)),
            "rho2/rho1": (g + 1.0) / (g - 1.0)}


def build_mach_list(start, stop, step):
    if step <= 0:
        raise ValueError("Step must be positive.")
    if stop < start:
        raise ValueError("Stop must not be smaller than start.")
    n = int(round((stop - start) / step))
    return [round(start + i * step, 6) for i in range(n + 1)]


# ================================================================
#  2. TINY PLOTTING ENGINE  (drawn straight onto a tk.Canvas,
#     so no matplotlib / numpy is required)
# ================================================================
PALETTE = ["#1f6feb", "#d1242f", "#1a7f37", "#9a6700",
           "#8250df", "#0b7285", "#bf3989", "#57606a"]


def nice_ticks(lo, hi, target=5):
    """A short list of round tick values covering [lo, hi]."""
    if hi <= lo:
        hi = lo + 1.0
    raw = (hi - lo) / float(max(target, 1))
    mag = 10.0 ** math.floor(math.log10(raw))
    step = 10.0 * mag
    for m in (1.0, 2.0, 2.5, 5.0, 10.0):
        if raw <= m * mag:
            step = m * mag
            break
    ticks, v = [], math.floor(lo / step) * step
    while v < hi + 0.5 * step:
        if v >= lo - 1e-9 * max(1.0, abs(v)):
            ticks.append(round(v, 12))
        v += step
    return ticks


def fmt_tick(v):
    """Compact axis-label text."""
    if abs(v) < 1e-12:
        return "0"
    if abs(v) >= 1e5 or abs(v) < 1e-3:
        return "%.0e" % v
    txt = ("%.4f" % v).rstrip("0").rstrip(".")
    return txt if txt else "0"


class PlotCanvas(ttk.Frame):
    """Draws one or more x-y panels on a plain tk.Canvas.

    A panel is a dict:
        {"title": str, "logy": bool, "series": [(label, xs, ys), ...]}
    """

    def __init__(self, master, **kw):
        super().__init__(master, **kw)
        self.canvas = tk.Canvas(self, bg="white", highlightthickness=1,
                                highlightbackground="#c9d1d9")
        self.canvas.pack(fill="both", expand=True)
        self.panels = []
        self.canvas.bind("<Configure>", lambda _ev: self.redraw())

    def show(self, panels):
        self.panels = panels
        self.redraw()

    # ---------- layout ----------
    def redraw(self):
        c = self.canvas
        c.delete("all")
        W, H = c.winfo_width(), c.winfo_height()
        if W < 60 or H < 60:
            return
        if not self.panels:
            c.create_text(W / 2, H / 2, text="Press  Plot  to draw the curves.",
                          fill="#57606a", font=("Segoe UI", 11))
            return

        n = len(self.panels)
        cols = 1 if n == 1 else (2 if n <= 4 else 4)
        rows = int(math.ceil(n / float(cols)))
        pw, ph = W / float(cols), H / float(rows)
        for i, panel in enumerate(self.panels):
            r, k = divmod(i, cols)
            self._draw_panel(k * pw, r * ph, (k + 1) * pw, (r + 1) * ph, panel)

    # ---------- one panel ----------
    def _draw_panel(self, px0, py0, px1, py1, panel):
        c = self.canvas
        compact = (px1 - px0) < 360
        fs = 7 if compact else 9
        ml = 46 if compact else 62
        mr, mt, mb = 12, 22, 34

        X0, X1 = px0 + ml, px1 - mr
        Y0, Y1 = py0 + mt, py1 - mb
        if X1 - X0 < 30 or Y1 - Y0 < 30:
            return

        logy = panel.get("logy", False)

        # collect drawable data
        curves = []
        for label, xs, ys in panel["series"]:
            pts = [(x, y) for x, y in zip(xs, ys) if not (logy and y <= 0.0)]
            if len(pts) >= 2:
                curves.append((label, pts))
        if not curves:
            c.create_text((px0 + px1) / 2, (py0 + py1) / 2, font=("Segoe UI", fs),
                          fill="#57606a", text="no positive data for a log axis")
            return

        xlo = min(q[0] for _l, pts in curves for q in pts)
        xhi = max(q[0] for _l, pts in curves for q in pts)
        raw = [(math.log10(q[1]) if logy else q[1])
               for _l, pts in curves for q in pts]
        ylo, yhi = min(raw), max(raw)
        if yhi - ylo < 1e-12:                    # flat curve (e.g. T02/T01)
            ylo, yhi = ylo - 0.5, yhi + 0.5
        if xhi - xlo < 1e-12:
            xhi = xlo + 1.0

        def sx(x):
            return X0 + (x - xlo) / (xhi - xlo) * (X1 - X0)

        def sy(v):
            return Y1 - (v - ylo) / (yhi - ylo) * (Y1 - Y0)

        # ---- grid + ticks ----
        for xt in nice_ticks(xlo, xhi, 4 if compact else 6):
            X = sx(xt)
            c.create_line(X, Y0, X, Y1, fill="#ececec")
            c.create_line(X, Y1, X, Y1 + 4, fill="#57606a")
            c.create_text(X, Y1 + 6, text=fmt_tick(xt), anchor="n",
                          font=("Segoe UI", fs), fill="#57606a")

        if logy:
            yticks = [float(k) for k in
                      range(int(math.floor(ylo)), int(math.ceil(yhi)) + 1)]
            if len(yticks) < 2:
                yticks = [ylo, yhi]
        else:
            yticks = nice_ticks(ylo, yhi, 4 if compact else 6)
        for yt in yticks:
            Y = sy(yt)
            if not (Y0 - 1 <= Y <= Y1 + 1):
                continue
            c.create_line(X0, Y, X1, Y, fill="#ececec")
            c.create_line(X0 - 4, Y, X0, Y, fill="#57606a")
            c.create_text(X0 - 6, Y, text=fmt_tick(10.0 ** yt if logy else yt),
                          anchor="e", font=("Segoe UI", fs), fill="#57606a")

        # ---- frame, titles ----
        c.create_rectangle(X0, Y0, X1, Y1, outline="#8b949e")
        c.create_text((X0 + X1) / 2, py0 + mt / 2,
                      font=("Segoe UI", fs + 1, "bold"),
                      text=panel["title"] + ("   [log scale]" if logy else ""))
        c.create_text((X0 + X1) / 2, Y1 + fs + 14, text="M1", anchor="n",
                      font=("Segoe UI", fs), fill="#57606a")

        # ---- curves ----
        for i, (label, pts) in enumerate(curves):
            colour = PALETTE[i % len(PALETTE)]
            flat = []
            for x, y in pts:
                flat += [sx(x), sy(math.log10(y) if logy else y)]
            c.create_line(*flat, fill=colour, width=2, smooth=False)

        # ---- legend (only when several curves share the panel) ----
        if len(curves) > 1:
            ly = Y0 + 10
            for i, (label, _pts) in enumerate(curves):
                colour = PALETTE[i % len(PALETTE)]
                c.create_line(X1 - 116, ly, X1 - 96, ly, fill=colour, width=3)
                c.create_text(X1 - 92, ly, text=label, anchor="w",
                              font=("Segoe UI", fs), fill="#24292f")
                ly += fs + 8


# ================================================================
#  3. GRAPHICAL USER INTERFACE
# ================================================================
class ShockApp(tk.Tk):

    def __init__(self):
        super().__init__()
        self.title("Normal Shock Calculator  -  Hypersonic Flow")
        self.geometry("1120x720")
        self.minsize(900, 600)

        self.gamma_var = tk.StringVar(value="1.4")
        self.rows = []                       # last generated table

        self._build_header()

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=(0, 6))
        self.tab_single = ttk.Frame(nb, padding=12)
        self.tab_table = ttk.Frame(nb, padding=12)
        self.tab_graph = ttk.Frame(nb, padding=12)
        nb.add(self.tab_single, text="  Single Mach number  ")
        nb.add(self.tab_table, text="  Generate table  ")
        nb.add(self.tab_graph, text="  Graphs  ")

        self._build_single_tab()
        self._build_table_tab()
        self._build_graph_tab()

        self.status = tk.StringVar(value="Ready.")
        ttk.Label(self, textvariable=self.status, relief="sunken",
                  anchor="w", padding=4).pack(fill="x", side="bottom")

    # ---------------- header: gamma ----------------
    def _build_header(self):
        f = ttk.Frame(self, padding=(12, 10, 12, 6))
        f.pack(fill="x")
        ttk.Label(f, text="NORMAL SHOCK PROPERTIES",
                  font=("Segoe UI", 14, "bold")).pack(side="left")
        ttk.Label(f, text="   calorically perfect gas").pack(side="left")

        ttk.Label(f, text="gamma =").pack(side="left", padx=(30, 4))
        ttk.Entry(f, textvariable=self.gamma_var, width=8).pack(side="left")
        ttk.Button(f, text="Air (1.4)",
                   command=lambda: self.gamma_var.set("1.4")).pack(side="left", padx=4)
        ttk.Button(f, text="Monatomic (1.667)",
                   command=lambda: self.gamma_var.set("1.667")).pack(side="left")

    def _gamma(self):
        try:
            g = float(self.gamma_var.get())
        except ValueError:
            raise ValueError("gamma must be a number.")
        if g <= 1.0:
            raise ValueError("gamma must be greater than 1.")
        return g

    # ---------------- tab 1: single point ----------------
    def _build_single_tab(self):
        f = self.tab_single

        inp = ttk.LabelFrame(f, text=" Input ", padding=10)
        inp.pack(fill="x")

        ttk.Label(inp, text="Upstream Mach number  M1 =").grid(
            row=0, column=0, sticky="w")
        self.m1_var = tk.StringVar(value="2.0")
        e = ttk.Entry(inp, textvariable=self.m1_var, width=12)
        e.grid(row=0, column=1, padx=6)
        e.bind("<Return>", lambda _ev: self.compute_single())
        e.focus_set()

        ttk.Button(inp, text="Compute", command=self.compute_single).grid(
            row=0, column=2, padx=8)

        ttk.Label(inp, text="Optional upstream conditions "
                            "(leave blank to skip):").grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(12, 2))
        ttk.Label(inp, text="p1 [Pa] =").grid(row=2, column=0, sticky="e")
        self.p1_var = tk.StringVar(value="101325")
        ttk.Entry(inp, textvariable=self.p1_var, width=12).grid(
            row=2, column=1, padx=6)
        ttk.Label(inp, text="T1 [K] =").grid(row=2, column=2, sticky="e",
                                             padx=(12, 0))
        self.T1_var = tk.StringVar(value="288.15")
        ttk.Entry(inp, textvariable=self.T1_var, width=12).grid(
            row=2, column=3, padx=6)
        ttk.Label(inp, text="(R = 287 J/kg.K)").grid(row=2, column=4, sticky="w")

        out = ttk.LabelFrame(f, text=" Results ", padding=10)
        out.pack(fill="both", expand=True, pady=(12, 0))
        self.single_text = tk.Text(out, height=18, font=("Consolas", 11),
                                   wrap="none", state="disabled")
        self.single_text.pack(fill="both", expand=True)

    def compute_single(self):
        try:
            g = self._gamma()
            M1 = float(self.m1_var.get())
            r = normal_shock(M1, g)
        except ValueError as err:
            messagebox.showerror("Invalid input", str(err))
            self.status.set("Error: " + str(err).splitlines()[0])
            return

        lines = ["Normal shock at  M1 = %.4f   with  gamma = %g" % (M1, g),
                 "-" * 58]
        for c in COLS[1:]:
            lines.append("  %-36s = %12.6f" % (LABELS[c], r[c]))

        # dimensional block, only if both boxes hold valid positive numbers
        try:
            p1 = float(self.p1_var.get())
            T1 = float(self.T1_var.get())
            if p1 > 0 and T1 > 0:
                p2, T2, rho1, rho2, a1, u1, u2 = dimensional_state(r, p1, T1, g)
                lines += ["", "Dimensional conditions (R = 287 J/kg.K):",
                          "-" * 58,
                          "  %-36s = %12.3f" % ("p1   [Pa]", p1),
                          "  %-36s = %12.3f" % ("p2   [Pa]", p2),
                          "  %-36s = %12.3f" % ("T1   [K]", T1),
                          "  %-36s = %12.3f" % ("T2   [K]", T2),
                          "  %-36s = %12.5f" % ("rho1 [kg/m^3]", rho1),
                          "  %-36s = %12.5f" % ("rho2 [kg/m^3]", rho2),
                          "  %-36s = %12.3f" % ("a1   [m/s]", a1),
                          "  %-36s = %12.3f" % ("u1   [m/s]", u1),
                          "  %-36s = %12.3f" % ("u2   [m/s]", u2)]
        except ValueError:
            pass

        lim = limiting_values(g)
        lines += ["", "Hypersonic limits (M1 -> inf):  M2 -> %.4f,   "
                      "rho2/rho1 -> %.4f" % (lim["M2"], lim["rho2/rho1"])]

        self.single_text.configure(state="normal")
        self.single_text.delete("1.0", "end")
        self.single_text.insert("1.0", "\n".join(lines))
        self.single_text.configure(state="disabled")
        self.status.set("Computed properties at M1 = %g." % M1)

    # ---------------- tab 2: table ----------------
    def _build_table_tab(self):
        f = self.tab_table

        inp = ttk.LabelFrame(f, text=" Mach sweep ", padding=10)
        inp.pack(fill="x")

        self.start_var = tk.StringVar(value="1.0")
        self.stop_var = tk.StringVar(value="20.0")
        self.step_var = tk.StringVar(value="0.05")

        for i, (txt, var) in enumerate([("Start M1", self.start_var),
                                        ("Stop M1", self.stop_var),
                                        ("Step", self.step_var)]):
            ttk.Label(inp, text=txt + " =").grid(
                row=0, column=2 * i, sticky="e", padx=(12 if i else 0, 4))
            en = ttk.Entry(inp, textvariable=var, width=10)
            en.grid(row=0, column=2 * i + 1)
            en.bind("<Return>", lambda _ev: self.generate_table())

        ttk.Button(inp, text="Generate", command=self.generate_table).grid(
            row=0, column=6, padx=12)
        ttk.Button(inp, text="Export CSV", command=self.export_csv).grid(
            row=0, column=7)

        tv_frame = ttk.Frame(f)
        tv_frame.pack(fill="both", expand=True, pady=(12, 0))

        self.tree = ttk.Treeview(tv_frame, columns=COLS, show="headings",
                                 height=20)
        for c in COLS:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=105, anchor="e", stretch=True)
        vsb = ttk.Scrollbar(tv_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True)
        vsb.pack(side="right", fill="y")

    def generate_table(self):
        try:
            g = self._gamma()
            start = float(self.start_var.get())
            stop = float(self.stop_var.get())
            step = float(self.step_var.get())
            machs = build_mach_list(start, stop, step)
            if len(machs) > 20000:
                raise ValueError("That sweep needs %d rows. Use a larger step."
                                 % len(machs))
            self.rows = [normal_shock(M, g) for M in machs]
        except ValueError as err:
            messagebox.showerror("Invalid input", str(err))
            self.status.set("Error: " + str(err).splitlines()[0])
            return

        self.tree.delete(*self.tree.get_children())
        for r in self.rows:
            self.tree.insert("", "end", values=(
                "%.2f" % r["M1"], "%.4f" % r["M2"], "%.4f" % r["p2/p1"],
                "%.4f" % r["rho2/rho1"], "%.4f" % r["T2/T1"],
                "%.5f" % r["p02/p01"], "%.4f" % r["p02/p1"],
                "%.1f" % r["T02/T01"], "%.4f" % r["ds/R"]))

        lim = limiting_values(g)
        self.status.set("%d rows for M1 = %g to %g, step %g, gamma = %g   |   "
                        "M1 -> inf:  M2 -> %.4f, rho2/rho1 -> %.4f"
                        % (len(self.rows), start, stop, step, g,
                           lim["M2"], lim["rho2/rho1"]))

    def export_csv(self):
        if not self.rows:
            messagebox.showinfo("Nothing to export", "Generate a table first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile="normal_shock_table.csv",
            filetypes=[("CSV file", "*.csv"), ("All files", "*.*")])
        if not path:
            return
        with open(path, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["gamma = %g" % self._gamma()])
            w.writerow(COLS)
            for r in self.rows:
                w.writerow(["%.6f" % r[c] for c in COLS])
        self.status.set("Saved %d rows to %s" % (len(self.rows), path))

    # ---------------- tab 3: graphs ----------------
    def _build_graph_tab(self):
        f = self.tab_graph

        inp = ttk.LabelFrame(f, text=" Plot settings ", padding=10)
        inp.pack(fill="x")

        self.g_start_var = tk.StringVar(value="1.0")
        self.g_stop_var = tk.StringVar(value="20.0")
        self.g_step_var = tk.StringVar(value="0.05")
        for i, (txt, var) in enumerate([("Start M1", self.g_start_var),
                                        ("Stop M1", self.g_stop_var),
                                        ("Step", self.g_step_var)]):
            ttk.Label(inp, text=txt + " =").grid(
                row=0, column=2 * i, sticky="e", padx=(12 if i else 0, 4))
            en = ttk.Entry(inp, textvariable=var, width=9)
            en.grid(row=0, column=2 * i + 1)
            en.bind("<Return>", lambda _ev: self.plot_graphs())

        ttk.Button(inp, text="Plot", command=self.plot_graphs).grid(
            row=0, column=6, padx=(20, 6))
        ttk.Button(inp, text="Save picture", command=self.save_plot).grid(
            row=0, column=7)

        mode = ttk.Frame(inp)
        mode.grid(row=1, column=0, columnspan=8, sticky="w", pady=(10, 0))
        self.mode_var = tk.StringVar(value="grid")
        ttk.Radiobutton(mode, text="All parameters (small multiples)",
                        variable=self.mode_var, value="grid",
                        command=self.plot_graphs).pack(side="left")
        ttk.Radiobutton(mode, text="Overlay selected",
                        variable=self.mode_var, value="overlay",
                        command=self.plot_graphs).pack(side="left", padx=(16, 0))
        self.logy_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(mode, text="Log y-axis", variable=self.logy_var,
                        command=self.plot_graphs).pack(side="left", padx=(24, 0))

        # which curves go into the overlay
        sel = ttk.Frame(inp)
        sel.grid(row=2, column=0, columnspan=8, sticky="w", pady=(8, 0))
        ttk.Label(sel, text="Overlay curves:").pack(side="left", padx=(0, 8))
        default_on = ("M2", "rho2/rho1", "p02/p01")
        self.series_vars = {}
        for c in COLS[1:]:
            v = tk.BooleanVar(value=(c in default_on))
            self.series_vars[c] = v
            ttk.Checkbutton(sel, text=c, variable=v,
                            command=self._replot_if_overlay).pack(side="left", padx=4)

        self.plot = PlotCanvas(f)
        self.plot.pack(fill="both", expand=True, pady=(12, 0))

    def _replot_if_overlay(self):
        if self.mode_var.get() == "overlay":
            self.plot_graphs()

    def plot_graphs(self):
        try:
            g = self._gamma()
            start = float(self.g_start_var.get())
            stop = float(self.g_stop_var.get())
            step = float(self.g_step_var.get())
            machs = build_mach_list(start, stop, step)
            if len(machs) > 20000:
                raise ValueError("That sweep needs %d points. Use a larger step."
                                 % len(machs))
            data = [normal_shock(M, g) for M in machs]
        except ValueError as err:
            messagebox.showerror("Invalid input", str(err))
            self.status.set("Error: " + str(err).splitlines()[0])
            return

        xs = [r["M1"] for r in data]
        logy = self.logy_var.get()

        if self.mode_var.get() == "grid":
            panels = [{"title": c, "logy": logy,
                       "series": [(c, xs, [r[c] for r in data])]}
                      for c in COLS[1:]]
            what = "all 8 parameters"
        else:
            chosen = [c for c in COLS[1:] if self.series_vars[c].get()]
            if not chosen:
                messagebox.showinfo("Nothing selected",
                                    "Tick at least one curve to overlay.")
                return
            panels = [{"title": "Normal shock properties vs M1   (gamma = %g)" % g,
                       "logy": logy,
                       "series": [(c, xs, [r[c] for r in data]) for c in chosen]}]
            what = ", ".join(chosen)

        self.plot.show(panels)
        self.status.set("Plotted %s over M1 = %g to %g (%d points), gamma = %g%s"
                        % (what, start, stop, len(machs), g,
                           ",  log y-axis" if logy else ""))

    def save_plot(self):
        if not self.plot.panels:
            messagebox.showinfo("Nothing to save", "Draw a plot first.")
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".ps", initialfile="normal_shock_plots.ps",
            filetypes=[("PostScript", "*.ps"),
                       ("Encapsulated PostScript", "*.eps"),
                       ("All files", "*.*")])
        if not path:
            return
        c = self.plot.canvas
        c.postscript(file=path, colormode="color", x=0, y=0,
                     width=c.winfo_width(), height=c.winfo_height())
        self.status.set("Plot written to %s  (vector PostScript)" % path)


# ================================================================
if __name__ == "__main__":
    ShockApp().mainloop()

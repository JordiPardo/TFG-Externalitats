# regressio_bcn.py
# -*- coding: utf-8 -*-

from pathlib import Path
import sys

import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
import matplotlib.pyplot as plt


def main():
    # ---------- 1) Rutes segures ----------
    ROOT = Path(__file__).resolve().parent
    excel_path = ROOT / "accidents_barcelona_per_mes.xlsx"  # <-- mateix directori que aquest .py

    print(f"[INFO] Carpeta script: {ROOT}")
    print(f"[INFO] Fitxer Excel:  {excel_path}")

    if not excel_path.exists():
        print("[ERROR] No s'ha trobat l'Excel esperat. Assegura't que el fitxer "
              "'accidents_barcelona_per_mes.xlsx' és al MATEIX directori que aquest script.")
        sys.exit(1)

    # ---------- 2) Carregar dades ----------
    # S'esperen les columnes:
    # Any | Nom_mes | Nombre d'accidents | Num_mes | ZBE_Dummy | Covid_Dummy
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print("[ERROR] Problema llegint l'Excel:", e)
        sys.exit(1)

    cols_req = ["Any", "Nom_mes", "Nombre d'accidents", "Num_mes", "ZBE_Dummy", "Covid_Dummy"]
    missing = [c for c in cols_req if c not in df.columns]
    if missing:
        print(f"[ERROR] Falten columnes a l'Excel: {missing}")
        print("       Columns requerides: ", cols_req)
        sys.exit(1)

    # ---------- 3) Preparació: ordenar i crear tendència ----------
    df = df.sort_values(["Any", "Num_mes"]).reset_index(drop=True)
    df["t"] = np.arange(1, len(df) + 1)

    # Comprovacions bàsiques de NA
    if not df[["Nombre d'accidents", "ZBE_Dummy", "Covid_Dummy", "t", "Num_mes"]].notna().all().all():
        print("[ERROR] Hi ha valors buits (NA) en alguna columna clau.")
        print(df[["Nombre d'accidents", "ZBE_Dummy", "Covid_Dummy", "t", "Num_mes"]].isna().sum())
        sys.exit(1)

    # ---------- 4) Model OLS amb estacionalitat i errors HAC ----------
    # C(Num_mes) crea dummies mensuals automàticament; drop-first intern
    formula = "Q('Nombre d\\'accidents') ~ ZBE_Dummy + Covid_Dummy + t + C(Num_mes)"
    print("\n[INFO] Fórmula OLS:", formula)

    try:
        mod_ols = smf.ols(formula, data=df).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    except Exception as e:
        print("[ERROR] No s'ha pogut estimar el model OLS:", e)
        sys.exit(1)

    print("\n=== ACCIDENTS BCN (mensual) — OLS amb errors HAC (lag 12) ===")
    print(mod_ols.summary())

    # ---------- 5) Exportar coeficients OLS ----------
    coefs_ols = pd.DataFrame({
        "variable": mod_ols.params.index,
        "coef": mod_ols.params.values,
        "std_err": mod_ols.bse.values,
        "t_value": mod_ols.tvalues.values,
        "p_value": mod_ols.pvalues.values
    })
    out_ols = ROOT / "resultats_accidents_bcn_mensual_ols_hac.csv"
    coefs_ols.to_csv(out_ols, index=False)
    print(f"\n[OK] Coeficients OLS exportats a: {out_ols}")

    # ---------- 6) (Opcional) Model de robustesa: Poisson ----------
    try:
        mod_pois = smf.glm(formula, data=df, family=sm.families.Poisson()).fit()
        print("\n=== ACCIDENTS BCN (mensual) — Poisson (robustesa) ===")
        print(mod_pois.summary())

        coefs_pois = pd.DataFrame({
            "variable": mod_pois.params.index,
            "coef": mod_pois.params.values,
            "std_err": mod_pois.bse.values,
            # statsmodels GLM mostra z-values; si no, calculem aprox:
            "z_value": getattr(mod_pois, "tvalues", mod_pois.params / mod_pois.bse),
            "p_value": mod_pois.pvalues.values
        })
        out_pois = ROOT / "resultats_accidents_bcn_mensual_poisson.csv"
        coefs_pois.to_csv(out_pois, index=False)
        print(f"[OK] Coeficients Poisson exportats a: {out_pois}")
    except Exception as e:
        print("[AVÍS] No s'ha pogut estimar/exportar el model Poisson (continua igualment):", e)

    # ---------- 7) Gràfic observat vs ajustat (OLS) ----------
    try:
        df_plot = df.copy()
        df_plot["fitted_ols"] = mod_ols.fittedvalues

        plt.figure()
        plt.plot(df_plot["t"], df_plot["Nombre d'accidents"], marker="o", label="Observat")
        plt.plot(df_plot["t"], df_plot["fitted_ols"], marker="x", label="Ajustat (OLS)")
        plt.title("Barcelona — Accidents mensuals: observat vs. ajustat")
        plt.xlabel("Tendència temporal (t)")
        plt.ylabel("Nombre d'accidents")
        plt.legend()
        plt.tight_layout()

        png_path = ROOT / "accidents_bcn_observat_vs_ajustat.png"
        plt.savefig(png_path, dpi=140)
        print(f"[OK] Gràfic guardat a: {png_path}")
        # Si prefereixes veure'l a pantalla, descomenta:
        # plt.show()
    except Exception as e:
        print("[AVÍS] No s'ha pogut generar el gràfic (continua igualment):", e)


if __name__ == "__main__":
    main()

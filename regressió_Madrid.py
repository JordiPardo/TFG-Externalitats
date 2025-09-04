# -*- coding: utf-8 -*-
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
import statsmodels.api as sm
import matplotlib.pyplot as plt

def main():
    ROOT = Path(__file__).resolve().parent
    excel_path = ROOT / "accidents_madrid_per_mes.xlsx"   # <-- mateix directori que aquest .py

    print(f"[INFO] Carpeta script: {ROOT}")
    print(f"[INFO] Fitxer Excel:  {excel_path}")
    if not excel_path.exists():
        print("[ERROR] No s'ha trobat l'Excel esperat ('accidents_madrid_per_mes.xlsx').")
        sys.exit(1)

    # 1) Carregar dades
    try:
        df = pd.read_excel(excel_path)
    except Exception as e:
        print("[ERROR] Llegint l'Excel:", e)
        sys.exit(1)

    # S'esperen: Any | Mes_nom | Nombre_Accidents
    req = ["Any", "Mes_nom", "Nombre_Accidents"]
    miss = [c for c in req if c not in df.columns]
    if miss:
        print("[ERROR] Falten columnes:", miss)
        print("       Es requereixen:", req)
        sys.exit(1)

    # 2) Normalitzar mesos i crear Num_mes (1..12)
    mapa_mes = {
        "gener":1, "febrer":2, "març":3, "marc":3, "abril":4, "maig":5, "juny":6,
        "juliol":7, "agost":8, "setembre":9, "octubre":10, "novembre":11, "desembre":12,
        # també si venen Capitalitzats (tal com tens): 
        "Gener":1, "Febrer":2, "Març":3, "Marc":3, "Abril":4, "Maig":5, "Juny":6,
        "Juliol":7, "Agost":8, "Setembre":9, "Octubre":10, "Novembre":11, "Desembre":12
    }
    df["Num_mes"] = df["Mes_nom"].map(mapa_mes)
    if df["Num_mes"].isna().any():
        valors_rars = df.loc[df["Num_mes"].isna(), "Mes_nom"].unique()
        print("[ERROR] Hi ha mesos no reconeguts:", valors_rars)
        sys.exit(1)

    # 3) Dummies de polítiques i COVID
    # Madrid Central / ZBEDEP: 1 des de 2019
    df["MC_Dummy"] = (df["Any"] >= 2019).astype(int)
    # COVID: 2020–2021
    df["Covid_Dummy"] = df["Any"].between(2020, 2021).astype(int)

    # 4) Tendència temporal i ordenació
    df = df.sort_values(["Any", "Num_mes"]).reset_index(drop=True)
    df["t"] = np.arange(1, len(df) + 1)

    # 5) Checks ràpids
    must = ["Nombre_Accidents", "Num_mes", "MC_Dummy", "Covid_Dummy", "t"]
    if not df[must].notna().all().all():
        print("[ERROR] Valors buits en columnes clau.")
        print(df[must].isna().sum())
        sys.exit(1)

    # 6) OLS amb estacionalitat i errors HAC
    # C(Num_mes) crea dummies mensuals (gener és el base)
    formula = "Q('Nombre_Accidents') ~ MC_Dummy + Covid_Dummy + t + C(Num_mes)"
    print("\n[INFO] Fórmula OLS:", formula)

    try:
        mod_ols = smf.ols(formula, data=df).fit(cov_type="HAC", cov_kwds={"maxlags": 12})
    except Exception as e:
        print("[ERROR] Estimant OLS:", e); sys.exit(1)

    print("\n=== ACCIDENTS MADRID (mensual) — OLS amb errors HAC (lag 12) ===")
    print(mod_ols.summary())

    # 7) Exportar coeficients OLS
    coefs_ols = pd.DataFrame({
        "variable": mod_ols.params.index,
        "coef": mod_ols.params.values,
        "std_err": mod_ols.bse.values,
        "t_value": mod_ols.tvalues.values,
        "p_value": mod_ols.pvalues.values
    })
    out_ols = ROOT / "resultats_accidents_madrid_mensual_ols_hac.csv"
    coefs_ols.to_csv(out_ols, index=False)
    print(f"\n[OK] Coeficients OLS exportats a: {out_ols}")

    # 8) (Opcional) Robustesa Poisson
    try:
        mod_pois = smf.glm(formula, data=df, family=sm.families.Poisson()).fit()
        print("\n=== ACCIDENTS MADRID (mensual) — Poisson (robustesa) ===")
        print(mod_pois.summary())

        coefs_pois = pd.DataFrame({
            "variable": mod_pois.params.index,
            "coef": mod_pois.params.values,
            "std_err": mod_pois.bse.values,
            "z_value": getattr(mod_pois, "tvalues", mod_pois.params / mod_pois.bse),
            "p_value": mod_pois.pvalues.values
        })
        out_pois = ROOT / "resultats_accidents_madrid_mensual_poisson.csv"
        coefs_pois.to_csv(out_pois, index=False)
        print(f"[OK] Coeficients Poisson exportats a: {out_pois}")
    except Exception as e:
        print("[AVÍS] No s'ha pogut estimar/exportar el model Poisson:", e)

    # 9) Gràfic observat vs. ajustat (OLS)
    try:
        df_plot = df.copy()
        df_plot["fitted_ols"] = mod_ols.fittedvalues

        plt.figure()
        plt.plot(df_plot["t"], df_plot["Nombre_Accidents"], marker="o", label="Observat")
        plt.plot(df_plot["t"], df_plot["fitted_ols"], marker="x", label="Ajustat (OLS)")
        plt.title("Madrid — Accidents mensuals: observat vs. ajustat")
        plt.xlabel("Tendència temporal (t)")
        plt.ylabel("Nombre d'accidents")
        plt.legend()
        plt.tight_layout()

        png_path = ROOT / "accidents_madrid_observat_vs_ajustat.png"
        plt.savefig(png_path, dpi=140)
        print(f"[OK] Gràfic guardat a: {png_path}")
    except Exception as e:
        print("[AVÍS] No s'ha pogut generar el gràfic observat vs ajustat:", e)

    # 10) Gràfic barres coeficients mensuals (estacionalitat)
    try:
        df_mes = coefs_ols[coefs_ols["variable"].str.contains(r"C\(Num_mes\)\[T\.", regex=True)].copy()
        df_mes["mes_num"] = df_mes["variable"].str.extract(r"\[T\.(\d+)\]").astype(int)
        ordre = list(range(2, 13))  # gener és categoria base
        df_mes = df_mes.set_index("mes_num").loc[ordre].reset_index()
        labels_cat = {2:"febrer",3:"març",4:"abril",5:"maig",6:"juny",7:"juliol",
                      8:"agost",9:"setembre",10:"octubre",11:"novembre",12:"desembre"}
        df_mes["mes_nom"] = df_mes["mes_num"].map(labels_cat)

        plt.figure(figsize=(9,5.2))
        plt.bar(df_mes["mes_nom"], df_mes["coef"], yerr=df_mes["std_err"], capsize=4)
        plt.axhline(0, linewidth=0.8)
        plt.title("Madrid — Efecte mensual sobre els accidents (coeficients OLS)")
        plt.ylabel("Canvi respecte gener (accidents)")
        plt.xlabel("Mes")
        plt.xticks(rotation=35)
        plt.tight_layout()

        bar_path = ROOT / "coeficients_mensuals_madrid_ols.png"
        plt.savefig(bar_path, dpi=140)
        print(f"[OK] Gràfic estacionalitat guardat a: {bar_path}")
    except Exception as e:
        print("[AVÍS] No s'ha pogut generar el gràfic de coeficients mensuals:", e)


if __name__ == "__main__":
    main()
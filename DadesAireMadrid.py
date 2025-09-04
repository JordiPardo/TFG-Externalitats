import pandas as pd
import os

# Diccionari de magnituds rellevants
magnituds = {
    8: "NO2",
    9: "PM2.5",
    10: "PM10",
    12: "NOx",
    14: "O3"
}

# Ruta a la carpeta amb els fitxers
carpeta = "/Users/jordipardo/Desktop/tfg/dades aire"
fitxers = [f for f in os.listdir(carpeta) if f.endswith(".csv")]

llista_dfs = []

for fitxer in fitxers:
    print(f"Llegint fitxer: {fitxer}")
    ruta = os.path.join(carpeta, fitxer)
    df = pd.read_csv(ruta, sep=";", encoding="latin1")
    df.columns = df.columns.str.strip().str.upper()

    dies = [f"D{i:02d}" for i in range(1, 32)]

    df_llarg = df.melt(
        id_vars=["PROVINCIA", "MUNICIPIO", "ESTACION", "MAGNITUD", "PUNTO_MUESTREO", "ANO", "MES"],
        value_vars=dies,
        var_name="DIA",
        value_name="VALOR"
    )

    df_llarg["DIA"] = df_llarg["DIA"].str[1:].astype(int)
    df_llarg["ANO"] = pd.to_numeric(df_llarg["ANO"], errors="coerce")
    df_llarg["MES"] = pd.to_numeric(df_llarg["MES"], errors="coerce")
    df_llarg["DIA"] = pd.to_numeric(df_llarg["DIA"], errors="coerce")

    df_llarg["DATA"] = pd.to_datetime(
        df_llarg.rename(columns={"ANO": "year", "MES": "month", "DIA": "day"})[["year", "month", "day"]],
        errors="coerce"
    )

    df_llarg = df_llarg.dropna(subset=["DATA", "VALOR"])
    df_llarg["VALOR"] = pd.to_numeric(df_llarg["VALOR"], errors="coerce")

    llista_dfs.append(df_llarg)

# Combinar tots els anys
df_total = pd.concat(llista_dfs, ignore_index=True)
df_total["ANY"] = df_total["DATA"].dt.year
df_total["MES"] = df_total["DATA"].dt.month

# Filtrar només magnituds d’interès
df_total = df_total[df_total["MAGNITUD"].isin(magnituds.keys())]

# Agregació mensual
resultat = (
    df_total.groupby(["ANY", "MES", "MAGNITUD"])["VALOR"]
    .mean()
    .reset_index()
    .rename(columns={"VALOR": "MITJANA_VALOR"})
)

# Afegim el nom del contaminant
resultat["CONTAMINANT"] = resultat["MAGNITUD"].map(magnituds)

# Substituir número de mes per nom
noms_mes = {
    1: "gener", 2: "febrer", 3: "març", 4: "abril", 5: "maig", 6: "juny",
    7: "juliol", 8: "agost", 9: "setembre", 10: "octubre", 11: "novembre", 12: "desembre"
}
resultat["MES"] = resultat["MES"].map(noms_mes)
resultat["ORDRE_MES"] = resultat["MES"].map({v: k for k, v in noms_mes.items()})

# Reordenar i ordenar cronològicament
resultat = resultat[["ANY", "MES", "MAGNITUD", "CONTAMINANT", "MITJANA_VALOR", "ORDRE_MES"]]
resultat = resultat.sort_values(["ANY", "ORDRE_MES", "CONTAMINANT"]).drop(columns="ORDRE_MES")

# Exportar
resultat.to_excel("qualitat_aire_mensual_filtrat.xlsx", index=False)
print("Excel generat: qualitat_aire_mensual_filtrat.xlsx")
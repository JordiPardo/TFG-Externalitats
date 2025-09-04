import pandas as pd
import glob
import os

# 📁 Ruta als fitxers
carpeta = "/Users/jordipardo/Desktop/accidents_Madrid/"
fitxers = glob.glob(os.path.join(carpeta, "*.csv"))

# Columnes habituals
columnes_target = {
    'FECHA': ['FECHA', 'Fecha', 'fecha'],
    'DISTRITO': ['DISTRITO', 'Distrito', 'distrito'],
    'Tipo Vehiculo': ['Tipo Vehiculo', 'TIPO VEHÍCULO', 'TIPO VEHICULO', 'tipo_vehiculo'],
    'Tipo Accident': ['TIPO ACCIDENTE', 'Tipo Accidente', 'tipo_accidente']
}

# Columnes mínimes necessàries
columnes_essencials = ['FECHA', 'DISTRITO', 'Tipo Vehiculo']

# 🔍 Funció per filtrar i renombrar columnes, inclòs el número d’accident
def filtra_columnes(df, nom_fitxer, any_fitxer):
    # Detectar la columna d'identificador segons l'any
    if any_fitxer <= 2018:
        id_col = 'Nº PARTE'
    else:
        # El nom pot portar BOM al principi
        possibles = [col for col in df.columns if 'num_expediente' in col.lower()]
        if possibles:
            id_col = possibles[0]
        else:
            print(f"❌ Falta la columna identificadora 'num_expediente' a {nom_fitxer}")
            return None
    if id_col not in df.columns:
        print(f"❌ Falta la columna identificadora '{id_col}' a {nom_fitxer}")
        return None
    df = df.rename(columns={id_col: 'id_accident'})

    # Renombrar altres columnes
    mapping = {}
    for col_final, variants in columnes_target.items():
        for variant in variants:
            if variant in df.columns:
                mapping[variant] = col_final
                break
        else:
            if col_final in columnes_essencials:
                print(f"❌ Falta la columna essencial '{col_final}' a {nom_fitxer}")
                return None
            else:
                print(f"⚠️ Falta la columna opcional '{col_final}' a {nom_fitxer}")
    df = df.rename(columns=mapping)

    # Retornem les columnes seleccionades
    return df[['id_accident'] + [col for col in columnes_target if col in df.columns]]

# 📦 Combinació dels fitxers
dades = []

for fitxer in fitxers:
    nom = os.path.basename(fitxer)
    try:
        any_fitxer = int(nom.split("_")[0])
    except:
        print(f"⚠️ No s'ha pogut identificar l'any del fitxer: {nom}")
        continue

    try:
        df_raw = pd.read_csv(fitxer, encoding='latin-1', sep=';', on_bad_lines='skip')
        df_filtrat = filtra_columnes(df_raw, nom, any_fitxer)
        if df_filtrat is not None:
            df_filtrat['Any'] = any_fitxer
            df_filtrat['FECHA'] = pd.to_datetime(df_filtrat['FECHA'], errors='coerce')
            df_filtrat = df_filtrat.dropna(subset=['FECHA', 'id_accident'])

            # ✅ Eliminar duplicats per id d’accident
            df_filtrat = df_filtrat.drop_duplicates(subset=['id_accident'])

            dades.append(df_filtrat)
            print(f"✅ Fitxer netejat: {nom} ({len(df_filtrat)} accidents únics)")
    except Exception as e:
        print(f"❌ Error amb {nom}: {e}")

# 🔁 Unió i exportació
if dades:
    df_total = pd.concat(dades, ignore_index=True)
    sortida = os.path.join(carpeta, "accidents_madrid_net_per_id.xlsx")
    df_total.to_excel(sortida, index=False)
    print(f"\n✅ Arxiu final exportat: {sortida}")
else:
    print("\n⚠️ Cap fitxer vàlid per combinar.")
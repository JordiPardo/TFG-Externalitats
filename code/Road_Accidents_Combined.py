import pandas as pd
import os

carpeta = "."
llista_dfs = []

for fitxer in os.listdir(carpeta):
    if fitxer.endswith(".csv") and "bcn" in fitxer.lower():
        try:
            ruta = os.path.join(carpeta, fitxer)
            df = pd.read_csv(ruta, encoding="latin1")
            df.columns = df.columns.str.strip()

            # Possibles noms per cada columna clau
            possibles_any = ['Any', 'NK Any', 'NK_Any']
            possibles_districte = ['Nom districte', 'Nom_districte']
            possibles_tipus = [
                'Descripció tipus accident',
                'Descripci¢ tipus accident',
                'Descripcio_tipus_accident',
                'Tipus_accident'
            ]
            possibles_mes = ['Nom_mes', 'nom_mes', 'Mes', 'mes', 'Nom mes', 'nom mes']

            col_any = next((col for col in possibles_any if col in df.columns), None)
            col_districte = next((col for col in possibles_districte if col in df.columns), None)
            col_tipus = next((col for col in possibles_tipus if col in df.columns), None)
            col_mes = next((col for col in possibles_mes if col in df.columns), None)

            if col_any and col_districte and col_tipus:
                columnes = [col_any, col_districte, col_tipus]
                noms_columns = {'Any': col_any, 'Districte': col_districte, 'Tipus accident': col_tipus}
                
                if col_mes:
                    columnes.append(col_mes)
                    noms_columns['Nom_mes'] = col_mes
                    print(f"📅 S'ha detectat la columna de mes ({col_mes}) a: {fitxer}")
                else:
                    print(f"⚠️ Sense columna de mes a: {fitxer}")

                df_filtrat = df[columnes].copy()
                df_filtrat = df_filtrat.rename(columns={v: k for k, v in noms_columns.items()})

                if 'Nom_mes' in df_filtrat.columns:
                    df_filtrat['Nom_mes'] = df_filtrat['Nom_mes'].str.strip().str.lower()

                llista_dfs.append(df_filtrat)
                print(f"✅ Fitxer afegit: {fitxer}")
            else:
                print(f"❌ Columnes no trobades a: {fitxer}")
                print(f"   → Any: {col_any}, Districte: {col_districte}, Tipus: {col_tipus}")

        except Exception as e:
            print(f"⚠️ Error amb el fitxer {fitxer}: {e}")

# Unificació final
df_bcn_total = pd.concat(llista_dfs, ignore_index=True)
df_bcn_total.to_excel("accidents_Barcelona_unificat.xlsx", index=False, sheet_name="Accidents BCN")

print("✅ Fitxer Excel creat: accidents_Barcelona_unificat.xlsx")

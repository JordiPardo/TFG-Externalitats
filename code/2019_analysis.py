import pandas as pd

# Carregar l'arxiu net
df = pd.read_excel("accidents_madrid_net_per_id.xlsx")

# Convertim la data correctament
df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
df = df.dropna(subset=['FECHA'])

# Eliminar duplicats per id_accident (si no s’ha fet abans)
df_unics = df.drop_duplicates(subset=['id_accident'])

# Comptar quants accidents únics hi ha per any
accidents_per_any = df_unics.groupby(df_unics['FECHA'].dt.year).size()

print("📊 Accidents únics per any:")
print(accidents_per_any)

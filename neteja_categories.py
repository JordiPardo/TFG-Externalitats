import pandas as pd

# 📥 Carrega l’Excel original
df = pd.read_excel("accidents_madrid_net_per_id.xlsx")

# 🔤 Funció per netejar caràcters mal interpretats
def neteja_text(text):
    if isinstance(text, str):
        try:
            return text.encode('latin1').decode('utf-8')
        except:
            return text
    return text

# 🧼 Columnes a netejar
columnes_netejar = ['Tipo Accident', 'Tipo Vehiculo', 'DISTRITO']

for col in columnes_netejar:
    if col in df.columns:
        print(f"\n🧾 Categories ORIGINALS de {col}:")
        print(df[col].dropna().unique())

        # Neteja
        df[col] = df[col].apply(neteja_text)

        print(f"\n✅ Categories NETEJADES de {col}:")
        print(df[col].dropna().unique())

# 💾 Desa l’arxiu netejat
df.to_excel("accidents_madrid_net_per_id_netejat.xlsx", index=False)
print("\n💾 Fitxer netejat desat com a 'accidents_madrid_net_per_id_netejat.xlsx'")
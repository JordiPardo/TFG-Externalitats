import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import unicodedata

# Carregar dades
df = pd.read_excel("accidents_madrid_net_per_id_netejat.xlsx", sheet_name="Sheet1")

# --------- Neteja general de columnes i valors ---------
df = df.rename(columns=lambda x: x.strip())
df["Tipo Accident"] = df["Tipo Accident"].str.strip()
df["Tipo Vehiculo"] = df["Tipo Vehiculo"].str.strip().str.upper()

# 🔤 Normalització dels noms de districte (accents, majúscules, espais)
def normalitza_text(text):
    if pd.isna(text):
        return text
    text = text.strip().upper()
    text = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in text if not unicodedata.combining(c))

df["DISTRITO"] = df["DISTRITO"].apply(normalitza_text)

# --------- GRÀFIC 1: Nombre d’accidents per any ---------
fig1, ax1 = plt.subplots(figsize=(8, 5))
df['Any'].value_counts().sort_index().plot(kind='bar', ax=ax1)
ax1.set_title("Nombre d’accidents per any")
ax1.set_xlabel("Any")
ax1.set_ylabel("Nombre d’accidents")
plt.tight_layout()
fig1.savefig("graf1_accidents_per_any.png")

# --------- GRÀFIC 2: Accidents per tipus de vehicle (Top 10) ---------
fig2, ax2 = plt.subplots(figsize=(10, 6))
df['Tipo Vehiculo'].value_counts().head(10).plot(kind='bar', ax=ax2)
ax2.set_title("Accidents per tipus de vehicle (Top 10)")
ax2.set_xlabel("Tipus de vehicle")
ax2.set_ylabel("Nombre d’accidents")
plt.tight_layout()
fig2.savefig("graf2_accidents_per_tipus_vehicle.png")

# --------- GRÀFIC 3: Accidents per districte (Top 10) ---------
fig3, ax3 = plt.subplots(figsize=(10, 6))
df['DISTRITO'].value_counts().head(10).plot(kind='bar', ax=ax3)
ax3.set_title("Accidents per districte (Top 10)")
ax3.set_xlabel("Districte")
ax3.set_ylabel("Nombre d’accidents")
plt.tight_layout()
fig3.savefig("graf3_accidents_per_districte.png")

# --------- GRÀFIC 4: Heatmap de tipus d’accident per districte ---------
heatmap_data = pd.crosstab(df['DISTRITO'], df['Tipo Accident'])

fig4, ax4 = plt.subplots(figsize=(14, 10))
sns.heatmap(heatmap_data, cmap="Reds", linewidths=.5, cbar=True, annot=False, ax=ax4)
ax4.set_title("Heatmap de tipus d’accident per districte")
plt.tight_layout()
fig4.savefig("graf4_heatmap_accidents.png")
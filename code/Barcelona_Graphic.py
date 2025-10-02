import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Carreguem les dades netejades
df = pd.read_excel("accidents_barcelona_netejat.xlsx")

# ----------- GRÀFIC 1: Nombre d’accidents per any -----------
fig1, ax1 = plt.subplots(figsize=(8, 5))
df['Any'].value_counts().sort_index().plot(kind='bar', ax=ax1)
ax1.set_title("Nombre d’accidents per any")
ax1.set_xlabel("Any")
ax1.set_ylabel("Nombre d’accidents")
plt.tight_layout()
fig1.savefig("graf1_bcn_accidents_per_any.png")

# ----------- GRÀFIC 2: Accidents per districte (Top 10) -----------
fig2, ax2 = plt.subplots(figsize=(10, 6))
df['Districte'].value_counts().head(10).plot(kind='bar', ax=ax2)
ax2.set_title("Accidents per districte (Top 10)")
ax2.set_xlabel("Districte")
ax2.set_ylabel("Nombre d’accidents")
plt.tight_layout()
fig2.savefig("graf2_bcn_accidents_per_districte.png")

# ----------- GRÀFIC 3: Heatmap tipus accident per districte -----------
heatmap_data = pd.crosstab(df['Districte'], df['Tipus accident'])

fig3, ax3 = plt.subplots(figsize=(14, 10))
sns.heatmap(heatmap_data, cmap="Reds", linewidths=.5, annot=False, cbar=True, ax=ax3)
ax3.set_title("Heatmap de tipus d’accident per districte (Barcelona)")
plt.tight_layout()
fig3.savefig("graf3_bcn_heatmap_accidents.png")

print("Gràfics generats i guardats amb èxit.")

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Carrega de dades Barcelona
df = pd.read_excel("qualitat_aire_bcn_tipus.xlsx", sheet_name="Sheet1")
df['ANY'] = df['ANY'].astype(int)

# Agrupem per contaminant i any (ignorem la columna TIPUS)
df_agrupat = df.groupby(['ANY', 'CONTAMINANT'])['MITJANA_VALOR'].mean().reset_index()

# Crear carpeta per guardar gràfics
output_dir = "grafics_bcn_comparables"
os.makedirs(output_dir, exist_ok=True)

# Estil gràfic
sns.set(style="whitegrid")

# Límits OMS/UE per comparar (si cal)
limits = {
    'NO2': 40,
    'PM10': 20,
    'PM2.5': 10,
    'O3': 100,     # Orientatiu per 8h, no sempre anual
    'NOx': 30      # No oficial, per visualitzar
}

# Generar gràfics per cada contaminant
for contaminant in df_agrupat['CONTAMINANT'].unique():
    df_cont = df_agrupat[df_agrupat['CONTAMINANT'] == contaminant]

    # Gràfic de línies: evolució temporal mitjana
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df_cont, x='ANY', y='MITJANA_VALOR', marker='o')
    plt.title(f'Evolució anual del {contaminant} a Barcelona (mitjana de totes les estacions)')
    plt.ylabel('Mitjana anual (µg/m³)')
    plt.xlabel('Any')

    # Afegim límit si existeix
    if contaminant in limits:
        plt.axhline(limits[contaminant], color='red', linestyle='--', label=f'Límit OMS/UE ({limits[contaminant]} µg/m³)')
        plt.legend()

    # Guardar gràfic
    plt.tight_layout()
    plt.savefig(f"{output_dir}/{contaminant}_bcn_evolucio.png")
    plt.close()
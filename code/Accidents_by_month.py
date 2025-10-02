import pandas as pd

# 📥 Carreguem el fitxer net
df = pd.read_excel("accidents_madrid_net_per_id.xlsx")

# 📆 Convertim la data i eliminem files amb errors
df['FECHA'] = pd.to_datetime(df['FECHA'], errors='coerce')
df = df.dropna(subset=['FECHA'])

# 🗓 Afegim Any i Mes (número)
df['Any'] = df['FECHA'].dt.year
df['Mes_num'] = df['FECHA'].dt.month

# 🧾 Creem columna amb nom del mes
mesos_cat = {
    1: 'Gener', 2: 'Febrer', 3: 'Març', 4: 'Abril',
    5: 'Maig', 6: 'Juny', 7: 'Juliol', 8: 'Agost',
    9: 'Setembre', 10: 'Octubre', 11: 'Novembre', 12: 'Desembre'
}
df['Mes_nom'] = df['Mes_num'].map(mesos_cat)

# 📊 Agrupem el nombre d'accidents per Any i Mes
accidents_mes = df.groupby(['Any', 'Mes_num', 'Mes_nom']).size().reset_index(name='Nombre_Accidents')

# 📤 Exportem a un Excel nou
accidents_mes = accidents_mes.sort_values(['Any', 'Mes_num'])
accidents_mes.to_excel("accidents_madrid_per_mes.xlsx", index=False)

print("✅ Excel generat: accidents_madrid_per_mes.xlsx")

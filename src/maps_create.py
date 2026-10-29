import os

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
from azure.cosmos import CosmosClient
import pandas as pd

# Konfiguracja połączenia z Cosmos DB
url = os.getenv('COSMOS_URL')
key = os.getenv('COSMOS_KEY')
database_name = os.getenv('COSMOS_DATABASENAME')
container_name = os.getenv('COSMOS_CONTAINER_NAME')

# Tworzenie klienta Cosmos DB
client = CosmosClient(url, key)
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

# Funkcja do pobierania danych z Cosmos DB
def fetch_data_from_cosmos():
    query = "SELECT * FROM c"
    items = list(container.query_items(query, enable_cross_partition_query=True))
    data = []
    for item in items:
        data.append(item)
    df = pd.DataFrame(data)

    return df

# Pobranie danych z Cosmos DB
df = fetch_data_from_cosmos()
df.drop(columns=['partitionKey','_rid','_self','_etag','_attachments','_ts'],inplace=True)
df.sort_values(by='stacja', ascending=True, inplace=True)
df['temperatura'] = df['temperatura'].astype(float)
df['cisnienie'] = df['cisnienie'].astype(float)
df['wilgotnosc_wzgledna'] = df['wilgotnosc_wzgledna'].astype(float)
df['suma_opadu'] = df['suma_opadu'].astype(float)
df['lat'] = df['lat'].astype(float)
df['lon'] = df['lon'].astype(float)

# Funkcja do tworzenia mapy i zapisywania jej do pliku
def create_and_save_map(parameter, title, filename):
    plt.figure(figsize=(16, 12))
    map = Basemap(llcrnrlon=13.9, llcrnrlat=48.8, urcrnrlon=25.5, urcrnrlat=55.1, resolution='i', projection='merc', epsg=2180)
    map.drawmapboundary(fill_color='lightsteelblue')
    map.fillcontinents(color='white', lake_color='lightsteelblue')
    map.drawcoastlines()
    map.drawcountries()

    x, y = map(df['lon'].astype(float).values, df['lat'].astype(float).values)
    map.scatter(x, y, marker='o', color='black', s=6)

    for i in range(len(df)):
        label = f"{df[parameter].iloc[i]}"

        if parameter == 'temperatura':
            label += '°C'
            color = 'r'
        elif parameter == 'cisnienie':
            label += ' hPa'
            color = 'purple'
        elif parameter == 'suma_opadu':
            label += ' mm'
            color = 'b'
        elif parameter == 'wilgotnosc_wzgledna':
            label += '%'
            color = 'g'

        if df['stacja'].iloc[i] in ['Kasprowy Wierch', 'Śnieżka', 'Kołobrzeg']:
            plt.annotate(label, (x[i], y[i]), textcoords="offset points", xytext=(0, -10),
                         color=color, fontsize=10, ha='center', va='center', zorder=10, style='normal')
        elif df['stacja'].iloc[i] == 'Mikołajki':
            plt.annotate(label, (x[i], y[i]), textcoords="offset points", xytext=(-6, 6),
                         color=color, fontsize=10, ha='left', va='center', zorder=10, style='normal')
        elif df['stacja'].iloc[i] == 'Zakopane':
            plt.annotate(label, (x[i], y[i]), textcoords="offset points", xytext=(2, 8),
                         color=color, fontsize=10, ha='center', va='center', zorder=10, style='normal')
        else:
            plt.annotate(label, (x[i], y[i]), textcoords="offset points", xytext=(6, 0),
                         color=color, fontsize=10, ha='left', va='center', zorder=10, style='normal')

    plt.title(f'{title} (dane ze stacji synoptycznych)', style='normal', fontsize=20)
    plt.figtext(0.192, 0.09, 'Źródłem pochodzenia danych jest Instytut Meteorologii i Gospodarki Wodnej (IMGW PiB)',
                style='italic', fontsize=12, ha='left', va='bottom')

    # Zapisanie do pliku
    plt.savefig(filename)
    plt.show(bbox_inches='tight')
    plt.close()

# Tworzenie i zapisywanie map dla różnych parametrów
create_and_save_map('temperatura', 'Rozkład temperatury na obszarze Polski', 'mapy/temperatura.png')
create_and_save_map('cisnienie', 'Rozkład ciśnienia na obszarze Polski', 'mapy/cisnienie.png')
create_and_save_map('suma_opadu', 'Rozkład sumy opadów na obszarze Polski', 'mapy/suma_opadu.png')
create_and_save_map('wilgotnosc_wzgledna', 'Rozkład wilgotności względnej na obszarze Polski', 'mapy/wilgotnosc_wzgledna.png')

print('Wszystkie mapy zostały wygnerowane poprawnie!')
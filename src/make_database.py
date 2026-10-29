import os
import pandas as pd
from azure.cosmos import CosmosClient, PartitionKey, exceptions

# Metoda aktualizująca dane w konkretnym kontenerze
def upsert_item(container, data):
    try:
        # Sprawdzanie istnienia dokumentu
        existing_item = container.read_item(item=data['id'], partition_key=data['partitionKey'])
        print(f"Dokument z id '{data['id']}' istnieje, aktualizacja danych.")

        # Aktualizacja istniejącego dokumentu
        container.replace_item(item=existing_item, body=data)
        print(f"Dokument z id '{data['id']}' został zaktualizowany.")

    except exceptions.CosmosResourceNotFoundError:
        # Dodanie nowego dokumentu
        container.create_item(body=data)
        print(f"Dokument z id '{data['id']}' został dodany.")


df = pd.read_csv('imgw_data.csv')  # Wczytywanie danych z DataFram'u

# Klucz główny i URI CosmosDB
url = os.getenv('COSMOS_URL')
key = os.getenv('COSMOS_KEY')

# Nazwa bazy danych i kontenera
database_name = os.getenv('COSMOS_DATABASENAME')
container_name = os.getenv('COSMOS_CONTAINER_NAME')

# Utworzenie klienta CosmosDB
client = CosmosClient(url, key)

# Utworzenie bazy danych
database = client.create_database_if_not_exists(id=database_name)
print(f"Baza danych '{database_name}' utworzona lub już istnieje.")

# Definiowanie klucza partycji
partition_key = PartitionKey(path="/partitionKey")

# Utworzenie kontenera
container = database.create_container_if_not_exists(
    id=container_name,
    partition_key=partition_key,
    offer_throughput=1000
)
print(f"Kontener '{container_name}' utworzony lub już istnieje.")

# Przetwarzanie danych z pliku CSV i aktualizacja lub dodanie dokumentów
for i in range(len(df)):
    id_stacji = df.iloc[i]["id_stacji"]
    station = df.iloc[i]["stacja"]
    hour = df.iloc[i]["godzina_pomiaru"]
    temp = df.iloc[i]["temperatura"]
    wind = df.iloc[i]["predkosc_wiatru"]
    humidity = df.iloc[i]["wilgotnosc_wzgledna"]
    precipation = df.iloc[i]["suma_opadu"]
    pressure = df.iloc[i]["cisnienie"]
    lat = df.iloc[i]["lat"]
    lon = df.iloc[i]["lon"]

    # Przygotowanie danych dokumentu
    data = {
        "id": str(id_stacji),
        "stacja": str(station),
        "temperatura": str(temp),
        "predkosc_wiatru": str(wind),
        "wilgotnosc_wzgledna": str(humidity),
        "cisnienie": str(pressure),
        "suma_opadu": str(precipation),
        "lat": str(lat),
        "lon": str(lon),
        "godzina_pomiaru": str(hour),
        "partitionKey": "weather",
    }

    # Aktualizacja lub dodanie dokumentu
    upsert_item(container, data)

print("Dane zostały zaktualizowane lub dodane do kontenera.")
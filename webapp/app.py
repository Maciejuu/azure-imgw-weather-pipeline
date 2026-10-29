from flask import Flask, render_template
from azure.storage.blob import BlobServiceClient
from azure.cosmos import exceptions, CosmosClient, PartitionKey
import os

app = Flask(__name__)

# Pobieranie zmiennych środowiskowych
COSMOS_URL = os.getenv('COSMOS_URL')
COSMOS_KEY = os.getenv('COSMOS_KEY')
COSMOS_DATABASE_NAME = os.getenv('COSMOS_DATABASE_NAME')
COSMOS_CONTAINER_NAME = os.getenv('COSMOS_CONTAINER_NAME')
STORAGE_CONNECTION_STRING = os.getenv('STORAGE_CONNECTION_STRING')
STORAGE_CONTAINER_NAME = os.getenv('STORAGE_CONTAINER_NAME')

# Inicjalizacja klienta Cosmos DB
client = CosmosClient(COSMOS_URL, COSMOS_KEY)
database = client.get_database_client(COSMOS_DATABASE_NAME)
container = database.get_container_client(COSMOS_CONTAINER_NAME)

# Inicjalizacja klienta Blob Storage
blob_service_client = BlobServiceClient.from_connection_string(STORAGE_CONNECTION_STRING)
blob_container_client = blob_service_client.get_container_client(STORAGE_CONTAINER_NAME)

# Funkcja do pobierania danych z Cosmos DB
def fetch_data_from_cosmos_db():
    try:
        query = "SELECT * FROM c"
        items = list(container.query_items(query, enable_cross_partition_query=True))
        data = [
            {
                'id': item['id'],
                'stacja': item['stacja'],
                'temperatura': item['temperatura'],
                'predkosc_wiatru': item['predkosc_wiatru'],
                'cisnienie': item['cisnienie'],
                'suma_opadu': item['suma_opadu'],
                'wilgotnosc_wzgledna': item['wilgotnosc_wzgledna'],
                'godzina_pomiaru': item['godzina_pomiaru']
            } for item in items
        ]
        return data
    except exceptions.CosmosHttpResponseError as e:
        print(f'Error: {e.message}')
        return []

# Funkcja do pobierania listy obrazów z Blob Storage
def get_images():
    blob_list = blob_container_client.list_blobs()
    images = [blob.name for blob in blob_list if blob.name.endswith('.png')]
    print("Pobrane obrazy:", images)  # Logowanie do konsoli
    return images

@app.route('/')
def index():
    data = fetch_data_from_cosmos_db()
    images = get_images()
    image_urls = [blob_container_client.get_blob_client(image).url for image in images]
    return render_template('index.html', data=data, image_urls=image_urls)

@app.route('/mapy/<image_name>')
def image(image_name):
    blob_client = blob_container_client.get_blob_client(image_name)
    image_url = blob_client.url
    print(f'Przekierowywanie do obrazu: {image_url}')  # Logowanie do konsoli
    return redirect(image_url)

if __name__ == '__main__':
    app.run(debug=True)


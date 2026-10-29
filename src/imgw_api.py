import requests
import json
import pandas as pd
from geopy.geocoders import ArcGIS, Nominatim
from geopy.exc import GeocoderServiceError


# Metoda mająca na celu pobranie danych z API, które następnie zapisywane są do ramki danych DataFrame
def get_data_from_api(url):
    response = requests.get(url)  # Wysłanie zapytania do strony internetowej
    data = response.json()  # Pobranie danych ze strony internetowej, które są w formie JSON

    df = pd.DataFrame(data)  # Zapisanie danych do ramki danych DataFrame
    df = df[df['stacja'] != 'Platforma']  # Celowe usunięcie jednej ze stacji meteorologicznych, którą ciężko geokodować

    # Konwersja kolumny 'godzina_pomiaru' na liczby całkowite
    df['godzina_pomiaru'] = pd.to_numeric(df['godzina_pomiaru'], errors='coerce').fillna(0).astype(int)

    # Dodanie 2 do każdej wartości w kolumnie "godzina_pomiaru" ze względu na czas UTC+2
    df['godzina_pomiaru'] = df['godzina_pomiaru'] + 2

    return df

# Metoda mająca na celu geokodowanie miejscowości wykorzystując przy tym zabezpieczenie dwóch geokoderów
def geocode_with_fallback(station, primary_geolocator, secondary_geolocator):
    try:
        location = primary_geolocator.geocode(station)
        if not location:
            raise GeocoderServiceError("Główny geocoder nie działa!")
    except GeocoderServiceError:
        try:
            location = secondary_geolocator.geocode(station)
        except GeocoderServiceError:
            location = None
    return location

# Metoda georeferująca
def georeference(df):
    df.sort_values(by='stacja', ascending=True, inplace=True)
    stations = df['stacja'].values[:]

    lat = []
    lon = []

    arcgis_geolocator = ArcGIS()
    nominatim_geolocator = Nominatim(user_agent="kubamaciejak@gmail.com")

    # Instrukcje warunkowe, w celu prawidłowego pobrania danych dotyczących szerokości i długości geograficznej
    for station in stations:
        if station == 'Gorzów':
            query = station + ' Wielkopolski, Poland'
        elif station == 'Olsztyn':
            query = station + ', Warmińsko-Mazurskie, Poland'
        elif station == 'Leszno' or station == 'Koło':
            query = station + ', Wielkopolskie, Poland'
        else:
            query = station + ', Poland'

        location = geocode_with_fallback(query, arcgis_geolocator, nominatim_geolocator)

        if location:
            lat.append(location.latitude)
            lon.append(location.longitude)
        else:
            lat.append(None)
            lon.append(None)

    df['lat'] = lat
    df['lon'] = lon

    return df


url = 'https://danepubliczne.imgw.pl/api/data/synop/' # Adres URL do API IMGW

df = get_data_from_api(url)

df = georeference(df)

df.to_csv('imgw_data.csv', index=False)

print("Dane zostały wygenerowane prawidłowo!")
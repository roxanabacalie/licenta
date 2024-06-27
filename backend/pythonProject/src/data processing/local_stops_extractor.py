import csv
import requests


def fetch_data(api_url, headers):
    try:
        response = requests.get(api_url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print("Error: Failed to fetch data. Status code:", response.status_code)
            return None
    except Exception as e:
        print("Error:", e)
        return None


def save_stops_to_csv(stops_data, file_name):
    if stops_data is None:
        print("No stops data to save.")
        return
    try:
        with open(file_name, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Stop ID', 'Stop Name', 'Stop Latitude', 'Stop Longitude'])
            for stop in stops_data:
                writer.writerow([stop['stop_id'], stop['stop_name'], stop['stop_lat'], stop['stop_lon']])
        print(f"Data successfully saved to {file_name}")
    except IOError as e:
        print(f"Error saving data to {file_name}: {e}")


def main():
    api_url_stops = "https://api.tranzy.ai/v1/opendata/stops"
    headers = {
        "Accept": "application/json",
        "X-API-KEY": "J0g4leUL612yf4gUCt9kh3k3UZ7WsAxF7rkZIOEz",
        "X-Agency-Id": "1"
    }

    stops = fetch_data(api_url_stops, headers)
    csv_file_name = '../../data/iasi/iasi_all_stops_data.csv'
    save_stops_to_csv(stops, csv_file_name)


if __name__ == "__main__":
    main()

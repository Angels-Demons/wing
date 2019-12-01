import requests
from requests.auth import HTTPBasicAuth

# URL = "http://localhost:8000/scooter/announce"
# URL = "5.253.27.84/bicyle"
URL = "http://5.253.27.84/scooter/announce"


def announce(device_code=1234, latitude=35.703276, longitude=51.355876, battery=0, device_status=1,
             gps_board_connected=True, gps_valid=True, alerted=False,
             user='tcp_server', password='tcp_server@123'):
    # defining a params dict for the parameters to be sent to the API
    PARAMS = {
        'device_code': device_code,
        'latitude': latitude,
        'longitude': longitude,
        'battery': battery,
        'device_status': device_status,
        'gps_board_connected': gps_board_connected,
        'gps_valid': gps_valid,
        'alerted': alerted,
    }

    # sending get request and saving the response as response object
    r = requests.get(url=URL, params=PARAMS, auth=HTTPBasicAuth(user, password))

    # extracting data in json format
    print(r.text)
    data = r.json()
    print(data)

announce()


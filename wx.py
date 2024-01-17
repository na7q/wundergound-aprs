import requests
from socket import *
import time
from datetime import datetime

def aprs(formatted_time, wind_direction, wind_speed, temp, humidity, pressure_mbar, wind_gust):
    # APRS-IS login info
    serverHost = 'rotate.aprs2.net'
    serverPort = 14580
    aprsUser = 'CALLSIGN'
    aprsPass = 'PASSCODE'

    # APRS packet
    btext = '@{}z4610.74N/12259.16W_{:03d}/{:03d}g{:03d}t{:03d}h{}b{:05.0f}KWALONGV153'.format(formatted_time, int(wind_direction), int(wind_speed), int(wind_gust), int(temp), humidity, pressure_mbar * 10)
    print("@{}z4610.74N/12259.16W_{:03d}/{:03d}g{:03d}t{:03d}h{}b{:05.0f}KWALONGV153".format(formatted_time, int(wind_direction), int(wind_speed), int(wind_gust), int(temp), humidity, pressure_mbar * 10))

    # create socket & connect to server
    sSock = socket(AF_INET, SOCK_STREAM)
    sSock.connect((serverHost, serverPort))
    # logon
    sSock.send(('user %s pass %s vers NA7Q Python\n' % (aprsUser, aprsPass)).encode())
    sSock.send(('%s>APRS:%s\n' % (aprsUser, btext)).encode())

    sSock.shutdown(0)
    sSock.close()

def get_weather_data(api_key, station_id):
    url = f"https://api.weather.com/v2/pws/observations/current?stationId={station_id}&format=json&units=e&apiKey={api_key}"

    response = requests.get(url)
    data = response.json()

    return data

def inHg_to_mbar(pressure_inHg):
    return pressure_inHg * 33.8639

def format_obs_time(obs_time_utc):
    # Convert string to datetime object
    obs_time = datetime.strptime(obs_time_utc, "%Y-%m-%dT%H:%M:%SZ")
    
    # Format as desired (remove colons and 'Z')
    formatted_obs_time = obs_time.strftime("%H%M%S")
    
    return formatted_obs_time


def print_weather_info(weather_data):
    observation = weather_data.get("observations", [])[0]

    if observation:
        imperial_data = observation.get("imperial", {})
        temp = imperial_data.get("temp")
        wind_speed = imperial_data.get("windSpeed")
        wind_gust = imperial_data.get("windGust")
        pressure_inHg = imperial_data.get("pressure")
        humidity = observation.get("humidity")
        pressure_mbar = inHg_to_mbar(pressure_inHg)
        wind_direction = observation.get("winddir")
        obs_time_utc = observation.get("obsTimeUtc")
        formatted_time = format_obs_time(obs_time_utc)

        print(f"Observation Time (UTC): {obs_time_utc}")
        print(f"Temperature: {temp}°F")
        print(f"Wind Speed: {wind_speed} mph")
        print(f"Wind Gust: {wind_gust} mph")
        print(f"Pressure: {pressure_mbar:.2f} mbar")
        print(f"Humidity: {humidity}%")
        print(f"Wind Direction: {wind_direction}°")
        aprs(formatted_time, wind_direction, wind_speed, temp, humidity, pressure_mbar, wind_gust)

    else:
        print("No observation data available.")

if __name__ == "__main__":
    api_key = "API_KEY"
    station_id = "STATION_ID"

    weather_data = get_weather_data(api_key, station_id)
    print_weather_info(weather_data)

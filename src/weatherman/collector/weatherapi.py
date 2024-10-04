import httpx
import constants


def parse_response_json(response):
    parsed_weather = dict()
    parsed_weather["last_updated"] = response["current"]["last_updated"]
    parsed_weather["location"] = {
        "name": response["location"]["name"],
        "latitude": response["location"]["lat"],
        "longitude": response["location"]["lon"],
    }
    parsed_weather["current"] = {
        "temperature": response["current"]["temp_c"],
        "wind_degree": response["current"]["wind_degree"],
        "wind_kph": response["current"]["wind_kph"],
        "pressure_mb": response["current"]["pressure_mb"],
        "condition": response["current"]["condition"]["text"],
    }
    print(parsed_weather)
    # return parsed_weather


class WeatherApi:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_weather(self, location, data_type):
        url = f"{constants.BASE_URL}/{data_type}.json?key={self.api_key}&q={location}"
        print(f"Trying URL: {url}")
        with httpx.Client() as client:
            response = client.get(url)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise ValueError(f"Failed to get data from weather API: {e}")
        return parse_response_json(response.json())

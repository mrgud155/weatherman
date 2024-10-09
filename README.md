# weatherman
Weatherman is a test application, which collects Weather data from weatherapi.com API and stores it in a database. The application is written in Python and uses SQLite as a database, although it can be easily changed to use any other database.
## Architecture
Weatherman consists of two components:
- Weatherman collector: This component collects weather data from weatherapi.com API on a set schedule, and stores it in a database.
- Weatherman API: This component provides an API to query the weather data stored in the database.

## Running it locally
### Pre-requisites
- Python 3.10 or higher
- API key for accessing weatherapi.com API, which can be obtained by signing up on their website.
- Secret key for signing JWT tokens, which can be generated using the following command:
  ```sh
  openssl rand -hex 32
  ```
- Default admin password for the API, which will be used to create the first `admin` user
- You can optionally create a file which will contain the cities for which you want to fetch weather data. The file should contain one city name per line and one interval in minutes, comma-separated. If you don't provide this file, the collector will fetch weather data for a default set of cities, which can be seen in [constants.py](src/weatherman/collector/constants.py) file. Filename needs to be provided as an environment variable `LOCATION_FILE` when running the collector. Example file:
```text
Moscow,10
Berlin,5
Belgrade,15
Rome,5
```

### Docker
Weatherman is automatically built and deployed to Docker Hub on every push to the main branch. To run Weatherman using Docker, follow these steps.

Run the collector:
```sh
  docker run -d \
  -v "${HOME}/db:/opt/db" \
  -e DATABASE_URL='sqlite:////opt/db/data.db' \
  -e WEATHER_API_KEY=weather-api-key \
  utodorovic/weatherman-collector:latest

```

Run the API:
```sh
  docker run -d \
  -p 5000:5000 \
  -v "${HOME}/db:/opt/db" \
  -e AUTH_DATABASE_URL='sqlite:////opt/db/auth.db' \
  -e DATABASE_URL='sqlite:////opt/db/data.db' \
  -e DEFAULT_ADMIN_PASSWORD=default-admin-password \
  -e API_SECRET_KEY=your_api_secret_key \
  utodorovic/weatherman-api:latest
```

Open your browser and navigate to `http://localhost:5000/docs` to view the API documentation.

You can also use the provided [docker-compose file](src/weatherman/compose/docker-compose.yaml) to run both components together:
```sh
  docker-compose up -d
```

### Command line
To run Weatherman locally, follow these steps:
#### Running the collector
1. Ensure you have Python 3.10 or higher installed on your machine.
2. Obtain an API key from [weatherapi.com](https://weatherapi.com) by signing up on their website.
3. Clone the repository:
   ```sh
   git clone git@github.com:mrgud155/weatherman.git
   cd weatherman
   ```
4. Create a virtual environment and activate it:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
5. Install the required dependencies:
   ```sh
   pip install -r requirements.txt
   ```
6. Set the `WEATHER_API_KEY` environment variable with your API key:
   ```sh
   export WEATHER_API_KEY=your_api_key  # On Windows use `set WEATHER_API_KEY=your_api_key`
   ```
7. Set the `DATABASE_URL` environment variable with the path to the SQLite database file:
   ```sh
   export DATABASE_URL=sqlite:///data.db  # On Windows use `set DATABASE_URL=sqlite:///weatherman.db`
   ```
8. Run the collector to fetch weather data:
   ```sh
   python src/weatherman/collector/main.py
   ```
8. Run the API server:
   ```sh
   python -m uvicorn src.weatherman.api.main:app --port 5000 --host 0.0.0.0
   ```

#### Running the API
1. Ensure you have Python 3.10 or higher installed on your machine.
2. Clone the repository:
   ```sh
   git clone
    cd weatherman
    ```
3. Create a virtual environment and activate it:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```
5. Set the `DATABASE_URL` environment variable with the path to the SQLite database file - same as the one used by the collector:
    ```sh
    export DATABASE_URL=sqlite:///data.db  # On Windows use `set DATABASE_URL=sqlite:///weatherman.db`
    ```
6. Set the `API_SECRET_KEY` environment variable with a secret key for the API that you generated in the previous step:
    ```sh
    export API_SECRET_KEY=your_secret
   ```
7. Set the `DEFAULT_ADMIN_PASSWORD` environment variable with the default admin password for the API:
    ```sh
    export DEFAULT_ADMIN_PASSWORD=default-admin-password  # On Windows use `set DEFAULT_ADMIN_PASSWORD=default-admin-password`
    ```
8. Run the API server:
    ```sh
    python -m uvicorn src.weatherman.api.main:app --port 5000 --host
    ```
9. Open your browser and navigate to `http://localhost:5000/docs` to view the API documentation.

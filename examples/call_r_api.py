import os
import requests


def main():
    host = os.environ.get("R_API_HOST", "localhost")
    port = os.environ.get("R_API_PORT", "8001")
    url = f"http://{host}:{port}/lcoe"

    payload = {
        "data_dir": "/path/datos",
        "input_file": "archivo.csv",
        "capital_cost": 3000,
        "operating_cost": 50,
        "energy_production": 5000,
        "discount_rate": 5,
        "lifetime": 20,
        "projection_date": "2045-12-31"
    }

    response = requests.post(url, json=payload, timeout=60)
    response.raise_for_status()
    print(response.json())


if __name__ == "__main__":
    main()

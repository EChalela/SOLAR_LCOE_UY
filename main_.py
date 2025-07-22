from flask import Flask, request, jsonify, render_template, Blueprint, send_from_directory, current_app
import requests
import matplotlib.pyplot as plt
import os
from app.generar_csv_climatico import generar_csv
from app.calcular_proyeccion_lcoe import calcular_lcoe_r

app = Flask(__name__, template_folder="app/templates")

@app.route("/")
def home():
    """Carga la página principal desde app/templates/index.html"""
    return render_template("index.html")

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"message": "La API de Flask está funcionando correctamente"}), 200

@app.route("/procesar", methods=["POST"])
def procesar():
    """
    Recibe parámetros, genera el CSV climático si no existe y llama a la API de R para calcular el LCOE.
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos en la solicitud"}), 400

    try:
        lat = data["latitude"]
        lon = data["longitude"]
        projection_date = data["projection_date"]

        # Parámetros LCOE
        capital_cost = float(data["capital_cost"])
        operating_cost = float(data["operating_cost"])
        energy_production = float(data["energy_production"])
        discount_rate = float(data["discount_rate"])
        lifetime = int(data["lifetime"])

        # Ruta base de datos
        data_dir = "data"

        # Generar CSV si no existe
        csv_file = f"{data_dir}/clima_{lat}_{lon}.csv"
        generar_csv(lat, lon, projection_date)

        # Llamar a la API de R
        resultado = calcular_lcoe_r(
            data_dir=data_dir,
            input_file=f"clima_{lat}_{lon}.csv",
            capital_cost=capital_cost,
            operating_cost=operating_cost,
            energy_production=energy_production,
            discount_rate=discount_rate,
            lifetime=lifetime,
            projection_date=projection_date
        )

        return jsonify(resultado)

    except KeyError as e:
        return jsonify({"error": f"Falta el parámetro requerido: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route("/calcular_lcoe", methods=["POST"])
def calcular_lcoe():
    ''''
    data = request.get_json()
    print("Datos recibidos para LCOE:", data)  # <-- Agregar este print para depurar

    # Extraer parámetros desde el frontend
    payload = {
        "capital_cost": data.get("capital_cost"),
        "operating_cost": data.get("operating_cost"),
        "energy_production": data.get("energy_production"),
        "discount_rate": data.get("discount_rate"),
        "lifetime": data.get("lifetime")
    }

    print("Enviando datos a la API de R:", payload)  # <-- Verificar datos antes de enviarlos

    url = "http://127.0.0.1:8001/lcoe"
    try:
        response = requests.post(url, json=payload)
        print("Respuesta de R:", response.text)  # <-- Ver qué devuelve la API de R
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print("Error en la conexión con la API de R:", e)  # <-- Ver error exacto
        return jsonify({"error": f"No se pudo conectar con la API de R: {str(e)}"}), 500

        '''
    data = request.json
    lcoe = (data['capital_cost'] + data['operating_cost'] * data['lifetime']) / (
                data['energy_production'] * data['lifetime'])
    # Generar gráfica
    plt.figure()
    plt.plot([1, 2, 3], [lcoe, lcoe * 1.1, lcoe * 0.9])
    plt.title('LCOE Proyección')
    images_dir = os.path.join(current_app.root_path, '..', 'images')
    os.makedirs(images_dir, exist_ok=True)
    image_filename = f'lcoe_{os.urandom(4).hex()}.png'
    image_path = os.path.join(images_dir, image_filename)
    plt.savefig(image_path)
    plt.close()
    return jsonify({'LCOE': round(lcoe, 2), 'image_url': f'/images/{image_filename}'})

# Servir imágenes
@bp.route('/images/<filename>')
def serve_image(filename):
    images_dir = os.path.join(current_app.root_path, '..', 'images')
    return send_from_directory(images_dir, filename)
@app.route("/obtener_datos_climaticos", methods=["POST"])
def obtener_datos_climaticos():
    """
    Recibe la latitud y longitud y obtiene datos climáticos desde OpenMeteo.
    """
    data = request.get_json()

    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "Faltan parámetros de latitud o longitud"}), 400

    lat = data["latitude"]
    lon = data["longitude"]

    try:
        csv_file = generar_csv(lat, lon, "2024-12-31")
        return jsonify({"message": "Datos climáticos obtenidos", "csv_file": csv_file})
    except Exception as e:
        return jsonify({"error": f"Error en la conexión con OpenMeteo: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
from flask import Flask, request, jsonify, render_template, Blueprint, send_from_directory, current_app
import requests
import matplotlib.pyplot as plt
import os
from app.generar_csv_climatico import generar_csv
from app.calcular_proyeccion_lcoe import calcular_lcoe_r

app = Flask(__name__, template_folder="app/templates")

@app.route("/")
def home():
    """Carga la página principal desde app/templates/index.html"""
    return render_template("index.html")

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"message": "La API de Flask está funcionando correctamente"}), 200

@app.route("/procesar", methods=["POST"])
def procesar():
    """
    Recibe parámetros, genera el CSV climático si no existe y llama a la API de R para calcular el LCOE.
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos en la solicitud"}), 400

    try:
        lat = data["latitude"]
        lon = data["longitude"]
        projection_date = data["projection_date"]

        # Parámetros LCOE
        capital_cost = float(data["capital_cost"])
        operating_cost = float(data["operating_cost"])
        energy_production = float(data["energy_production"])
        discount_rate = float(data["discount_rate"])
        lifetime = int(data["lifetime"])

        # Ruta base de datos
        data_dir = "data"

        # Generar CSV si no existe
        csv_file = f"{data_dir}/clima_{lat}_{lon}.csv"
        generar_csv(lat, lon, projection_date)

        # Llamar a la API de R
        resultado = calcular_lcoe_r(
            data_dir=data_dir,
            input_file=f"clima_{lat}_{lon}.csv",
            capital_cost=capital_cost,
            operating_cost=operating_cost,
            energy_production=energy_production,
            discount_rate=discount_rate,
            lifetime=lifetime,
            projection_date=projection_date
        )

        return jsonify(resultado)

    except KeyError as e:
        return jsonify({"error": f"Falta el parámetro requerido: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"Error interno: {str(e)}"}), 500

@app.route("/calcular_lcoe", methods=["POST"])
def calcular_lcoe():
    ''''
    data = request.get_json()
    print("Datos recibidos para LCOE:", data)  # <-- Agregar este print para depurar

    # Extraer parámetros desde el frontend
    payload = {
        "capital_cost": data.get("capital_cost"),
        "operating_cost": data.get("operating_cost"),
        "energy_production": data.get("energy_production"),
        "discount_rate": data.get("discount_rate"),
        "lifetime": data.get("lifetime")
    }

    print("Enviando datos a la API de R:", payload)  # <-- Verificar datos antes de enviarlos

    url = "http://127.0.0.1:8001/lcoe"
    try:
        response = requests.post(url, json=payload)
        print("Respuesta de R:", response.text)  # <-- Ver qué devuelve la API de R
        return jsonify(response.json())
    except requests.exceptions.RequestException as e:
        print("Error en la conexión con la API de R:", e)  # <-- Ver error exacto
        return jsonify({"error": f"No se pudo conectar con la API de R: {str(e)}"}), 500

        '''
    data = request.json
    lcoe = (data['capital_cost'] + data['operating_cost'] * data['lifetime']) / (
                data['energy_production'] * data['lifetime'])
    # Generar gráfica
    plt.figure()
    plt.plot([1, 2, 3], [lcoe, lcoe * 1.1, lcoe * 0.9])
    plt.title('LCOE Proyección')
    images_dir = os.path.join(current_app.root_path, '..', 'images')
    os.makedirs(images_dir, exist_ok=True)
    image_filename = f'lcoe_{os.urandom(4).hex()}.png'
    image_path = os.path.join(images_dir, image_filename)
    plt.savefig(image_path)
    plt.close()
    return jsonify({'LCOE': round(lcoe, 2), 'image_url': f'/images/{image_filename}'})

# Servir imágenes
@bp.route('/images/<filename>')
def serve_image(filename):
    images_dir = os.path.join(current_app.root_path, '..', 'images')
    return send_from_directory(images_dir, filename)
@app.route("/obtener_datos_climaticos", methods=["POST"])
def obtener_datos_climaticos():
    """
    Recibe la latitud y longitud y obtiene datos climáticos desde OpenMeteo.
    """
    data = request.get_json()

    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "Faltan parámetros de latitud o longitud"}), 400

    lat = data["latitude"]
    lon = data["longitude"]

    try:
        csv_file = generar_csv(lat, lon, "2024-12-31")
        return jsonify({"message": "Datos climáticos obtenidos", "csv_file": csv_file})
    except Exception as e:
        return jsonify({"error": f"Error en la conexión con OpenMeteo: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)

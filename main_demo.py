from flask import Flask, request, jsonify, render_template, send_from_directory, current_app
import requests
from flasgger import Swagger
import matplotlib.pyplot as plt
import os
from app.generar_csv_climatico import generar_csv
from app.calcular_proyeccion_lcoe import calcular_lcoe_r

app = Flask(__name__, template_folder="app/templates")
swagger = Swagger(app)

@app.route("/")
def home():
    """
    Página principal.
    ---
    get:
      summary: Carga la página principal.
      description: Renderiza el archivo index.html desde la carpeta de templates.
      responses:
        200:
          description: Página HTML cargada correctamente.
    """

    return render_template("index2_demo.html")

@app.route("/status", methods=["GET"])
def status():
    """
    Estado de la API.
    ---
    get:
      summary: Verifica el estado de la API.
      description: Devuelve un mensaje indicando que la API está funcionando correctamente.
      responses:
        200:
          description: Respuesta exitosa con mensaje de estado.
          schema:
            type: object
            properties:
              message:
                type: string
    """
    return jsonify({"message": "La API de Flask está funcionando correctamente"}), 200

@app.route("/procesar", methods=["POST"])
def procesar():
    """
    Procesa parámetros y calcula el LCOE usando datos climáticos.
    ---
    post:
      summary: Procesa los datos recibidos y calcula el LCOE.
      description: Recibe parámetros, genera el CSV climático si no existe y llama a la API de R para calcular el LCOE.
      parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              latitude:
                type: number
              longitude:
                type: number
              projection_date:
                type: string
              capital_cost:
                type: number
              operating_cost:
                type: number
              energy_production:
                type: number
              discount_rate:
                type: number
              lifetime:
                type: integer
      responses:
        200:
          description: Resultado del cálculo LCOE.
          schema:
            type: object
        400:
          description: Error por parámetros faltantes.
        500:
          description: Error interno.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se enviaron datos en la solicitud"}), 400

    try:
        lat = data["latitude"]
        lon = data["longitude"]
        projection_date = data["projection_date"]

        capital_cost = float(data["capital_cost"])
        operating_cost = float(data["operating_cost"])
        energy_production = float(data["energy_production"])
        discount_rate = float(data["discount_rate"])
        lifetime = int(data["lifetime"])

        data_dir = "data"
        csv_file = f"{data_dir}/clima_{lat}_{lon}.csv"
        generar_csv(lat, lon, projection_date)

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
    """
    Calcula el LCOE y genera una gráfica.
    ---
    post:
      summary: Calcula el LCOE y genera una imagen de la proyección.
      description: Calcula el LCOE promedio y guarda una gráfica en la carpeta images, devolviendo la URL de la imagen.
      parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              capital_cost:
                type: number
              operating_cost:
                type: number
              energy_production:
                type: number
              lifetime:
                type: integer
              image_name:
                type: string
      responses:
        200:
          description: LCOE calculado y URL de la imagen generada.
          schema:
            type: object
            properties:
              LCOE:
                type: number
              image_url:
                type: string
    """
    return jsonify({'image_url': '/images/lcoe_energia.png'})

@app.route("/images/<filename>")
def serve_image(filename):
    """
    Sirve imágenes generadas.
    ---
    get:
      summary: Devuelve una imagen generada.
      description: Sirve imágenes desde la carpeta images.
      parameters:
        - in: path
          name: filename
          required: true
          type: string
      responses:
        200:
          description: Imagen servida correctamente.
    """
    images_dir = os.path.join(current_app.root_path, 'images')
    return send_from_directory(images_dir, filename)

@app.route("/obtener_datos_climaticos", methods=["POST"])
def obtener_datos_climaticos():
    """
    Obtiene datos climáticos desde OpenMeteo.
    ---
    post:
      summary: Obtiene datos climáticos por latitud y longitud.
      description: Recibe latitud y longitud y obtiene datos climáticos desde OpenMeteo, generando un archivo CSV.
      parameters:
        - in: body
          name: body
          required: true
          schema:
            type: object
            properties:
              latitude:
                type: number
              longitude:
                type: number
      responses:
        200:
          description: Datos climáticos obtenidos y archivo CSV generado.
          schema:
            type: object
            properties:
              message:
                type: string
              csv_file:
                type: string
        400:
          description: Parámetros faltantes.
        500:
          description: Error en la conexión con OpenMeteo.
    """
    data = request.get_json()

    if not data or "latitude" not in data or "longitude" not in data:
        return jsonify({"error": "Faltan parámetros de latitud o longitud"}), 400

    lat = data["latitude"]
    lon = data["longitude"]

    try:
        csv_file = generar_csv(lat, lon, "2044-12-31")
        return jsonify({"message": "Datos climáticos obtenidos", "csv_file": csv_file})
    except Exception as e:
        return jsonify({"error": f"Error en la conexión con OpenMeteo: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)
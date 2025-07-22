#
# from flask import Blueprint, render_template, jsonify
# from .utils import validate_coordinates, calculate_lcoe
# import folium
#
# bp = Blueprint('main', __name__)
#
# @bp.route('/')
# def index():
#     m = folium.Map(location=[-33, -56], zoom_start=7)
#     folium.TileLayer(
#         tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
#         attr="© OpenStreetMap contributors",
#         name="OpenStreetMap",
#         max_zoom=19
#     ).add_to(m)
#     return render_template('index.html', map_html=m._repr_html_())
#
# @bp.route('/validate/<float:lat>/<float:lon>')
# def validate(lat, lon):
#     is_valid, message = validate_coordinates(lat, lon)
#     return jsonify({'valid': is_valid, 'message': message})
#
# @bp.route('/lcoe')
# def lcoe():
#     capital_cost = 2000
#     operating_cost = 50
#     energy_production = 4000
#     discount_rate = 0.05
#     lifetime = 20
#     lcoe_value = calculate_lcoe(capital_cost, operating_cost, energy_production, discount_rate, lifetime)
#     return jsonify({'LCOE': round(lcoe_value, 2)})

###################################

from flask import Blueprint, render_template, jsonify, request
from .utils import validate_coordinates, calculate_lcoe
from .generar_csv_climatico import generar_csv
import folium

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    m = folium.Map(location=[-33, -56], zoom_start=7)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="© OpenStreetMap contributors",
        name="OpenStreetMap",
        max_zoom=19
    ).add_to(m)
    return render_template('index.html', map_html=m._repr_html_())


@bp.route('/validate/<float:lat>/<float:lon>')
def validate(lat, lon):
    is_valid, message = validate_coordinates(lat, lon)
    return jsonify({'valid': is_valid, 'message': message})


@bp.route('/lcoe')
def lcoe():
    #capital_cost = 2000
    #operating_cost = 50
    #energy_production = 4000
    #discount_rate = 0.05
    #lifetime = 20
    lcoe_value = calculate_lcoe(capital_cost, operating_cost, energy_production, discount_rate, lifetime)
    return jsonify({'LCOE': round(lcoe_value, 2)})


@bp.route('/generate_csv', methods=['GET'])
def generate_csv():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    end_date = request.args.get('end_date', type=str)

    if lat is None or lon is None or end_date is None:
        return jsonify({"error": "Parámetros faltantes. Debe incluir lat, lon y end_date."}), 400

    filename = generar_csv(lat, lon, end_date)

    if filename:
        return jsonify({"message": "Archivo CSV generado correctamente.", "file": filename})
    else:
        return jsonify({"error": "Error al generar el archivo CSV."}), 500
from flask import Blueprint, render_template, jsonify, request
from .utils import validate_coordinates, calculate_lcoe
from .generar_csv_climatico import generar_csv
import folium

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    m = folium.Map(location=[-33, -56], zoom_start=7)
    folium.TileLayer(
        tiles="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
        attr="© OpenStreetMap contributors",
        name="OpenStreetMap",
        max_zoom=19
    ).add_to(m)
    return render_template('index.html', map_html=m._repr_html_())


@bp.route('/validate/<float:lat>/<float:lon>')
def validate(lat, lon):
    is_valid, message = validate_coordinates(lat, lon)
    return jsonify({'valid': is_valid, 'message': message})


@bp.route('/lcoe')
def lcoe():
    capital_cost = 2000
    operating_cost = 50
    energy_production = 4000
    discount_rate = 0.05
    lifetime = 20
    lcoe_value = calculate_lcoe(capital_cost, operating_cost, energy_production, discount_rate, lifetime)
    return jsonify({'LCOE': round(lcoe_value, 2)})


@bp.route('/generate_csv', methods=['GET'])
def generate_csv():
    lat = request.args.get('lat', type=float)
    lon = request.args.get('lon', type=float)
    end_date = request.args.get('end_date', type=str)

    if lat is None or lon is None or end_date is None:
        return jsonify({"error": "Parámetros faltantes. Debe incluir lat, lon y end_date."}), 400

    filename = generar_csv(lat, lon, end_date)

    if filename:
        return jsonify({"message": "Archivo CSV generado correctamente.", "file": filename})
    else:
        return jsonify({"error": "Error al generar el archivo CSV."}), 500

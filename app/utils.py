
from shapely.geometry import Point, Polygon

URUGUAY_POLYGON = Polygon([
    (-58.5, -30.1), (-53.2, -30.1), (-53.2, -34.9), (-58.5, -34.9), (-58.5, -30.1)
])

RIVERS = [
    Polygon([(-57, -33), (-56.5, -33), (-56.5, -33.5), (-57, -33.5)]),
    Polygon([(-54, -31), (-53.5, -31), (-53.5, -31.5), (-54, -31.5)])
]

def validate_coordinates(lat, lon):
    point = Point(lon, lat)
    if not URUGUAY_POLYGON.contains(point):
        return False, "Las coordenadas no están dentro de Uruguay."
    for river in RIVERS:
        if river.contains(point):
            return False, "Las coordenadas están sobre un río."
    return True, "Ubicación válida."

def calculate_lcoe(capital_cost, operating_cost, energy_production, discount_rate, lifetime):
    annual_cost = capital_cost * discount_rate / (1 - (1 + discount_rate) ** -lifetime)
    annual_cost += operating_cost
    return annual_cost / energy_production

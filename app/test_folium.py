import folium

# Crear un mapa básico
m = folium.Map(location=[-34.9, -56.2], zoom_start=7)

# Guardar el mapa como un archivo HTML
m.save("test_map.html")

print("Mapa guardado en 'test_map.html'. Ábrelo en tu navegador para verificar.")
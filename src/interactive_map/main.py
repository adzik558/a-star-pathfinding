import sys
import json
import tracemalloc
import time
import os
import random

IS_WIN = sys.platform == "win32"
if IS_WIN:
    import ctypes
    from ctypes import wintypes

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel,
    QMessageBox, QHBoxLayout, QGroupBox, QStyle, QLineEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QComboBox, QFileDialog
)
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import QUrl, QSize, Qt, QObject, pyqtSlot
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtGui import QFont, QIcon
import routing
import folium
import osmnx as ox
from geopy.geocoders import Nominatim
import networkx as nx
import pandas as pd
import pyqtgraph as pg

pg.setConfigOption('background', '#3C3C3C')
pg.setConfigOption('foreground', '#F0F0F0')

class WebBridge(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent

    @pyqtSlot(float, float, int)
    def receive_coords_from_js(self, lat, lon, click_count):
        formatted_coords = f"{lat:.6f}, {lon:.6f}"
        if click_count == 1:
            self.main_window.start_address_input.setText(formatted_coords)
            self.main_window.end_address_input.clear()
        elif click_count == 2:
            self.main_window.end_address_input.setText(formatted_coords)

MODERN_STYLESHEET = """
QWidget { background-color: #2E2E2E; color: #F0F0F0; font-family: 'Segoe UI'; font-size: 14px; }
QGroupBox { background-color: #3C3C3C; border: 1px solid #555; border-radius: 8px; margin-top: 1ex; font-weight: bold; }
QGroupBox::title { subcontrol-origin: margin; subcontrol-position: top center; padding: 0 10px; }
QPushButton { background-color: #555; border: 1px solid #666; padding: 8px; border-radius: 6px; }
QPushButton:hover { background-color: #6A6A6A; }
QPushButton:pressed { background-color: #4A4A4A; }
QComboBox { background-color: #4A4A4A; border: 1px solid #666; padding: 6px; border-radius: 4px; }
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background-color: #4A4A4A; border: 1px solid #666; selection-background-color: #6A6A6A; }
QLineEdit { background-color: #4A4A4A; border: 1px solid #666; padding: 6px; border-radius: 4px; }
QTableWidget { background-color: #3C3C3C; gridline-color: #555; color: #F0F0F0; }
QHeaderView::section { background-color: #4A4A4A; padding: 4px; border: 1px solid #555; font-weight: bold; color: #F0F0F0;}
QTableWidgetItem { padding: 5px; }
#CoordsLabel { font-style: italic; color: #AAAAAA; }
"""

class BarChartWidget(pg.PlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setLabel('bottom', 'Czas (s)'); self.getAxis('left').setWidth(80)
        self.showAxis('top', False); self.showAxis('right', False)

    def update_chart(self, results):
        self.clear()
        if not results: return
        results.sort(key=lambda x: x['name'])
        names = [res['name'].replace(" (Euklidesowa)", " (E)").replace(" (Manhattan)", " (M)") for res in results]
        y_ticks = list(range(len(names)))
        init_times = [res.get('time_components', {}).get('init_time', 0) for res in results]
        loop_times = [res.get('time_components', {}).get('loop_time', 0) for res in results]
        recon_times = [res.get('time_components', {}).get('reconstruction_time', 0) for res in results]
        bar1 = pg.BarGraphItem(y=y_ticks, x0=0, width=init_times, height=0.5, brush='#3498DB'); self.addItem(bar1)
        bar2 = pg.BarGraphItem(y=y_ticks, x0=init_times, width=loop_times, height=0.5, brush='#E74C3C'); self.addItem(bar2)
        start_recon = [i + l for i, l in zip(init_times, loop_times)]
        bar3 = pg.BarGraphItem(y=y_ticks, x0=start_recon, width=recon_times, height=0.5, brush='#F1C40F'); self.addItem(bar3)
        self.getAxis('left').setTicks([list(zip(y_ticks, names))])

class RoutePlanner(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Route Planner Rzeszów - Porównanie Algorytmów")
        self.setGeometry(100, 100, 1600, 900)
        
        icon_path = "app_icon.svg";
        if os.path.exists(icon_path): self.setWindowIcon(QIcon(icon_path))
        if IS_WIN: self.set_dark_title_bar()
        
        self.G = self.load_graph()
        self.geolocator = Nominatim(user_agent="rzeszow_planner_gui")
        self.algorithms = [{"name": "Dijkstra", "h": None, "c": "red", "dash": "10, 5"}, {"name": "A* (Euklidesowa)", "h": "euklidesowa", "c": "green", "dash": None}, {"name": "A* (Manhattan)", "h": "manhattan", "c": "purple", "dash": "1, 5"}, {"name": "BFS", "h": None, "c": "blue", "dash": "20, 10, 5, 10"}]
        self.latest_results = []

        self.bridge = WebBridge(self)
        self.channel = QWebChannel(); self.channel.registerObject("backend", self.bridge)
        self.map_view = QWebEngineView(); self.map_view.page().setWebChannel(self.channel)

        main_layout = QHBoxLayout(); main_layout.setContentsMargins(15, 15, 15, 15); main_layout.setSpacing(15)
        left_panel_layout = QVBoxLayout(); left_panel_layout.setSpacing(15)

        address_group = QGroupBox("Wprowadź Adresy"); address_layout = QVBoxLayout(); address_layout.setContentsMargins(10, 20, 10, 10)
        self.start_address_input = QLineEdit(""); self.start_address_input.setPlaceholderText("np. al. Powstańców Warszawy 12")
        self.end_address_input = QLineEdit(""); self.end_address_input.setPlaceholderText("np. Port Lotniczy Rzeszów-Jasionka")
        address_layout.addWidget(QLabel("Punkt startowy:")); address_layout.addWidget(self.start_address_input); address_layout.addWidget(QLabel("Punkt końcowy:")); address_layout.addWidget(self.end_address_input)
        address_group.setLayout(address_layout); left_panel_layout.addWidget(address_group)
        
        click_group = QGroupBox("Wybierz Punkty na Mapie"); click_layout = QVBoxLayout(); click_layout.setContentsMargins(10, 20, 10, 10)
        self.status_label = QLabel("Wybór zresetowany. Kliknij na mapie."); self.status_label.setObjectName("CoordsLabel")
        clear_button = QPushButton("Wyczyść punkty i odśwież mapę"); clear_button.clicked.connect(self.clear_points)
        click_layout.addWidget(self.status_label); click_layout.addWidget(clear_button); click_group.setLayout(click_layout); left_panel_layout.addWidget(click_group)

        single_route_group = QGroupBox("Wyznacz Trasę"); single_route_layout = QHBoxLayout(); single_route_layout.setContentsMargins(10, 20, 10, 10)
        self.algo_selection_box = QComboBox()
        for algo in self.algorithms: self.algo_selection_box.addItem(algo["name"])
        find_route_button = QPushButton("Wyznacz"); find_route_button.clicked.connect(self.find_single_route)
        single_route_layout.addWidget(self.algo_selection_box); single_route_layout.addWidget(find_route_button)
        single_route_group.setLayout(single_route_layout); left_panel_layout.addWidget(single_route_group)

        compare_button = QPushButton("Porównaj Wszystkie Algorytmy"); compare_button.clicked.connect(self.run_comparison)
        left_panel_layout.addWidget(compare_button)

        results_group = QGroupBox("Wyniki"); results_layout = QVBoxLayout(); results_layout.setContentsMargins(10, 20, 10, 10)
        self.results_table = QTableWidget(); self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(["Algorytm", "Długość (km)", "Czas (s)", "Pamięć (MB)", "Odw. węzły"])
        self.results_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        results_layout.addWidget(self.results_table)
        export_button = QPushButton("Eksportuj do Excela"); export_button.clicked.connect(self.export_results_to_excel)
        results_layout.addWidget(export_button)
        results_group.setLayout(results_layout); left_panel_layout.addWidget(results_group, 1)

        chart_group = QGroupBox("Analiza Czasu Obliczeń"); chart_layout = QVBoxLayout(); chart_layout.setContentsMargins(10, 15, 10, 10)
        self.bar_chart_widget = BarChartWidget()
        chart_layout.addWidget(self.bar_chart_widget)
        chart_group.setLayout(chart_layout); left_panel_layout.addWidget(chart_group, 1)

        right_panel_layout = QVBoxLayout(); right_panel_layout.addWidget(self.map_view)
        main_layout.addLayout(left_panel_layout, 1); main_layout.addLayout(right_panel_layout, 2); self.setLayout(main_layout)
        self.load_clickable_map()
    
    def export_results_to_excel(self):
        if not self.latest_results: self.show_error("Brak danych", "Najpierw wyznacz trasy."); return
        filePath, _ = QFileDialog.getSaveFileName(self, "Zapisz jako...", "", "Pliki Excel (*.xlsx);;Wszystkie pliki (*)")
        if filePath:
            try:
                export_data = [{'Algorytm': r.get('name', ''), 'Długość (km)': f"{r.get('len', 0):.2f}", 'Czas (s)': f"{r.get('time', 0):.4f}", 'Pamięć (MB)': f"{r.get('mem', 0):.4f}", 'Odwiedzone węzły': r.get('visited', 0)} for r in self.latest_results]
                df = pd.DataFrame(export_data); df.to_excel(filePath, index=False)
                QMessageBox.information(self, "Sukces", f"Wyniki pomyślnie wyeksportowano do:\n{filePath}")
            except Exception as e: self.show_error("Błąd eksportu", f"Nie udało się zapisać pliku. Błąd: {e}")

    def process_routes(self, algorithms_to_process, start_c, end_c):
        self.results_table.setRowCount(0); self.bar_chart_widget.clear(); QApplication.processEvents()
        try:
            start_node = ox.distance.nearest_nodes(self.G, X=start_c[1], Y=start_c[0])
            end_node = ox.distance.nearest_nodes(self.G, X=end_c[1], Y=end_c[0])
            results_data, map_data = [], []
            for algo in algorithms_to_process:
                tracemalloc.start(); start_time = time.perf_counter()
                name_for_func = "A*" if "A*" in algo["name"] else algo["name"]
                path, visited_count, time_components = routing.find_path(self.G, start_node, end_node, name_for_func, algo["h"])
                end_time = time.perf_counter(); _, peak = tracemalloc.get_traced_memory(); tracemalloc.stop()
                if path:
                    length = nx.path_weight(self.G, path, weight="length") / 1000
                    results_data.append({ "name": algo["name"], "len": length, "time": end_time - start_time, "mem": peak / (1024**2), "visited": visited_count, "time_components": time_components })
                    map_data.append({"path": path, "c": algo["c"], "name": algo["name"], "len": length, "dash": algo.get("dash")})
            if not results_data: self.show_error("Błąd", "Nie udało się znaleźć trasy."); return
            self.latest_results = results_data
            self.update_results_table(results_data)
            self.bar_chart_widget.update_chart(results_data)
            self.generate_comparison_map(start_c, end_c, map_data)
        except nx.NetworkXNoPath: self.show_error("Błąd trasy", "Nie można znaleźć połączenia.")
        except Exception as e: self.show_error("Błąd przetwarzania", f"Wystąpił błąd: {e}")
        
    def update_results_table(self, results):
        self.results_table.setRowCount(len(results)); results.sort(key=lambda x: x['len'])
        for row, res in enumerate(results):
            self.results_table.setItem(row, 0, QTableWidgetItem(res["name"]))
            self.results_table.setItem(row, 1, QTableWidgetItem(f"{res['len']:.2f}"))
            self.results_table.setItem(row, 2, QTableWidgetItem(f"{res['time']:.4f}"))
            self.results_table.setItem(row, 3, QTableWidgetItem(f"{res['mem']:.4f}"))
            self.results_table.setItem(row, 4, QTableWidgetItem(f"{res['visited']}"))
            
    def generate_comparison_map(self, start_coords, end_coords, map_data):
        m = folium.Map(location=start_coords, zoom_start=12)
        blue_icon, red_icon = folium.Icon(color='blue', icon='play'), folium.Icon(color='red', icon='stop')
        folium.Marker(start_coords, popup="Start", icon=blue_icon).add_to(m)
        folium.Marker(end_coords, popup="Koniec", icon=red_icon).add_to(m)
        for data in map_data:
            route_coords = [(self.G.nodes[n]['y'], self.G.nodes[n]['x']) for n in data['path']]
            folium.PolyLine(locations=route_coords, color=data['c'], weight=4, opacity=0.8, tooltip=f"{data['name']}: {data['len']:.2f} km", dash_array=data.get('dash')).add_to(m)
        if len(map_data) > 1:
            legend_html = self.generate_legend_html(map_data)
            html_map = m.get_root().render()
            final_html = html_map.replace("</body>", legend_html + "</body>")
            self.map_view.setHtml(final_html)
        else:
            self.map_view.setHtml(m.get_root().render())
        if map_data: m.fit_bounds(m.get_bounds(), padding=(10, 10))
        
    def generate_legend_html(self, map_data):
        legend_items = ""
        for data in sorted(map_data, key=lambda x: x['name']):
            color = data['c']
            dash_style = f"border-top: 3px dashed {color};" if data.get('dash') else f"background: {color};"
            legend_items += f'<div style="margin-bottom: 4px; display: flex; align-items: center;"><span style="display: inline-block; width: 30px; height: 5px; {dash_style}"></span><span style="margin-left: 5px;">{data["name"]}</span></div>'
        
        return f"""
         <div style="position: fixed; top: 10px; right: 10px; width: auto; height: auto; 
                     background-color: rgba(46, 46, 46, 0.85);
                     border:1px solid #555; z-index:9999; font-size:14px;
                     padding: 10px; border-radius: 8px; color: #F0F0F0; font-family: 'Segoe UI';">
         <h4 style="margin-top:0; margin-bottom: 8px; font-weight: bold; text-align: center;">Legenda</h4>
         {legend_items}
         </div>"""
        
    def set_dark_title_bar(self):
        try:
            hwnd = wintypes.HWND(int(self.winId())); value = wintypes.DWORD(1)
            ctypes.windll.dwmapi.DwmSetWindowAttribute(hwnd, 20, ctypes.byref(value), ctypes.sizeof(value))
        except Exception as e: print(f"Nie można ustawić ciemnego paska tytułu: {e}")
        
    def clear_points(self):
        coords_file = os.path.join("data", "coords.json");
        if os.path.exists(coords_file): os.remove(coords_file)
        self.start_address_input.clear(); self.end_address_input.clear()
        self.status_label.setText("Wybór zresetowany. Kliknij na mapie, aby wybrać start.")
        self.load_clickable_map()
        
    def load_graph(self):
        graph_file = "data/rzeszow.graphml"
        if not os.path.exists(graph_file):
            print("Pobieranie mapy Rzeszowa...")
            center_point = (50.0375, 22.0044)
            G = ox.graph_from_point(center_point, dist=15000, network_type="drive")
            G = nx.Graph(G)  # konwersja do nieskierowanego grafu
            ox.save_graphml(G, graph_file)
            return G
        G = ox.load_graphml(graph_file)
        return nx.Graph(G)
        
    def load_clickable_map(self):
        m = folium.Map(location=[50.0412, 21.9991], zoom_start=12)
        qwebchannel_js = "<script src='qrc:///qtwebchannel/qwebchannel.js'></script>"
        js_script = f"""<script>
            window.onload = function() {{
                new QWebChannel(qt.webChannelTransport, function(channel) {{ window.backend = channel.objects.backend; }});
                var map_object = {m.get_name()};
                var blueIcon = new L.Icon({{iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png', shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]}});
                var redIcon = new L.Icon({{iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png', shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png', iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41]}});
                var markers = []; var coords = [];  
                map_object.on('click', function(e) {{
                    if (markers.length >= 2) {{ markers.forEach(function(m) {{ map_object.removeLayer(m); }}); markers = []; coords = []; }}
                    if (window.backend) {{ window.backend.receive_coords_from_js(e.latlng.lat, e.latlng.lng, markers.length + 1); }}
                    let icon = (markers.length === 0) ? blueIcon : redIcon;
                    var newMarker = L.marker([e.latlng.lat, e.latlng.lng], {{icon: icon}}).addTo(map_object);
                    markers.push(newMarker); coords.push([e.latlng.lat, e.latlng.lng]);
                    if (coords.length === 2) {{ fetch('http://localhost:8000/save_coords', {{ method: 'POST', headers: {{'Content-Type': 'application/json'}}, body: JSON.stringify(coords) }}) }}
                }});
            }};
            </script>"""
        html_map = m.get_root().render()
        final_html = html_map.replace('</body>', qwebchannel_js + js_script + '</body>')
        self.map_view.setHtml(final_html)
        
    def _get_start_end_points(self):
        start_c, end_c = None, None; coords_file = os.path.join("data", "coords.json")
        if os.path.exists(coords_file):
            try:
                with open(coords_file, 'r') as f: coords_list = json.load(f)
                if len(coords_list) == 2: start_c, end_c = coords_list[0], coords_list[1]
            except (json.JSONDecodeError, IndexError): pass
        if not (start_c and end_c):
            start_addr, end_addr = self.start_address_input.text(), self.end_address_input.text()
            try:
                if ',' in start_addr and ',' in end_addr:
                    lat_s, lon_s = map(float, start_addr.split(',')); lat_e, lon_e = map(float, end_addr.split(','))
                    return (lat_s, lon_s), (lat_e, lon_e)
            except (ValueError, TypeError): pass 
            if not start_addr or not end_addr: self.show_error("Brak danych", "Wprowadź adresy lub wybierz dwa punkty."); return None, None
            try:
                start_loc, end_loc = self.geolocator.geocode(start_addr + ", Rzeszów"), self.geolocator.geocode(end_addr + ", Rzeszów")
                if not start_loc or not end_loc: self.show_error("Błąd geokodowania", "Nie można znaleźć adresu."); return None, None
                start_c, end_c = (start_loc.latitude, start_loc.longitude), (end_loc.latitude, end_loc.longitude)
            except Exception as e: self.show_error("Błąd geokodowania", f"Błąd: {e}"); return None, None
        return start_c, end_c
        
    def find_single_route(self):
        start_c, end_c = self._get_start_end_points();
        if not start_c: return
        selected_algo_name = self.algo_selection_box.currentText()
        algo_to_run = next((item for item in self.algorithms if item["name"] == selected_algo_name), None)
        if not algo_to_run: self.show_error("Błąd", "Nie znaleziono wybranego algorytmu."); return
        self.process_routes([algo_to_run], start_c, end_c)
        
    def run_comparison(self):
        start_c, end_c = self._get_start_end_points();
        if not start_c: return
        self.process_routes(self.algorithms, start_c, end_c)
        
    def show_error(self, title, text):
        msg_box = QMessageBox(self); msg_box.setIcon(QMessageBox.Critical); msg_box.setText(title)
        msg_box.setInformativeText(text); msg_box.setWindowTitle("Błąd"); msg_box.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    QWebEngineProfile.defaultProfile().clearHttpCache()
    app.setStyleSheet(MODERN_STYLESHEET)
    window = RoutePlanner()
    window.show()
    sys.exit(app.exec_())
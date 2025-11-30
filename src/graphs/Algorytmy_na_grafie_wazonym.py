import networkx as nx
import matplotlib.pyplot as plt
import time
import tracemalloc
import random
import math
from queue import PriorityQueue, Queue


def generuj_graf(n=30, gestosc=0.1):
    G = nx.erdos_renyi_graph(n=n, p=gestosc)
    while not nx.is_connected(G):
        G = nx.erdos_renyi_graph(n=n, p=gestosc)
    for (u, v) in G.edges():
        G[u][v]['weight'] = random.randint(1, 4)
    return G

def bfs(graf, start, cel):
    kolejka = Queue()
    kolejka.put(start)
    odwiedzone = {start}
    sciezka = {}

    while not kolejka.empty():
        obecny = kolejka.get()
        if obecny == cel:
            droga = odwiedzony_na_sciezke(sciezka, start, cel)
            koszt = sum(graf[droga[i]][droga[i+1]]['weight'] for i in range(len(droga) - 1))
            return droga, odwiedzone, koszt
        for sasiad in graf.neighbors(obecny):
            if sasiad not in odwiedzone:
                odwiedzone.add(sasiad)
                kolejka.put(sasiad)
                sciezka[sasiad] = obecny
    return [], odwiedzone, 0

def dfs(graf, start, cel):
    stos = [start]
    odwiedzone = {start}
    sciezka = {}

    while stos:
        obecny = stos.pop()
        if obecny == cel:
            droga = odwiedzony_na_sciezke(sciezka, start, cel)
            koszt = sum(graf[droga[i]][droga[i+1]]['weight'] for i in range(len(droga) - 1))
            return droga, odwiedzone, koszt
        for sasiad in graf.neighbors(obecny):
            if sasiad not in odwiedzone:
                odwiedzone.add(sasiad)
                stos.append(sasiad)
                sciezka[sasiad] = obecny
    return [], odwiedzone, 0

def dijkstra(graf, start, cel):
    kolejka = PriorityQueue()
    kolejka.put((0, start))
    koszt = {start: 0}
    odwiedzone = {start}
    sciezka = {}

    while not kolejka.empty():
        dystans, obecny = kolejka.get()
        if obecny == cel:
            droga = odwiedzony_na_sciezke(sciezka, start, cel)
            return droga, odwiedzone, koszt[cel]
        for sasiad in graf.neighbors(obecny):
            waga = graf[obecny][sasiad]['weight']
            nowy_koszt = dystans + waga
            if sasiad not in koszt or nowy_koszt < koszt[sasiad]:
                koszt[sasiad] = nowy_koszt
                kolejka.put((nowy_koszt, sasiad))
                sciezka[sasiad] = obecny
                odwiedzone.add(sasiad)
    return [], odwiedzone, 0

def heurystyka_indeksowa(a, b):
    return abs(a - b)

def heurystyka_euklidesowa(pos):
    def h(a, b):
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    return h

def heurystyka_manhattan(pos):
    def h(a, b):
        x1, y1 = pos[a]
        x2, y2 = pos[b]
        return abs(x1 - x2) + abs(y1 - y2)
    return h

def astar(graf, start, cel, heurystyka):
    kolejka = PriorityQueue()
    kolejka.put((0, start))
    koszt = {start: 0}
    odwiedzone = {start}
    sciezka = {}

    while not kolejka.empty():
        _, obecny = kolejka.get()
        if obecny == cel:
            droga = odwiedzony_na_sciezke(sciezka, start, cel)
            return droga, odwiedzone, koszt[cel]
        for sasiad in graf.neighbors(obecny):
            waga = graf[obecny][sasiad]['weight']
            nowy_koszt = koszt[obecny] + waga
            if sasiad not in koszt or nowy_koszt < koszt[sasiad]:
                koszt[sasiad] = nowy_koszt
                priorytet = nowy_koszt + heurystyka(sasiad, cel)
                kolejka.put((priorytet, sasiad))
                sciezka[sasiad] = obecny
                odwiedzone.add(sasiad)
    return [], odwiedzone, 0

def odwiedzony_na_sciezke(skamd, start, cel):
    sciezka = []
    obecny = cel
    while obecny != start:
        sciezka.append(obecny)
        obecny = skamd.get(obecny)
        if obecny is None:
            return []
    sciezka.append(start)
    sciezka.reverse()
    return sciezka

def zmierz_i_rysuj(graf, algorytm, nazwa, pos, start, cel, subplot_index):
    tracemalloc.start()
    start_czas = time.perf_counter()
    sciezka, odwiedzone, koszt = algorytm(graf, start, cel)
    koniec_czas = time.perf_counter()
    pamiec, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    plt.subplot(2, 3, subplot_index)
    nx.draw(graf, pos, node_color='lightgrey', edge_color='black', with_labels=True, node_size=500, font_size=8)

    if sciezka:
        krawedzie = list(zip(sciezka[:-1], sciezka[1:]))
        nx.draw_networkx_edges(graf, pos, edgelist=krawedzie, edge_color='green', width=2.5)
        nx.draw_networkx_nodes(graf, pos, nodelist=sciezka, node_color='limegreen', node_size=500)
        etykiety_krawedzi = nx.get_edge_attributes(graf, 'weight')
        nx.draw_networkx_edge_labels(graf, pos, edge_labels=etykiety_krawedzi, font_size=6)

    plt.title(
        f"{nazwa}\nCzas: {koniec_czas - start_czas:.4f}s | Pamięć: {pamiec / 1024:.1f}KB | "
        f"Wierzchołki: {len(odwiedzone)} | Koszt: {koszt}"
    )

def main():
    graf = generuj_graf(50, 0.07)
    pos = nx.spring_layout(graf, seed=15, k=0.7)
    start, cel = 1, 40

    plt.figure(figsize=(18, 8))
    zmierz_i_rysuj(graf, bfs, "BFS", pos, start, cel, 1)
    zmierz_i_rysuj(graf, dfs, "DFS", pos, start, cel, 2)
    zmierz_i_rysuj(graf, dijkstra, "Dijkstra", pos, start, cel, 3)
    zmierz_i_rysuj(graf, lambda g, s, c: astar(g, s, c, heurystyka_indeksowa), "A* (indeksowa)", pos, start, cel, 4)
    zmierz_i_rysuj(graf, lambda g, s, c: astar(g, s, c, heurystyka_euklidesowa(pos)), "A* (euklidesowa)", pos, start, cel, 5)
    zmierz_i_rysuj(graf, lambda g, s, c: astar(g, s, c, heurystyka_manhattan(pos)), "A* (manhattan)", pos, start, cel, 6)
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    main()
import pygame
from queue import PriorityQueue, Queue
import time
import tracemalloc
import sys
sys.setrecursionlimit(3000)

pygame.init()          
pygame.font.init()    


#kolory
CZERWONY = (255, 0, 0)
ZIELONY = (0, 255, 0)
BIALY = (255, 255, 255)
CZARNY = (0, 0, 0)
FIOLETOWY = (128, 0, 128)
POMARANCZOWY = (255, 165, 0)
SZARY = (128, 128, 128)
TURKUSOWY = (64, 224, 208)
SZEROKOSC = 700
OKNO = pygame.display.set_mode((SZEROKOSC, SZEROKOSC))
pygame.display.set_caption("Wizualizacja algorytmu wyszukiwania sciezek")


#na statystyki
statystyki_algorytmu = ""

def zmierz_statystyki(algorytm):
    def opakowanie(rysuj, siatka, start, koniec, *args):
        global statystyki_algorytmu
        tracemalloc.start()
        start_czas = time.time()
        wynik = algorytm(rysuj, siatka, start, koniec, *args) if args else algorytm(rysuj, siatka, start, koniec)
        koniec_czas = time.time()
        pamiec, _ = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        odwiedzone = len([s for rzad in siatka for s in rzad if s.czy_otwarty() or s.czy_zamkniety() or s.kolor == FIOLETOWY])
        dlugosc_sciezki = len([s for rzad in siatka for s in rzad if s.kolor == FIOLETOWY])

        nazwa_alg = {
            'dijkstra': 'Dijkstra',
            'astar': 'A* (Manhattan)',
            'astar_euklides': 'A* (Euklides)',
            'bfs': 'BFS',
            'dfs': 'DFS'
        }.get(algorytm.__name__, algorytm.__name__)

        statystyki_algorytmu = (
            f"{nazwa_alg} | Czas: {koniec_czas - start_czas:.2f}s  "
            f"Pamiec: {pamiec / 1024:.1f}KB  "
            f"Wierzcholki: {odwiedzone}  "
            f"Dlugosc sciezki: {dlugosc_sciezki}"
        )
        return wynik
    return opakowanie


class Pole:
    def __init__(self, wiersz, kolumna, rozmiar, ilosc_wierszy):
        self.wiersz = wiersz
        self.kolumna = kolumna
        self.x = wiersz * rozmiar
        self.y = kolumna * rozmiar
        self.kolor = BIALY
        self.sasiedzi = []
        self.rozmiar = rozmiar
        self.ilosc_wierszy = ilosc_wierszy

    def pozycja(self):
        return self.wiersz, self.kolumna

    def czy_zamkniety(self): return self.kolor == CZERWONY
    def czy_otwarty(self): return self.kolor == ZIELONY
    def czy_bariera(self): return self.kolor == CZARNY
    def czy_start(self): return self.kolor == POMARANCZOWY
    def czy_cel(self): return self.kolor == TURKUSOWY

    def zresetuj(self): self.kolor = BIALY
    def ustaw_start(self): self.kolor = POMARANCZOWY
    def ustaw_zamkniety(self): self.kolor = CZERWONY
    def ustaw_otwarty(self): self.kolor = ZIELONY
    def ustaw_bariera(self): self.kolor = CZARNY
    def ustaw_cel(self): self.kolor = TURKUSOWY
    def ustaw_sciezka(self): self.kolor = FIOLETOWY

    def rysuj(self, okno):
        pygame.draw.rect(okno, self.kolor, (self.x, self.y, self.rozmiar, self.rozmiar))

    def aktualizuj_sasiadow(self, siatka):
        self.sasiedzi = []
        if self.wiersz < self.ilosc_wierszy - 1 and not siatka[self.wiersz + 1][self.kolumna].czy_bariera():
            self.sasiedzi.append(siatka[self.wiersz + 1][self.kolumna])
        if self.wiersz > 0 and not siatka[self.wiersz - 1][self.kolumna].czy_bariera():
            self.sasiedzi.append(siatka[self.wiersz - 1][self.kolumna])
        if self.kolumna < self.ilosc_wierszy - 1 and not siatka[self.wiersz][self.kolumna + 1].czy_bariera():
            self.sasiedzi.append(siatka[self.wiersz][self.kolumna + 1])
        if self.kolumna > 0 and not siatka[self.wiersz][self.kolumna - 1].czy_bariera():
            self.sasiedzi.append(siatka[self.wiersz][self.kolumna - 1])

    def __lt__(self, inny):
        return False


def heurystyka(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)

def heurystyka_euklidesowa(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return ((x1 - x2)**2 + (y1 - y2)**2) ** 0.5

def odtworz_sciezke(skamd, obecny, rysuj):
    while obecny in skamd:
        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                pygame.quit()
        obecny = skamd[obecny]
        if not obecny.czy_start() and not obecny.czy_cel():
            obecny.ustaw_sciezka()
        rysuj()


def astar(rysuj, siatka, start, koniec):
    licznik = 0
    otwarte = PriorityQueue()
    otwarte.put((0, licznik, start))
    skad = {}
    koszt_g = {pole: float("inf") for rzad in siatka for pole in rzad}
    koszt_g[start] = 0
    koszt_f = {pole: float("inf") for rzad in siatka for pole in rzad}
    koszt_f[start] = heurystyka(start.pozycja(), koniec.pozycja())
    zamkniete = {start}

    while not otwarte.empty():
        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                pygame.quit()

        obecny = otwarte.get()[2]
        if obecny == koniec:
            odtworz_sciezke(skad, koniec, rysuj)
            koniec.ustaw_cel()
            return True
        for sasiad in obecny.sasiedzi:
            tymczasowy_g = koszt_g[obecny] + 1

            if tymczasowy_g < koszt_g[sasiad]:
                skad[sasiad] = obecny
                koszt_g[sasiad] = tymczasowy_g
                koszt_f[sasiad] = tymczasowy_g + heurystyka(sasiad.pozycja(), koniec.pozycja())
                if sasiad not in zamkniete:
                    licznik += 1
                    otwarte.put((koszt_f[sasiad], licznik, sasiad))
                    zamkniete.add(sasiad)
                    sasiad.ustaw_otwarty()

        rysuj()
        if obecny != start:
            obecny.ustaw_zamkniety()
    return False

def astar_euklides(rysuj, siatka, start, koniec):
    licznik = 0
    otwarte = PriorityQueue()
    otwarte.put((0, licznik, start))
    skad = {}
    koszt_g = {pole: float("inf") for rzad in siatka for pole in rzad}
    koszt_g[start] = 0
    koszt_f = {pole: float("inf") for rzad in siatka for pole in rzad}
    koszt_f[start] = heurystyka_euklidesowa(start.pozycja(), koniec.pozycja())
    zamkniete = {start}

    while not otwarte.empty():
        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                pygame.quit()
        obecny = otwarte.get()[2]
        if obecny == koniec:
            odtworz_sciezke(skad, koniec, rysuj)
            koniec.ustaw_cel()
            return True
        for sasiad in obecny.sasiedzi:
            tymczasowy_g = koszt_g[obecny] + 1
            if tymczasowy_g < koszt_g[sasiad]:
                skad[sasiad] = obecny
                koszt_g[sasiad] = tymczasowy_g
                koszt_f[sasiad] = tymczasowy_g + heurystyka_euklidesowa(sasiad.pozycja(), koniec.pozycja())
                if sasiad not in zamkniete:
                    licznik += 1
                    otwarte.put((koszt_f[sasiad], licznik, sasiad))
                    zamkniete.add(sasiad)
                    sasiad.ustaw_otwarty()
        rysuj()
        if obecny != start:
            obecny.ustaw_zamkniety()
    return False

def bfs(rysuj, siatka, start, koniec):
    kolejka = Queue()
    kolejka.put(start)
    odwiedzone = {start}
    skad = {}
    while not kolejka.empty():
        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                pygame.quit()
        obecny = kolejka.get()
        if obecny == koniec:
            odtworz_sciezke(skad, koniec, rysuj)
            koniec.ustaw_cel()
            return True
        for sasiad in obecny.sasiedzi:
            if sasiad not in odwiedzone:
                kolejka.put(sasiad)
                odwiedzone.add(sasiad)
                skad[sasiad] = obecny
                sasiad.ustaw_otwarty()
        rysuj()
        if obecny != start:
            obecny.ustaw_zamkniety()
    return False


def dijkstra(rysuj, siatka, start, koniec):
    licznik = 0
    otwarte = PriorityQueue()
    otwarte.put((licznik, start))
    skad = {}
    koszt_g = {pole: float("inf") for rzad in siatka for pole in rzad}
    koszt_g[start] = 0
    odwiedzone = {start}

    while not otwarte.empty():
        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                pygame.quit()
        obecny = otwarte.get()[1]
        if obecny == koniec:
            odtworz_sciezke(skad, koniec, rysuj)
            koniec.ustaw_cel()
            return True
        for sasiad in obecny.sasiedzi:
            tymczasowy_g = koszt_g[obecny] + 1
            if tymczasowy_g < koszt_g[sasiad]:
                skad[sasiad] = obecny
                koszt_g[sasiad] = tymczasowy_g
                if sasiad not in odwiedzone:
                    licznik += 1
                    otwarte.put((licznik, sasiad))
                    odwiedzone.add(sasiad)
                    sasiad.ustaw_otwarty()
        rysuj()
        if obecny != start:
            obecny.ustaw_zamkniety()
    return False


def dfs(rysuj, siatka, start, koniec):
    odwiedzone = {start}
    sciezka = [start]
    def rekurencja(obecny):
        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                pygame.quit()
        if not obecny.czy_start() and not obecny.czy_cel():
            obecny.ustaw_otwarty()
        if obecny == koniec:
            sciezka_map = {sciezka[i]: sciezka[i - 1] for i in range(1, len(sciezka))}
            odtworz_sciezke(sciezka_map, obecny, rysuj)
            koniec.ustaw_cel()
            return True
        for sasiad in obecny.sasiedzi:
            if sasiad not in odwiedzone:
                odwiedzone.add(sasiad)
                sciezka.append(sasiad)
                if rekurencja(sasiad):
                    return True
                sciezka.pop()
        return False

    return rekurencja(start)

astar = zmierz_statystyki(astar)
astar_euklides = zmierz_statystyki(astar_euklides)
bfs = zmierz_statystyki(bfs)
dijkstra = zmierz_statystyki(dijkstra)
dfs = zmierz_statystyki(dfs)

def wyczysc_tymczasowe_pola(siatka):
    for rzad in siatka:
        for pole in rzad:
            if not (pole.czy_bariera() or pole.czy_start() or pole.czy_cel()):
                pole.zresetuj()

def utworz_siatke(wiersze, szerokosc):
    siatka = []
    rozmiar = szerokosc // wiersze
    for i in range(wiersze):
        siatka.append([Pole(i, j, rozmiar, wiersze) for j in range(wiersze)])
    return siatka


def rysuj_siatke(okno, wiersze, szerokosc):
    rozmiar = szerokosc // wiersze
    for i in range(wiersze):
        pygame.draw.line(okno, SZARY, (0, i * rozmiar), (szerokosc, i * rozmiar))
        for j in range(wiersze):
            pygame.draw.line(okno, SZARY, (j * rozmiar, 0), (j * rozmiar, szerokosc))


def rysuj(okno, siatka, wiersze, szerokosc):
    global statystyki_algorytmu
    okno.fill(BIALY)
    for rzad in siatka:
        for pole in rzad:
            pole.rysuj(okno)
    rysuj_siatke(okno, wiersze, szerokosc)
    if statystyki_algorytmu:
        czcionka = pygame.font.SysFont(None, 22)
        tekst = czcionka.render(statystyki_algorytmu, True, (0, 0, 0))
        okno.blit(tekst, (10, szerokosc + 10))  
    pygame.display.update()

def kliknieta_pozycja(poz, wiersze, szerokosc):
    rozmiar = szerokosc // wiersze
    y, x = poz
    return y // rozmiar, x // rozmiar


def start_program(okno, szerokosc):
    WIERSZE = 50
    WYSOKOSC_SIATKI = szerokosc
    WYSOKOSC_OKNA = szerokosc + 40  # dodatkowy pasek na statystyki
    OKNO = pygame.display.set_mode((szerokosc, WYSOKOSC_OKNA))
    siatka = utworz_siatke(WIERSZE, szerokosc)
    poczatek = koniec = None
    dziala = True

    while dziala:
        rysuj(okno, siatka, WIERSZE, szerokosc)

        for zdarzenie in pygame.event.get():
            if zdarzenie.type == pygame.QUIT:
                dziala = False

            if pygame.mouse.get_pressed()[0]:
                poz = pygame.mouse.get_pos()
                w, k = kliknieta_pozycja(poz, WIERSZE, szerokosc)
                pole = siatka[w][k]
                if not poczatek and pole != koniec:
                    poczatek = pole
                    poczatek.ustaw_start()
                elif not koniec and pole != poczatek:
                    koniec = pole
                    koniec.ustaw_cel()
                elif pole != koniec and pole != poczatek:
                    pole.ustaw_bariera()

            elif pygame.mouse.get_pressed()[2]:
                poz = pygame.mouse.get_pos()
                w, k = kliknieta_pozycja(poz, WIERSZE, szerokosc)
                pole = siatka[w][k]
                pole.zresetuj()
                if pole == poczatek:
                    poczatek = None
                elif pole == koniec:
                    koniec = None

            if zdarzenie.type == pygame.KEYDOWN:
                if zdarzenie.key == pygame.K_c:
                    poczatek = koniec = None
                    siatka = utworz_siatke(WIERSZE, szerokosc)

                if zdarzenie.key == pygame.K_1 and poczatek and koniec:
                    wyczysc_tymczasowe_pola(siatka)
                    for rzad in siatka:
                        for pole in rzad:
                            pole.aktualizuj_sasiadow(siatka)
                    dijkstra(lambda: rysuj(okno, siatka, WIERSZE, szerokosc), siatka, poczatek, koniec)

                if zdarzenie.key == pygame.K_2 and poczatek and koniec:
                    wyczysc_tymczasowe_pola(siatka)
                    for rzad in siatka:
                        for pole in rzad:
                            pole.aktualizuj_sasiadow(siatka)
                    astar(lambda: rysuj(okno, siatka, WIERSZE, szerokosc), siatka, poczatek, koniec)

                if zdarzenie.key == pygame.K_3 and poczatek and koniec:
                    wyczysc_tymczasowe_pola(siatka)
                    for rzad in siatka:
                        for pole in rzad:
                            pole.aktualizuj_sasiadow(siatka)
                    bfs(lambda: rysuj(okno, siatka, WIERSZE, szerokosc), siatka, poczatek, koniec)

                if zdarzenie.key == pygame.K_4 and poczatek and koniec:
                    wyczysc_tymczasowe_pola(siatka)
                    for rzad in siatka:
                        for pole in rzad:
                            pole.aktualizuj_sasiadow(siatka)
                    odwiedzone = {poczatek}
                    sciezka = [poczatek]
                    dfs(lambda: rysuj(okno, siatka, WIERSZE, szerokosc), siatka, poczatek, koniec)

                if zdarzenie.key == pygame.K_5 and poczatek and koniec:
                    wyczysc_tymczasowe_pola(siatka)
                    for rzad in siatka:
                        for pole in rzad:
                            pole.aktualizuj_sasiadow(siatka)
                    astar_euklides(lambda: rysuj(okno, siatka, WIERSZE, szerokosc), siatka, poczatek, koniec)
    pygame.quit()


if __name__ == "__main__":
    start_program(OKNO, SZEROKOSC)

# Implementacja i analiza algorytmu A* (A-Star) w wyszukiwaniu najkrótszej ścieżki  
**Praca magisterska – Adrian Dereń (2024)**

Projekt przedstawia implementację algorytmu **A\*** oraz analizę jego działania w różnych
scenariuszach wyszukiwania ścieżek w grafach.  
Algorytm A\* jest jednym z najważniejszych i najczęściej wykorzystywanych algorytmów
w systemach nawigacji, grach komputerowych, robotyce i analizie sieci.

W projekcie zaimplementowano:
- algorytm A* na grafach ważonych,  
- różne rodzaje heurystyk,  
- testy jakości i porównania przebiegów,  
- analizę wydajności, złożoności i dokładności,  
- wizualizację działania algorytmu.

Pełny opis implementacji i badań znajduje się w pliku PDF dołączonym w repozytorium.

---

## Zawartość repozytorium

- **mapa_rzeszowa.rar / planner_z_heurystyka.rar / algorytmy_na_siatce.rar** – implementacje algorytmów 
- **praca_mgr_adrian_deren.pdf** – praca magisterska (pełna dokumentacja projektu)  
---

## Cel projektu

Celem pracy było:
- zaimplementowanie algorytmu A*,  
- porównanie różnych heurystyk (Euklidesowa, Manhattan) 
- analiza ich wpływu na czas działania oraz długość ścieżki,  
- ocena poprawności heurystyk (admisyjność, monotoniczność),  
- analiza przypadków optymalnych i suboptymalnych.

---

## Opis algorytmu A\*

Algorytm A* przeszukuje graf, minimalizując funkcję:

**f(n) = g(n) + h(n)**

gdzie:
- **g(n)** – koszt dojścia do wierzchołka *n*,  
- **h(n)** – heurystyka (szacowany koszt do celu).

W projekcie zaimplementowano rodzaje heurystyk:
- **h1 – odległość Euklidesowa**  
- **h2 – odległość Manhattan**

Każda z nich została przetestowana na tych samych grafach i porównana
pod względem liczby odwiedzonych wierzchołków oraz czasu działania.

---

## Implementacja i funkcjonalności

W projekcie zaimplementowano:

### Reprezentację grafu
- koszty wagowe  
- możliwość budowy grafów losowych  

### Algorytm A*
- czysta implementacja bez zależności zewnętrznych  
- kolejka priorytetowa (min-heap)  
- pełna rekonstrukcja znalezionej ścieżki  
- zabezpieczenie przed zapętleniem  
- liczenie liczby operacji i odwiedzeń  

### Warianty heurystyk
- testowanie wpływu heurystyki na wydajność  
- analiza admissibility oraz consistency  
- porównanie działania A* z Dijkstrą oraz BFS, DFS

### Wizualizacja
- prezentacja grafu  
- rysowanie znalezionej ścieżki  
- oznaczanie rozwiniętych węzłów  
- porównanie ścieżek między heurystykami  

---

## Wyniki eksperymentów

W pracy przeprowadzono analizę, w której porównano:

- długość ścieżek dla każdej heurystyki  
- liczbę rozwiniętych węzłów  
- czas działania algorytmu  
- wpływ heurystyki na szybkość i trafność  
- przypadki, w których heurystyka powoduje degradację wyników  

Najważniejsze obserwacje:
- heurystyka Euklidesowa była najefektywniejsza na grafach przestrzennych,  
- Manhattan sprawdzał się najlepiej na siatkach regularnych,  
- heurystyka zerowa (Dijkstra) była najwolniejsza, ale zawsze optymalna.

Szczegółowe wyniki znajdują się w dokumencie PDF.

---

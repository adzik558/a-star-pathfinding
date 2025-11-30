# Implementacja i analiza algorytmu A* (A-Star) w wyszukiwaniu najkrótszej ścieżki  
**Praca magisterska – Adrian Dereń (2025)**

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
- porównanie algorytmu A* z innymi algorytmami wyszukiwania najkrótszych ścieżek,
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

1) **Dla losowego grafu o parametrach:** </br>
•	50 wierzchołków, </br>
•	gęstość = 0.07, </br>
•	ścieżka od 1 do 40, </br>
•	wagi krawędzi losowe (zakres od 1 do 3) </br>

<img width="1104" height="555" alt="image" src="https://github.com/user-attachments/assets/3af350f4-df3b-44ca-8a97-4ee3ea80a648" /> </br>

2) **Siatka 2D o wymiarach 50x50** </br>
Kolor Fioletowy przedstawia wyznaczoną ścieżke dla danego algorytmu: </br>
- **BFS** </br>

<img width="504" height="527" alt="image" src="https://github.com/user-attachments/assets/2882c95f-6e7b-4325-b8bb-82d78f955af5" /> </br>

- **DFS** </br>

<img width="494" height="520" alt="image" src="https://github.com/user-attachments/assets/5d91b2ac-9141-4fe8-ab25-c86d64cb9b22" /> </br>

- **Dijkstra** </br>

<img width="519" height="544" alt="image" src="https://github.com/user-attachments/assets/23908581-cee3-4715-acbb-2629c56222dc" /> </br>

- **Algorytm A*** </br>

a) **Heurystyka Manhattan** </br>

<img width="486" height="505" alt="image" src="https://github.com/user-attachments/assets/85ace8b8-4552-4de0-b798-1d75422fb20d" /> </br>


b) **Heurystyka Euklidesowa** </br>

<img width="537" height="559" alt="image" src="https://github.com/user-attachments/assets/e02e65a8-bcdb-46ee-a94f-680032df9a42" /> </br>

3) **Rzeczywista mapa Rzeszowa:** </br>

-Trasa Politechnika - Dworzec Kolejowy: </br>

<img width="951" height="498" alt="image" src="https://github.com/user-attachments/assets/3e6f4944-cd36-47a9-89e7-d19f830ff8f2" /> </br>

-Trasa Politechnika - Uniwersytet: </br>

<img width="888" height="466" alt="image" src="https://github.com/user-attachments/assets/62c849ee-2dff-45dd-92a8-1969a9bad098" />


---

## Wyniki eksperymentów

W pracy przeprowadzono analizę, w której porównano:

- długość ścieżek dla każdej heurystyki  
- liczbę rozwiniętych węzłów  
- czas działania algorytmu  
- wpływ heurystyki na szybkość i trafność  
- przypadki, w których heurystyka powoduje degradację wyników

1) **Graf Ważony:** </br>

<img width="548" height="143" alt="image" src="https://github.com/user-attachments/assets/0f587d34-7317-4c08-82b9-f78f4b32aecc" /> </br>

2) **Siatka 2D:** </br>

<img width="547" height="127" alt="image" src="https://github.com/user-attachments/assets/44f4f56f-b413-438a-89ce-e302bc5d6bab" /> </br>

3) **Mapa Rzeszowa:** </br>

**Politechnika - Dworzec Główny:** </br>

<img width="549" height="111" alt="image" src="https://github.com/user-attachments/assets/4920269e-f6d5-4210-a0c4-9da897651237" /> </br>

**Politechnika - Uniwersytet:** </br>

<img width="549" height="111" alt="image" src="https://github.com/user-attachments/assets/1a8cbadb-b0e7-43cc-9ac4-05179136f37a" /> </br>
---


## Najważniejsze obserwacje: </br>
W środowisku grafów ważonych najlepsze rezultaty dawały metody uwzględniające wagi – zwłaszcza Dijkstra oraz A* z heurystyką euklidesową lub manhattan. Oba podejścia zapewniały dobre wyniki przy stosunkowo niskim koszcie obliczeniowym. BFS przeszukiwał szerzej i zużywał więcej pamięci, mimo że również znajdował poprawną ścieżkę. DFS natomiast często zbaczał z optymalnej trasy i generował wynik o wyższym koszcie.
Na siatkach 2D dominowały te same rozwiązania. Algorytm A* ponownie wypadał najlepiej, zarówno pod względem szybkości działania, jak i liczby odwiedzanych pól. BFS oraz Dijkstra dostarczały poprawnych wyników, lecz były mniej efektywne pod względem zasobów. DFS, mimo szybkości działania w niektórych przypadkach, nie gwarantował jakościowych tras i wymagał znacznie więcej pamięci operacyjnej. W tym środowisku można było również zauważyć wpływ wyboru heurystyki na efektywność A* (heurystyka manhattan działa lepiej w układach bardziej regularnych).
W środowisku najbardziej zbliżonym do rzeczywistości czyli na mapie Rzeszowa, algorytmy trasowania zachowywały się nieco inaczej. Dijkstra i A* prowadziły trasy głównymi drogami, tworząc sensowne i intuicyjne przebiegi co potwierdzają wizualizacje. BFS, mimo że działał szybko, częściej wybierał ścieżki boczne, a to w efekcie skutkowało większą liczbą odwiedzonych węzłów oraz wydłużeniem trasy. Heurystyka manhattan, ze względu na brak regularnej struktury ulic, nie przynosiła tu żadnych korzyści. A* z heurystyką euklidesową był w tym przypadku najbardziej uniwersalny 
i efektywny


**Szczegółowe wyniki znajdują się w dokumencie PDF.**

---

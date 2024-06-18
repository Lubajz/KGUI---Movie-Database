# KGUI - Semestrální práce 
## Luboš Kemr

Jednoduchá aplikace pro načítání dat z API https://developer.themoviedb.org/reference/discover-movie a uložení do DB.
Následné načtení dat a zpracování v podobě grafů či tabulky.
Vytvořeno převážně pomocí tkinteru a asyncio pro asynchronní volání API.

## Funkcionality

### Filter Bar
Stránka obsahuje jednoduchý filter bar s možností filtrovat filmy dle názvu filmu, žánru, jazyka a datumu vydání.

### Režimy
Pomocí tlačítek Charts a Table lze přepínat mezi režimem zobrazení v podobě grafů nebo v podobě tabulky. Jedná se o oddělená samostatná okna.

#### Tabulka
Zobrazení načtených filmů z API ve scrollovatelné tabulce eřazené dle abecedy vzestupně.

#### Grafy
Obrazovka se 4 grafy. 
Hlavní graf zobrazuje top 15 filmů s největší popularitou dle pole **popularity**.
Menší grafy zobrazují top 3 filmy dle: - počtů hodnocení - **vote_count**
                                       - průměrného hodnocení - **vote_average**
                                       - nejvíc vyskytované žánry - **genre**


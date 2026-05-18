# Datové zpracování katastrálních reportů & SMTP export

Praktické řešení technické úlohy v jazyce Python (3.x) zaměřené na objektově orientované zpracování dat, čištění specifických datových typů (české desetinné čárky, anomálie v katastrálních datech) a automatizovaný export výsledků.

## Hlavní funkcionality
- **Robustní parsování:** Načítání dat z formátu Excel (`.xlsx`) za použití knihovny `pandas`.
- **Čištění dat:** Ošetření českého formátu desatinných čárek u geodetických veličin (`Plocha VB`, `Délka`) a bezpečné odfiltrování nečíselných anomálií (např. znaky 'X').
- **Statistický modul:** Automatický výpočet agregací (unikátní hodnoty, prázdné buňky, matematické průměry, minima/maxima) a zápis do logu `<název>_statistika.log`.
- **Bezpečná konfigurace:** Parametry SMTP serveru jsou kompletně odděleny od zdrojového kódu a načítají se dynamicky přes `config.ini` (v souladu s principy bezpečné správy přihlašovacích údajů).
- **Logování a testování:** Implementováno podrobné logování operací do `app_operation.log` a základní sada unit testů (`unittest`) s mockováním SMTP a IO operací.

## Architektura projektu
```text
├── data_processing.py      # Třída DataProcessing s aplikační logikou
├── main.py                 # Hlavní spouštěcí skript aplikace
├── config.ini              # Konfigurační soubor (v repozitáři ukázková šablona)
├── requirements.txt        # Seznam závislostí
├── test_data_processing.py # Unit testy pro ověření funkčnosti komponent
└── .gitignore              # Ignorování lokálních dat, logů a cache

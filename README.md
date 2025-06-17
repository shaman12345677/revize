# Revize Školka/Škola

Webová aplikace pro správu revizí ve školce a škole s ukládáním dat do Google Sheets.

## Funkce
- Přihlášení uživatele (role: administrátor/uživatel)
- Správa uživatelů (pouze administrátor)
- Evidence revizí pro školku (List1) a školu (List2)
- Automatické výpočty termínů a stavů
- Moderní a přehledné rozhraní
- Ukládání a načítání dat z Google Sheets
- Možnost nasazení na GitHub Pages (frontend) a Render.com (backend)

## Struktura projektu
- `docs/` – frontend (HTML, CSS, JS) pro GitHub Pages
- `backend.py` – Flask backend (API)
- `requirements.txt` – závislosti pro backend
- `service_account.json` – Google API klíč (nenahrávej do repozitáře!)

## Nasazení backendu na Render.com
1. Vytvoř si účet na [Render.com](https://render.com/)
2. Vytvoř nový **Web Service** a propojení s tímto repozitářem
3. Build command: `pip install -r requirements.txt`
4. Start command: `python backend.py`
5. Nahraj `service_account.json` jako Secret File
6. Po nasazení získáš veřejnou URL (např. `https://revize.onrender.com`)

## Nasazení frontendu na GitHub Pages
1. Složka `docs/` obsahuje všechny potřebné soubory
2. V nastavení repozitáře na GitHubu nastav Pages na branch `main` a složku `/docs`
3. Výsledná adresa bude např. `https://shaman12345677.github.io/revize/`
4. V souboru `docs/app.js` je potřeba mít správně nastavenou proměnnou `BACKEND_URL` na adresu backendu

## Práce s aplikací
- Přihlaš se jako administrátor pro správu uživatelů a obou revizních sekcí
- Běžný uživatel vidí pouze revize podle svého typu (školka/škola)
- Administrátor má typ automaticky `školka,škola` a vidí vše
- Všechny změny se ukládají do Google Sheets (nutné správné sdílení a nastavení API)

## Bezpečnost
- Nikdy nenahrávej `service_account.json` do veřejného repozitáře!
- Backend musí být chráněn (např. CORS, bezpečné heslo, případně HTTPS)

## Požadavky
- Python 3.8+
- Flask, Flask-CORS, google-api-python-client, google-auth, bcrypt

## Vývoj a testování
- Backend lze spustit lokálně: `python backend.py`
- Frontend lze testovat otevřením `docs/index.html` v prohlížeči nebo přes Pages

## Autor
- [shaman12345677](https://github.com/shaman12345677)

## Autoři a poděkování

Tento projekt vytvořil:
- **Autor aplikace:** [shaman12345677](https://github.com/shaman12345677)

Schváleno a převzato:
- **Zadavatel:** __________________________
- **Datum:** _____________________________

---

Děkujeme za spolupráci a důvěru!

Pro jakékoli dotazy nebo vylepšení otevři issue nebo mě kontaktuj.

---

© Samek Tomáš 2025 
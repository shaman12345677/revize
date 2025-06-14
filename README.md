# Revize Školka

Webová aplikace pro správu revizí ve školce s ukládáním dat do Google Sheets.

## Funkce

- Přihlášení pomocí hesla
- Přidávání nových revizí
- Zobrazení seznamu revizí
- Mazání revizí
- Ukládání dat do Google Sheets
- Přístup odkudkoli

## Nastavení

1. Vytvořte nový Google Sheet s následujícími sloupci:
   - Datum
   - Popis
   - Stav

2. Získejte Google Sheets API klíč:
   - Jděte na [Google Cloud Console](https://console.cloud.google.com)
   - Vytvořte nový projekt
   - Povolte Google Sheets API
   - Vytvořte API klíč

3. Upravte soubor `app.js`:
   - Nahraďte `YOUR_SPREADSHEET_ID` ID vašeho Google Sheetu
   - Nahraďte `YOUR_API_KEY` vaším Google API klíčem
   - Volitelně změňte `APP_PASSWORD` na jiné heslo

4. Nahrajte soubory na GitHub Pages:
   - Vytvořte nový GitHub repozitář
   - Nahrajte všechny soubory
   - Povolte GitHub Pages v nastavení repozitáře

## Použití

1. Otevřete webovou stránku
2. Přihlaste se pomocí hesla
3. Používejte tlačítko "Přidat revizi" pro nové záznamy
4. Data se automaticky ukládají do Google Sheets

## Bezpečnost

- Heslo je uloženo v kódu (v produkci by mělo být bezpečně uloženo)
- Google Sheets API klíč je omezen na doménu GitHub Pages
- Data jsou přístupná pouze po přihlášení 
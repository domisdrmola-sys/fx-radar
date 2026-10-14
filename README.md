# SAB FX RADAR

Webová aplikace (PWA) pro EUR/CZK, USD/CZK, EUR/USD a PLN/CZK. Běží v prohlížeči bez přihlášení a bez instalace aplikací.

## Co odkud bere
- **Kurzy a grafy:** při každém otevření se stahují přímo z veřejného Frankfurter API (denní referenční kurzy ECB, rok zpět). Telefon odesílá jen dotaz na kurzy, žádná vaše data.
- **Zprávy a centrální banky:** soubor `data.json` v tomto repozitáři. Jeho aktualizace mění jen tento soubor, aplikace zůstává stejná.
- **Offline:** poslední stažená data zůstanou v telefonu a aplikace se otevře i bez signálu (štítek nahoře pak ukazuje „Offline“).

## Přidání na plochu
- **iPhone (Safari):** otevřít adresu → Sdílet → Přidat na plochu.
- **Android (Chrome):** otevřít adresu → menu ⋮ → Přidat na plochu / Instalovat aplikaci.

## Formát data.json
Soubor plní naplánovaná úloha 4× denně. Klíče:
- `news` – zprávy k párům, `banks` – centrální banky
- `cnb` – kurz ČNB (EUR, USD, PLN, HUF za 100)
- `mm` – mezibankové sazby pro forwardy (PRIBOR, EURIBOR, US T-bill, WIBOR; 1M/3M/6M/12M)
- `diff` – měsíční vývoj 3M PRIBOR vs. 3M EURIBOR
- `risk` – Brent, plyn TTF, spready BTP–Bund a OAT–Bund, VIX
- `calendar` – makrokalendář (pražský čas), `forecast` – prognóza ČNB

Svátky a dny bez vypořádání (ČR, TARGET2, USA, Polsko) aplikace počítá sama. Rozpočtové a cílové kurzy se ukládají jen v telefonu uživatele.

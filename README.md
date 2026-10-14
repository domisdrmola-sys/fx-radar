# FX Radar

Webová aplikace (PWA) pro EUR/CZK, USD/CZK, EUR/USD a PLN/CZK. Běží v prohlížeči bez přihlášení a bez instalace aplikací.

## Co odkud bere
- **Kurzy a grafy:** při každém otevření se stahují přímo z veřejného Frankfurter API (denní referenční kurzy ECB, rok zpět). Telefon odesílá jen dotaz na kurzy, žádná vaše data.
- **Zprávy a centrální banky:** soubor `data.json` v tomto repozitáři. Jeho aktualizace mění jen tento soubor, aplikace zůstává stejná.
- **Offline:** poslední stažená data zůstanou v telefonu a aplikace se otevře i bez signálu (štítek nahoře pak ukazuje „Offline“).

## Přidání na plochu
- **iPhone (Safari):** otevřít adresu → Sdílet → Přidat na plochu.
- **Android (Chrome):** otevřít adresu → menu ⋮ → Přidat na plochu / Instalovat aplikaci.

## Formát data.json
```
{ "news":  { "asOf": "YYYY-MM-DD", "pairs": { "EUR/CZK": [ {source, currency, title, url, summary, why} ], ... } },
  "banks": { "asOf": "YYYY-MM-DD", "banks": [ {id, name, currency, rate, rateLabel, next, bias, outlook6m, expect, drivers, url, source} ] } }
```

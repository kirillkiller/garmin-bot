# Jak vypnout MFA na Garmin Connect

## Postup:

1. **Přihlas se na Garmin Connect**
   - Jdi na https://connect.garmin.com
   - Přihlas se svým účtem

2. **Otevři nastavení účtu**
   - Klikni na ikonu profilu (pravý horní roh)
   - Vyber "Account Settings" nebo "Nastavení účtu"

3. **Najdi sekci zabezpečení**
   - Hledej "Security" nebo "Zabezpečení"
   - Nebo "Two-Factor Authentication" / "Dvoufázové ověření"

4. **Vypni MFA**
   - Najdi přepínač pro "Two-Factor Authentication" nebo "2FA"
   - Vypni ho
   - Potvrď změnu (možná budeš muset zadat heslo)

## Alternativní cesta:

1. Jdi přímo na: https://connect.garmin.com/modern/settings/account/security
2. Najdi "Two-Factor Authentication"
3. Vypni ho

## POZOR:

- Po vypnutí MFA bude tvůj účet méně zabezpečený
- Pokud máš citlivá data, zvaž, jestli to chceš udělat
- Pro bot je to ale výhodné - nebudeš muset zadávat MFA kód při každém spuštění

## Po vypnutí MFA:

- Bot by měl fungovat bez nutnosti zadávat MFA kód
- Session by se měla ukládat a znovu používat
- Nebudou problémy s rate limitingem kvůli MFA


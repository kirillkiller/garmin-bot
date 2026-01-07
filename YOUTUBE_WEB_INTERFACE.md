# 📺 YouTube Webové Rozhraní

Webové rozhraní pro prohlížení YouTube videí a transkriptů.

## 🚀 Spuštění

```bash
python3 web_app.py
```

Pak otevři prohlížeč na: **http://localhost:5000**

## 📋 Funkce

### YouTube Tab

1. **Statistiky**
   - Celkový počet videí
   - Počet videí s transkripty
   - Počet videí bez transkriptů
   - Počet aktivních kanálů

2. **Filtrování**
   - Podle kanálu (dropdown)
   - Podle transkriptu (všechna / s transkriptem / bez transkriptu)

3. **Seznam videí**
   - Název videa
   - Datum publikace
   - Jazyk transkriptu
   - Odkaz na video
   - Tlačítko pro zobrazení transkriptu

4. **Zobrazení transkriptu**
   - Modal s plným transkriptem
   - Kopírování do schránky
   - Odkaz na video

## 🎯 Použití

1. Spusť webové rozhraní
2. Klikni na tab **📺 YouTube**
3. Vyber kanál (nebo nech "Všechny kanály")
4. Vyber filtr (nebo nech "Všechna videa")
5. Klikni na **📝 Zobrazit transkript** u videa
6. Transkript se zobrazí v modalu
7. Můžeš kopírovat transkript pomocí tlačítka

## 🔄 Obnovení dat

Klikni na tlačítko **🔄 Obnovit** pro načtení nejnovějších dat z databáze.

## 💡 Tipy

- Transkripty jsou uloženy v databázi, takže jsou dostupné i offline
- Můžeš filtrovat podle kanálu pro lepší přehled
- Transkripty jsou v čistém textu, můžeš je kopírovat


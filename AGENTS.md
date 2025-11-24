# CML Agent Instructions

## Automatická Startup Procedura

**DŮLEŽITÉ: Pokud dostaneš příkaz přečíst tento soubor při startu, AUTOMATICKY proveď následující kroky:**

1. **Spusť startup music** - přehraj `~/cml/CML-CENTRÁLNÍ MOZEK LIDSTVA.mp3` na pozadí (mpg123)
2. **Zjisti dostupné MCP servery** - přečti `~/.config/opencode/opencode.json` a zjisti, jaké nástroje máš k dispozici
3. Zjisti aktuální socket path z `~/.opencode-socket`
4. Vytvoř nové split okno pro listener
5. Spusť v něm CML listener
6. Nastav velikost okna listenera (spodní okno zmenšit na cca 1/3 výšky)
7. Pojmenuj okna
8. Nastav průhlednost hlavního okna (Window 1) na 0.65
9. Vrať fokus do hlavního okna
10. **Zastav startup music** - ukonči přehrávání MP3 (pkill mpg123) před prvním hlasovým výstupem

---

## Startup Procedure

Po startu OpenCode s CML voice control je potřeba spustit následující:

### 1. Vytvoření nového okna pro listener

```bash
# Vytvořit nové okno rozdělením (split) v Kitty
kitty @ --to unix:/tmp/kitty-socket-XXXXX launch --type=window --cwd=current
```

To vytvoří nové okno (Window 2) ve stejném Kitty tabu, ale rozdělené na půl obrazovky.

### 2. Spuštění CML listenera v novém okně

```bash
# Poslat příkaz do nového okna (Window 2)
kitten @ --to unix:/tmp/kitty-socket-XXXXX send-text --match id:2 "cd ~/cml && ./start-cml-voice.sh"
kitten @ --to unix:/tmp/kitty-socket-XXXXX send-key --match id:2 enter
```

### 3. Nastavení velikosti okna listenera

**PREFEROVANÁ VELIKOST:**
- Horní okno (OpenCode, id:1): **51 řádků** (~70% výšky)
- Dolní okno (CML Voice, id:2): **22 řádků** (~30% výšky)

```bash
# Zmenšit spodní okno (listener) na preferovanou velikost
# Po vytvoření split okna (50:50), zmenšit dolní o 13 řádků celkem
kitty @ --to unix:/tmp/kitty-socket-XXXXX resize-window --match id:2 --axis vertical --increment -13
```

### 4. Pojmenování oken

```bash
# Nastavit názvy pro snadnější identifikaci
kitty @ --to unix:/tmp/kitty-socket-XXXXX set-window-title --match id:1 "OpenCode AI"
kitty @ --to unix:/tmp/kitty-socket-XXXXX set-window-title --match id:2 "CML Voice Listener"
```

### 5. Nastavení průhlednosti hlavního okna

```bash
# Nastavit průhlednost pozadí hlavního okna na 0.65
kitty @ --to unix:/tmp/kitty-socket-XXXXX set-background-opacity --match id:1 0.65
```

### 6. Vrácení fokusu do OpenCode

```bash
# Vrátit fokus zpět do hlavního okna
kitty @ --to unix:/tmp/kitty-socket-XXXXX focus-window --match id:1
```

## Aktivace Poslouchání Po Otázce

**KRITICKÉ PRAVIDLO:**

Když odpověď končí **otázkou** (např. "Co přesně nefunguje?", "Co potřebuješ upravit?", "Mám ho nainstalovat?"), MUSÍŠ:

1. **VŽDY** spustit trigger pro aktivaci auto-poslouchání
2. Posluchač automaticky začne poslouchat do 5 sekund
3. Uživatel má čas odpovědět bez nutnosti říkat "C M L"
4. **PLATÍ I PRO PSANÉ OTÁZKY** - i když otázku jen napíšeš (nevyslovuješ ji), stále zavolej trigger!

**Příkaz pro aktivaci (spustit asynchronně):**
```bash
~/cml/trigger-auto-listen.sh &
```

**Kdy použít:**
- ✅ Když tvá odpověď končí otázkou (ať už vyslovená nebo jen psaná!)
- ✅ Když očekáváš okamžitou reakci uživatele
- ✅ Když je potřeba více informací od uživatele
- ✅ I když nevyslovuješ otázku TTS, ale píšeš ji v textu
- ❌ Když pouze informuješ o dokončení úkolu (bez otázky)
- ❌ Když nepotřebuješ další vstup

**Příklad použití:**
```bash
# Na konci odpovědi s VYSLOVOVANOU otázkou:
~/cml/voice-output/text-to-speech.sh "Co potřebuješ upravit?" &
~/cml/trigger-auto-listen.sh &

# Na konci odpovědi s POUZE PSANOU otázkou (bez TTS):
# Stále zavolat trigger, i když otázka není vyslovena!
~/cml/trigger-auto-listen.sh &
```

**Jak to funguje:**
1. Skript vytvoří trigger soubor `/tmp/cml-auto-listen.trigger`
2. CML listener detekuje trigger během své smyčky (kontrola každých ~30ms)
3. Automaticky přehraje "Ano?" a začne nahrávat
4. Uživatel může odpovědět bez wake word

---

## Git Workflow - Verzování Změn

**KRITICKÉ PRAVIDLO PRO PROGRAMOVÁNÍ:**

Když provádíš **jakékoliv změny v souborech** (programování, editace konfigurace, úpravy skriptů), MUSÍŠ:

1. **Zkontrolovat, zda je adresář git repozitář**
   ```bash
   git status
   ```

2. **Pokud ANO (adresář JE git repozitář), vytvořit commit po každé logické změně:**
   ```bash
   git add <změněné-soubory>
   git commit -m "Popisná zpráva změny"
   ```

3. **Pokud NE (adresář NENÍ git repozitář):**
   - **NENAVRHOVAT inicializaci git**
   - **NEPTAT SE, zda inicializovat**
   - **POUZE pracovat s běžnými soubory bez verzování**
   - Commity se dělají POUZE v existujících git repozitářích

**Kdy vytvořit commit:**
- ✅ Po dokončení funkční změny (nová funkce, oprava bugu)
- ✅ Před začátkem větší refaktorizace
- ✅ Po úspěšném otestování změny
- ✅ Před experimentálními změnami (aby bylo kam se vrátit)
- ❌ Nekompletní změny (rozbité, nefunkční)
- ❌ Dočasné testovací úpravy

**Výhody tohoto přístupu:**
- Možnost vrátit se k předchozímu stavu (`git reset --hard HEAD~1`)
- Historie všech změn a jejich důvodů
- Snadné porovnání verzí (`git diff`)
- Bezpečné experimentování s novými řešeními

**Commit message guidelines:**
- Česky, stručně, výstižně
- Začínat velkým písmenem
- Např: "Přidána validace vstupů", "Opravena chyba v parsování", "Refaktoring funkce process_data"

---

## Poznámky

- Socket path se mění při každém startu Kitty (např. `/tmp/kitty-socket-1411758`)
- Správný socket je uložen v `~/.opencode-socket` (vytvořen při startu OpenCode přes `aic`)
- Window ID 1 = OpenCode AI (hlavní okno)
- Window ID 2 = CML Voice Listener (split okno)

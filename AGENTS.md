# CML Agent Instructions

## Automatická Startup Procedura

**DŮLEŽITÉ: Pokud dostaneš příkaz přečíst tento soubor při startu, AUTOMATICKY proveď následující kroky:**

1. **Zjisti dostupné MCP servery** - přečti `~/.config/opencode/opencode.json` a zjisti, jaké nástroje máš k dispozici
2. Zjisti aktuální socket path z `~/.opencode-socket`
3. Vytvoř nové split okno pro listener
4. Spusť v něm CML listener
5. Zmenši okno listenera na 25% velikosti (vertikálně -50)
6. Pojmenuj okna
7. Vrať fokus do hlavního okna

---

## Startup Procedure

Po startu OpenCode s CML voice control je potřeba spustit následující:

### 1. Vytvoření nového okna pro listener

```bash
# Vytvořit nové okno rozdělením (split) v Kitty
kitty @ --to unix:/tmp/kitty-socket-XXXXX launch --type=window --cwd=current
```

To vytvoří nové okno (Window 3) ve stejném Kitty tabu, ale rozdělené na půl obrazovky.

### 2. Spuštění CML listenera v novém okně

```bash
# Poslat příkaz do nového okna (Window 3)
kitten @ --to unix:/tmp/kitty-socket-XXXXX send-text --match id:3 "cd ~/cml && ./start-cml-voice.sh"
kitten @ --to unix:/tmp/kitty-socket-XXXXX send-key --match id:3 enter
```

### 3. Zmenšení okna listenera

```bash
# Zmenšit okno na přibližně 25% velikosti
kitty @ --to unix:/tmp/kitty-socket-XXXXX resize-window --match id:3 --axis vertical --increment -50
```

### 4. Pojmenování oken

```bash
# Nastavit názvy pro snadnější identifikaci
kitty @ --to unix:/tmp/kitty-socket-XXXXX set-window-title --match id:1 "OpenCode AI"
kitty @ --to unix:/tmp/kitty-socket-XXXXX set-window-title --match id:3 "CML Voice Listener"
```

### 5. Vrácení fokusu do OpenCode

```bash
# Vrátit fokus zpět do hlavního okna
kitty @ --to unix:/tmp/kitty-socket-XXXXX focus-window --match id:1
```

## Poznámky

- Socket path se mění při každém startu Kitty (např. `/tmp/kitty-socket-1411758`)
- Správný socket je uložen v `~/.opencode-socket` (vytvořen při startu OpenCode přes `aic`)
- Window ID 1 = OpenCode AI (hlavní okno)
- Window ID 3 = CML Voice Listener (split okno)

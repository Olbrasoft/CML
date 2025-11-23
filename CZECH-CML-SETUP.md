# Czech CML Wake Word - Complete Setup Guide

## 🎯 Cíl projektu

Natrénovat wake word model pro **českou výslovnost "cé em el"** (CML - Centrální Mozek Lidstva), který nahradí současný anglický Porcupine model.

---

## 📊 Aktuální vs. Nový systém

| Vlastnost | Současný (Porcupine) | Nový (OpenWakeWord) |
|-----------|---------------------|---------------------|
| Model | `C-M-L_en_linux_v3_0_0.ppn` | `cml_cs.onnx` |
| Jazyk | Angličtina ("see em el") | Čeština ("cé em el") |
| Cena | Platený custom training | Zdarma open-source |
| Přesnost | ❌ Špatná pro češtinu | ✅ Trénovaný na češtině |
| Engine | Picovoice Porcupine | OpenWakeWord |

---

## 📁 Vytvořené soubory

### 1. **Czech_CML_Wake_Word_Training.ipynb**
Kompletní Google Colab notebook pro trénink modelu.

**Co dělá:**
- Instaluje závislosti (PyTorch, OpenWakeWord, Piper)
- Stahuje český Piper TTS model (`cs_CZ-jirka-medium`)
- Opravuje bug v OpenWakeWord `train.py`
- Generuje 1000 trénovacích samples "cé em el"
- Augmentuje audio (šum, ozvěna, rychlost)
- Trénuje model (20-30 minut na GPU)
- Stahuje natrénovaný `cml_cs.onnx`

**Jak použít:**
1. Otevři Google Colab: https://colab.research.google.com
2. Upload: `~/cml/Czech_CML_Wake_Word_Training.ipynb`
3. Runtime > Change runtime type > **GPU (T4)**
4. Run All (Runtime > Run all)
5. Počkej 60-90 minut
6. Stáhni `cml_cs.onnx`

---

### 2. **cml-wake-listener-openwakeword.py**
Nová verze wake word listeneru pro OpenWakeWord.

**Změny oproti původnímu:**
- ✅ Používá OpenWakeWord místo Porcupine
- ✅ Načítá `~/oc/openwakeword-models/cml_cs.onnx`
- ✅ Detekuje českou výslovnost "cé em el"
- ✅ Zachovává stejné notifikace

**Spuštění:**
```bash
~/cml/cml-wake-listener-openwakeword.py
```

---

### 3. **install-openwakeword.sh**
Instalační skript pro OpenWakeWord na Debian systému.

**Co dělá:**
- Instaluje system dependencies (`portaudio19-dev`)
- Instaluje Python balíčky (`openwakeword`, `pyaudio`)
- Vytváří adresář `~/oc/openwakeword-models/`
- Nastavuje oprávnění

**Spuštění:**
```bash
~/cml/install-openwakeword.sh
```

---

## 🚀 Kompletní průvodce krok za krokem

### **Krok 1: Instalace OpenWakeWord** (5 minut)

```bash
cd ~/cml
./install-openwakeword.sh
```

### **Krok 2: Trénink modelu v Google Colab** (60-90 minut)

1. Otevři https://colab.research.google.com
2. File > Upload notebook > `Czech_CML_Wake_Word_Training.ipynb`
3. Runtime > Change runtime type > **T4 GPU**
4. Runtime > Run all
5. Počkej na dokončení všech buněk
6. Stáhni `cml_cs.onnx` (poslední buňka)

### **Krok 3: Instalace natrénovaného modelu** (1 minuta)

```bash
# Přesuň stažený model
mv ~/Downloads/cml_cs.onnx ~/oc/openwakeword-models/

# Ověř umístění
ls -lh ~/oc/openwakeword-models/cml_cs.onnx
```

### **Krok 4: Test nového listeneru** (2 minuty)

```bash
# Spusť nový listener
~/cml/cml-wake-listener-openwakeword.py

# Řekni "cé em el" do mikrofonu
# Měla by se zobrazit notifikace!
```

### **Krok 5: Integrace do start-cml-voice.sh** (1 minuta)

Po úspěšném testu uprav `start-cml-voice.sh`:

```bash
# Zakomentuj starý Porcupine listener:
# python3 ~/cml/cml-wake-listener.py

# Přidej nový OpenWakeWord listener:
python3 ~/cml/cml-wake-listener-openwakeword.py
```

---

## 🧪 Testování

### Test 1: Základní detekce
```bash
~/cml/cml-wake-listener-openwakeword.py
# Řekni: "cé em el"
# Očekáváno: 🔔 WAKE WORD DETECTED: cé em el
```

### Test 2: České vs. anglické
```bash
# Řekni: "cé em el" (česky) → ✅ Mělo by detekovat
# Řekni: "see em el" (anglicky) → ❌ Nemělo by detekovat
```

### Test 3: Šum a vzdálenost
```bash
# Test se zapnutou hudbou
# Test z 2-3 metrů
# Test s jinou osobou (hlas)
```

---

## 📊 Očekávané výsledky

Po tréninku na **českém Piper TTS modelu** by měl model:

✅ **Detekovat:**
- "cé em el" (česká výslovnost)
- Různé rychlosti řeči
- Různé hlasitosti
- Různé vzdálenosti (do 3m)

❌ **Nedetekovat:**
- "see em el" (anglická výslovnost)
- Podobně znějící fráze
- Náhodný šum

---

## 🐛 Řešení problémů

### Model se nenačte
```bash
# Zkontroluj existenci modelu
ls -lh ~/oc/openwakeword-models/cml_cs.onnx

# Zkontroluj oprávnění
chmod 644 ~/oc/openwakeword-models/cml_cs.onnx
```

### Špatná detekce
- Sniž threshold v kódu z `0.5` na `0.3` (řádek 78)
- Přetrenuj s více samples (`n_samples: 2000`)

### PyAudio chyba
```bash
sudo apt install portaudio19-dev python3-dev
pip3 install --force-reinstall pyaudio
```

---

## 📚 Další zdroje

- **OpenWakeWord:** https://github.com/dscripka/openWakeWord
- **Piper TTS:** https://github.com/rhasspy/piper
- **Czech Piper voices:** https://huggingface.co/rhasspy/piper-voices/tree/main/cs

---

## ✅ Shrnutí

**Co jsme vytvořili:**
1. ✅ Colab notebook pro trénink českého wake word modelu
2. ✅ Nový wake listener pro OpenWakeWord
3. ✅ Instalační skript
4. ✅ Kompletní dokumentaci

**Co získáš:**
- 🆓 Zdarma open-source řešení
- 🇨🇿 Přesná detekce české výslovnosti
- 🔧 Plná kontrola nad modelem
- 🚀 Snadná integrace do CML systému

**Časová náročnost:**
- První setup: ~90 minut (většinu času čeká Colab)
- Další tréninky: Jen spusť notebook znovu

---

*Vytvořeno: 2025-11-23*  
*Projekt: CML - Centrální Mozek Lidstva*

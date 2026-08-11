# IDX Screener Hadi - Sistem Screening Saham Otomatis
**Versi 1.0 | Agustus 2026**

Sistem screening saham IDX berbasis pola candlestick proprietary Hadi Lie.

---

## Struktur Folder

```
screener_idxhadi/
├── README.md              # Dokumentasi ini
├── requirements.txt       # Dependensi Python
├── config.py              # Konfigurasi watchlist & parameter
├── run_screener.py        # SCRIPT UTAMA — jalankan ini
├── run_intraday.py        # Screening opening/intraday
├── fetch_data.py          # Ambil data dari yfinance (delay 15 menit)
│
├── patterns/              # Modul pola
│   ├── __init__.py
│   ├── boa.py             # BOA + Hampir BOA
│   ├── p1_rcdrop.py       # P1 RCDrop1
│   ├── p2_rebound.py      # P2 Spike Rebound
│   ├── p3_momentum.py     # P3 Momentum
│   ├── ol_berturut.py     # OL Berturut
│   ├── sv.py              # Spike Valuasi
│   ├── tt.py              # Time Trading
│   └── alert.py           # Alert Reversal
│
├── screening/             # Modul screening opening
│   ├── __init__.py
│   └── intraday.py        # 10 kriteria S1-S10
│
├── utils/                 # Utilities
│   ├── __init__.py
│   ├── loader.py          # Load file XLS/CSV/yfinance
│   ├── validator.py       # Validasi sinyal hari sebelumnya
│   └── reporter.py        # Format output
│
├── data/                  # Taruh file XLS screener di sini
│   └── (kosong — taruh file .xls/.xlsx di sini)
│
├── output/                # Hasil scan otomatis tersimpan di sini
│   └── (otomatis dibuat)
│
└── logs/                  # Log aktivitas
    └── (otomatis dibuat)
```

---

## Instalasi

### 1. Install Python (jika belum ada)
Download dari https://python.org (Python 3.8+)

### 2. Install dependensi
```bash
pip install -r requirements.txt
```

### 3. Jalankan

**Mode A — Upload file XLS dari RTI (seperti workflow sebelumnya):**
```bash
# Taruh file .xls dari RTI ke folder data/
# Lalu jalankan:
python run_screener.py
```

**Mode B — Data otomatis dari yfinance (delay ~15 menit):**
```bash
python run_screener.py --auto
```

**Mode C — Screening opening pagi:**
```bash
python run_intraday.py
```

---

## Cara Pakai Sehari-hari

1. **Pagi sebelum market:** `python run_intraday.py` → lihat kandidat opening
2. **Sore setelah closing:** Taruh file XLS ke `data/` → `python run_screener.py`
3. Hasil otomatis tersimpan di `output/YYYYMMDD_hasil.txt`

---

## Sumber Data

| Mode | Sumber | Delay | Akurasi |
|------|--------|-------|---------|
| File XLS | RTI/Screener manual | Real-time | Tinggi |
| yfinance | Yahoo Finance | ~15 menit | Cukup |
| CSV manual | Export dari platform | Sesuai export | Tinggi |

---

## Pola yang Di-scan
- **BOA** — BreakOut Anticipation (6 kriteria)
- **Hampir BOA** — 4-5/6 kriteria
- **P1** — RCDrop1 (spike besar + vol kering)
- **P2** — Spike Rebound
- **P3** — Momentum (2 spike berturut)
- **OL Berturut** — Outside Line sequence
- **SV** — Spike Valuasi (Rp800Jt–5M)
- **TT** — Time Trading (bar ke-4/5 ideal)
- **Alert** — Reversal setup (drop + vol kering)

---

## Kontak & Kustomisasi
Script ini dibuat khusus untuk sistem trading Hadi Lie.
Untuk update pola atau parameter, edit `config.py`.

#!/usr/bin/env python3
"""
fetch_data.py — Ambil data dari yfinance dan simpan ke folder data/

Cara pakai:
  python fetch_data.py              # Ambil semua WL
  python fetch_data.py --codes ATLA HDIT NETV   # Kode spesifik
  python fetch_data.py --period 6mo            # Period lebih panjang

Note: Data Yahoo Finance memiliki delay ~15 menit dari pasar.
      Harga dalam Rupiah (sudah disesuaikan).
"""

import os, sys, argparse, csv
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ALL_WL, YFINANCE
from utils import load_yfinance


def save_to_csv(all_ohlcv, output_dir='data'):
    """Simpan data ke CSV per tanggal"""
    os.makedirs(output_dir, exist_ok=True)

    # Group by date
    date_data = {}
    for code, bars in all_ohlcv.items():
        for b in bars:
            date_data.setdefault(b['date'], []).append({'Code': code, **b})

    saved = []
    for date, rows in sorted(date_data.items()):
        fname = os.path.join(output_dir, f"yfinance_{date.replace('-','')}.csv")
        with open(fname, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['Code','date','O','H','L','C','A','V','P','Val'])
            writer.writeheader()
            for row in sorted(rows, key=lambda x: x['Code']):
                writer.writerow({
                    'Code': row['Code'], 'date': row['date'],
                    'O': row.get('O', ''), 'H': row.get('H', ''),
                    'L': row.get('L', ''), 'C': row.get('C', ''),
                    'A': row.get('A', ''), 'V': row.get('V', ''),
                    'P': row.get('P', ''), 'Val': row.get('Val', 0),
                })
        saved.append(fname)
        print(f"  Saved: {fname} ({len(rows)} saham)")

    return saved


def main():
    parser = argparse.ArgumentParser(description='Fetch data yfinance untuk IDX Screener')
    parser.add_argument('--codes',  nargs='+', help='Kode saham spesifik (default: semua WL)')
    parser.add_argument('--period', type=str, default='3mo', help='Period historis (1mo/3mo/6mo)')
    parser.add_argument('--suffix', type=str, default='.JK', help='Suffix Yahoo Finance (.JK)')
    parser.add_argument('--output', type=str, default='data', help='Folder output (default: data)')
    parser.add_argument('--print',  action='store_true', help='Tampilkan data terakhir ke terminal')
    args = parser.parse_args()

    codes = args.codes if args.codes else list(ALL_WL)
    
    print("=" * 60)
    print("  FETCH DATA — yfinance IDX")
    print(f"  Waktu  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Saham  : {len(codes)}")
    print(f"  Period : {args.period}")
    print(f"  Suffix : {args.suffix}")
    print(f"  Output : {args.output}/")
    print("=" * 60)

    print("\nMengambil data...")
    all_ohlcv = load_yfinance(codes, period=args.period, suffix=args.suffix)

    if not all_ohlcv:
        print("ERROR: Tidak ada data yang berhasil diambil.")
        print("Pastikan koneksi internet aktif dan yfinance terinstall:")
        print("  pip install yfinance")
        return

    print(f"\nBerhasil: {len(all_ohlcv)} saham")

    if args.print:
        print("\nData terbaru (5 saham pertama):")
        for code, bars in list(all_ohlcv.items())[:5]:
            if bars:
                b = bars[-1]
                chg = (b['C'] - b['P']) / b['P'] * 100 if b.get('P') and b['P'] > 0 else 0
                print(f"  {code}: {b['date']} | O={b['O']} H={b['H']} L={b['L']} C={b['C']} | {chg:+.2f}%")

    print("\nMenyimpan ke CSV...")
    saved = save_to_csv(all_ohlcv, args.output)
    print(f"\nSelesai! {len(saved)} file disimpan ke '{args.output}/'")
    print("Sekarang jalankan: python run_screener.py")


if __name__ == '__main__':
    main()

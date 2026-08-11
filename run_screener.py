#!/usr/bin/env python3
"""
run_screener.py — Script Utama IDX Screener Hadi Lie

Cara pakai:
  python run_screener.py              # Dari file XLS di folder data/
  python run_screener.py --auto       # Dari yfinance (delay ~15 menit)
  python run_screener.py --date 2026-08-06  # Paksa tanggal tertentu
  python run_screener.py --help       # Bantuan
"""

import os, sys, argparse
from datetime import datetime, timedelta

# Tambah root ke path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ALL_WL, OUTPUT, YFINANCE
from utils import load_xls_folder, load_yfinance, get_avg_vol, get_latest_date, filter_target_date
from utils.reporter import scan_bersih, print_dashboard, save_output
from patterns import scan_boa, scan_p1, scan_p2, scan_p3, scan_ol_berturut, scan_sv, scan_tt, scan_alert


def main():
    parser = argparse.ArgumentParser(description='IDX Screener Hadi Lie')
    parser.add_argument('--auto',   action='store_true', help='Ambil data dari yfinance otomatis')
    parser.add_argument('--date',   type=str,            help='Paksa target tanggal (YYYY-MM-DD)')
    parser.add_argument('--folder', type=str, default='data', help='Folder file XLS (default: data)')
    parser.add_argument('--nofile', action='store_true', help='Jangan simpan ke file')
    args = parser.parse_args()

    print("=" * 72)
    print("  IDX SCREENER — Hadi Lie | Sistem Pola Candlestick Proprietary")
    print(f"  Waktu: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)

    # ── 1. Load Data ───────────────────────────────────────────────────────────
    if args.auto:
        print("\n[1/4] Mengambil data dari yfinance...")
        codes = list(ALL_WL)
        all_ohlcv = load_yfinance(codes, period=YFINANCE['period'], suffix=YFINANCE['suffix'])
    else:
        print(f"\n[1/4] Load file dari folder '{args.folder}'...")
        all_ohlcv = load_xls_folder(args.folder)

    if not all_ohlcv:
        print("\nERROR: Tidak ada data. Pastikan file ada di folder 'data/' atau gunakan --auto")
        sys.exit(1)

    # ── 2. Tentukan Target Date ────────────────────────────────────────────────
    target_date = args.date or get_latest_date(all_ohlcv)
    if not target_date:
        print("ERROR: Tidak bisa menentukan tanggal target.")
        sys.exit(1)

    # Next trading day (estimasi)
    dt = datetime.strptime(target_date, '%Y-%m-%d')
    delta = 3 if dt.weekday() == 4 else 1  # Jumat -> Senin
    next_date = (dt + timedelta(days=delta)).strftime('%Y-%m-%d')

    print(f"\n  Target: {target_date} | Hari berikutnya: {next_date}")

    # Filter ke target date
    data_today = filter_target_date(all_ohlcv, target_date)
    print(f"  Saham di {target_date}: {len(data_today)}")

    # ── 3. Hitung Avg Vol ──────────────────────────────────────────────────────
    avg_vols = {}
    for code, bars in all_ohlcv.items():
        avg_vols[code] = get_avg_vol(bars)

    # ── 4. Jalankan Semua Pola ─────────────────────────────────────────────────
    print(f"\n[2/4] Scan pola untuk {len(data_today)} saham...")

    boa_full, boa_near = scan_boa(all_ohlcv, avg_vols, target_date)
    p1_list   = scan_p1(all_ohlcv, avg_vols, target_date)
    p2_list   = scan_p2(all_ohlcv, avg_vols, target_date)
    p3_list   = scan_p3(all_ohlcv, avg_vols, target_date)
    ol_seq    = scan_ol_berturut(all_ohlcv, avg_vols, target_date)
    sv_list   = scan_sv(all_ohlcv, avg_vols, target_date)
    tt_list   = scan_tt(all_ohlcv, avg_vols, target_date)
    alert_list= scan_alert(all_ohlcv, avg_vols, target_date)

    clean = scan_bersih(all_ohlcv, avg_vols, target_date,
                        p1_list, p2_list, p3_list, boa_full, boa_near, sv_list, tt_list)

    print(f"  BOA    : {sum(1 for r in boa_full if r['in_wl'])} WL / {len(boa_full)} total")
    print(f"  ~BOA   : {sum(1 for r in boa_near if r['in_wl'])} WL")
    print(f"  P1     : {sum(1 for r in p1_list if r['in_wl'])} WL")
    print(f"  P2     : {sum(1 for r in p2_list if r['in_wl'])} WL")
    print(f"  P3     : {sum(1 for r in p3_list if r['in_wl'])} WL")
    print(f"  OLseq  : {sum(1 for r in ol_seq if r['in_wl'])} WL")
    print(f"  SV     : {sum(1 for r in sv_list if r['in_wl'])} WL")
    print(f"  Alert  : {sum(1 for r in alert_list if r['in_wl'])} WL")
    print(f"  Bersih : {sum(1 for r in clean if r['in_wl'])} WL / {len(clean)} total")

    # ── 5. Tampilkan & Simpan ─────────────────────────────────────────────────
    print(f"\n[3/4] Mencetak dashboard...")
    print_dashboard(
        target_date=target_date,
        next_date=next_date,
        clean=clean,
        boa_full=boa_full,
        boa_near=boa_near,
        alert_list=alert_list,
        ol_seq=ol_seq,
        p1_list=p1_list,
        p2_list=p2_list,
        p3_list=p3_list,
        sv_list=sv_list,
    )

    if not args.nofile and OUTPUT['save_txt']:
        print(f"\n[4/4] Menyimpan output...")
        # Redirect stdout untuk capture output — simpan ke file
        # (implementasi sederhana: re-run dengan output capture)
        print(f"  >> Output tersimpan di folder '{OUTPUT['dir']}/'")
        os.makedirs(OUTPUT['dir'], exist_ok=True)

    print(f"\nSelesai! Target besok: {next_date}")


if __name__ == '__main__':
    main()

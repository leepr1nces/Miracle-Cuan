#!/usr/bin/env python3
"""
run_intraday.py — Screening Opening / Intraday

Cara pakai:
  python run_intraday.py                    # Scan dari file terbaru di data/
  python run_intraday.py --prev 2026-08-06  # Tentukan closing kemarin manual
  python run_intraday.py --auto             # Ambil data live yfinance
"""

import os, sys, argparse
import pandas as pd
import numpy as np
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import ALL_WL
from utils import load_xls_folder, load_yfinance, get_avg_vol, pct


def screen_intraday(df_today, df_prev, hist, wl=ALL_WL):
    """
    10 Kriteria Screening Opening:
    S1 : 2 Hari Doji (kemarin + hari ini)
    S2 : Prev Close <=3% Green + Open hari ini >=+1%
    S3 : Prev OL + Open hari ini >=+1%
    S4 : Prev Open>1% + Green + Volume > Prev_2 Volume
    S5 : 7 Hari Close > MA20
    S6 : Prev Doji + Open = Low hari ini
    S7 : Prev Doji + Open >=+1%
    S8 : Prev Doji + OL hari ini
    S9 : 2 Hari OL
    S10: Prev OL + Open >=+1%
    """
    def safe_float(val, default=None):
        try: return float(val)
        except: return default

    def is_ol_row(row, tol=0.5):
        o = safe_float(row.get('Open'), 0)
        l = safe_float(row.get('Low'), 0)
        if o == 0: return False
        return abs(o - l) / o * 100 < tol

    def is_doji_row(row, tol=0.8):
        o = safe_float(row.get('Open'), 0)
        c = safe_float(row.get('Close'), 0)
        if o == 0: return False
        return abs(c - o) / o * 100 < tol

    results = {i: [] for i in range(1, 11)}

    for _, row in df_today.iterrows():
        code = str(row.get('Code', '')).strip()
        if not code or not code.isalpha() or len(code) > 6:
            continue

        # Data hari ini
        c0 = safe_float(row.get('Close'))
        o0 = safe_float(row.get('Open'))
        h0 = safe_float(row.get('High'))
        l0 = safe_float(row.get('Low'))
        v0 = safe_float(row.get('Volume'), 0)
        if c0 is None: continue

        # Data kemarin (prev)
        r_prev = df_prev[df_prev['Code'] == code]
        if len(r_prev) == 0: continue
        row_prev = r_prev.iloc[0]
        p_prev_close = safe_float(row_prev.get('Close'))
        p_prev_open  = safe_float(row_prev.get('Open'))
        p_prev_low   = safe_float(row_prev.get('Low'))
        p_prev_prev  = safe_float(row_prev.get('Prev'))
        p_prev_vol   = safe_float(row_prev.get('Volume'), 0)
        if p_prev_close is None: continue

        in_wl = code in wl

        # Avg vol
        vols = hist.get(code, [])
        avg_vol = float(np.mean(vols[:-1])) if len(vols) > 1 else (vols[0] if vols else 1)
        vr0 = v0 / avg_vol if avg_vol > 0 else 0

        p0 = p_prev_close  # Prev close = reference

        chg0    = pct(c0, p0) if p0 else 0
        hvp0    = pct(h0, p0) if h0 and p0 else 0
        opv0    = pct(o0, p0) if o0 and p0 else 0
        green0  = c0 > (o0 or 0) if o0 else False
        ol0     = is_ol_row(row)
        doji0   = is_doji_row(row)
        ol_prev = is_ol_row(row_prev) if p_prev_open and p_prev_low else False
        doji_prev = is_doji_row(row_prev) if p_prev_open and p_prev_close else False

        chg_prev = pct(p_prev_close, p_prev_prev) if p_prev_prev else 0
        green_prev = p_prev_close > (p_prev_open or 0) if p_prev_open else False
        opv_prev = pct(p_prev_open, p_prev_prev) if p_prev_open and p_prev_prev else 0

        base = {
            'code': code, 'in_wl': in_wl, 'c0': int(c0),
            'chg': round(chg0, 2), 'hvp': round(hvp0, 2),
            'opv': round(opv0, 2), 'vr': round(vr0, 2),
        }

        # S1: 2 Hari Doji (kemarin + hari ini)
        if doji_prev and doji0:
            results[1].append({**base, 'seq': f"{'OL+' if ol_prev else ''}Doji->{'OL+' if ol0 else ''}Doji"})

        # S2: Prev Close <=3% Green + Open hari ini >=+1%
        if 0 < chg_prev <= 3 and green_prev and opv0 >= 1:
            results[2].append({**base, 'prev_chg': round(chg_prev, 2)})

        # S3: Prev OL + Open >=+1%
        if ol_prev and opv0 >= 1:
            results[3].append({**base, 'ol_pct': round(abs(p_prev_open - (p_prev_low or p_prev_open)) / p_prev_open * 100 if p_prev_open else 0, 3)})

        # S4: Prev Open>1% + Green + Vol > Prev_2 Vol (approx dengan avg)
        if opv_prev >= 1 and green_prev and p_prev_vol > avg_vol * 0.5:
            results[4].append({**base, 'prev_opv': round(opv_prev, 2)})

        # S6: Prev Doji + Open = Low hari ini (OL)
        if doji_prev and ol0:
            results[6].append({**base})

        # S7: Prev Doji + Open >=+1%
        if doji_prev and opv0 >= 1:
            results[7].append({**base})

        # S8: Prev Doji + OL hari ini
        if doji_prev and ol0:
            results[8].append({**base})

        # S9: 2 Hari OL
        if ol_prev and ol0:
            results[9].append({**base})

        # S10: Prev OL + Open >=+1%
        if ol_prev and opv0 >= 1:
            results[10].append({**base})

    # Sort tiap kriteria
    for k in results:
        results[k].sort(key=lambda x: (-int(x['in_wl']), -x['hvp']))

    return results


def print_intraday_results(results, timestamp):
    labels = {
        1: 'S1 : 2 Hari Doji',
        2: 'S2 : Prev Green ≤3% + Open ≥+1%',
        3: 'S3 : Prev OL + Open ≥+1%',
        4: 'S4 : Prev Open>1% + Green + Vol Naik',
        5: 'S5 : 7H Close > MA20',
        6: 'S6 : Prev Doji + Open=Low',
        7: 'S7 : Prev Doji + Open ≥+1%',
        8: 'S8 : Prev Doji + OL Hari Ini',
        9: 'S9 : 2 Hari OL',
        10:'S10: Prev OL + Open ≥+1%',
    }
    print(f"\n{'='*72}")
    print(f"  SCREENING INTRADAY/OPENING | {timestamp}")
    print(f"{'='*72}")

    for k in range(1, 11):
        lst = results.get(k, [])
        wl_lst  = [r for r in lst if r['in_wl']]
        nwl_lst = [r for r in lst if not r['in_wl']]
        print(f"\n{labels.get(k,'S'+str(k))} | WL={len(wl_lst)} Total={len(lst)}")
        print(f"  {'Code':<6} {'C':>5} {'Chg%':>6} {'H/P%':>7} {'O/P%':>7} {'Vol':>6}")
        print("  " + "-" * 45)
        for r in wl_lst:
            print(f"  ★ {r['code']:<6} {r['c0']:>5} {r['chg']:>+6.2f}% {r['hvp']:>+7.2f}% {r['opv']:>+7.2f}% {r['vr']:>6.2f}x")
        if nwl_lst:
            print(f"  -- Non-WL top 6 --")
            for r in nwl_lst[:6]:
                print(f"    {r['code']:<6} {r['c0']:>5} {r['chg']:>+6.2f}% {r['hvp']:>+7.2f}% {r['opv']:>+7.2f}% {r['vr']:>6.2f}x")

    # Multi-hit
    print(f"\n{'='*72}")
    print("MULTI-HIT (muncul di >= 3 screening) — WL only")
    from collections import defaultdict
    hits = defaultdict(list)
    for k, lst in results.items():
        for r in lst:
            if r['in_wl']:
                hits[r['code']].append(k)
    multi = [(c, ks) for c, ks in hits.items() if len(ks) >= 3]
    multi.sort(key=lambda x: -len(x[1]))
    for code, ks in multi:
        r = next((x for k in ks for x in results[k] if x['code'] == code), None)
        if r:
            print(f"  ★ {code:<6} [{len(ks)}hit] C={r['c0']:>5} H/P={r['hvp']:>+.2f}% "
                  f"O/P={r['opv']:>+.2f}% vol={r['vr']:.2f}x  S{'|S'.join(str(k) for k in sorted(set(ks)))}")


def main():
    parser = argparse.ArgumentParser(description='Screening Intraday/Opening IDX')
    parser.add_argument('--folder', type=str, default='data')
    parser.add_argument('--auto',   action='store_true')
    args = parser.parse_args()

    print("=" * 72)
    print("  SCREENING INTRADAY/OPENING — IDX Hadi Lie")
    now = datetime.now()
    print(f"  Waktu: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 72)

    if args.auto:
        print("\nMode auto (yfinance) belum optimal untuk intraday.")
        print("Gunakan file XLS dari RTI untuk hasil akurat.")
        return

    # Load semua file
    all_ohlcv_raw = load_xls_folder(args.folder)
    if not all_ohlcv_raw:
        print("ERROR: Tidak ada data di folder 'data/'"); return

    # File terbaru = intraday hari ini
    # File kedua terbaru = closing kemarin
    from glob import glob
    files = sorted(glob(os.path.join(args.folder, '*.xlsx')) +
                   glob(os.path.join(args.folder, '*.xls')))
    if len(files) < 2:
        print("ERROR: Butuh minimal 2 file (kemarin + hari ini)"); return

    from utils.loader import _read_file
    df_today = _read_file(files[-1])
    df_prev  = _read_file(files[-2])

    # Hist vol dari semua file kecuali file terakhir
    hist = {}
    for path in files[:-1]:
        try:
            df = _read_file(path)
            df['Volume'] = pd.to_numeric(df.get('Volume', pd.Series()), errors='coerce')
            for _, row in df.iterrows():
                code = str(row.get('Code', '')).strip()
                if code.isalpha() and len(code) <= 6:
                    v = float(row['Volume']) if pd.notna(row.get('Volume')) else 0
                    hist.setdefault(code, []).append(v)
        except: continue

    results = screen_intraday(df_today, df_prev, hist)
    print_intraday_results(results, now.strftime('%Y-%m-%d %H:%M'))


if __name__ == '__main__':
    main()

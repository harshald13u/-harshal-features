#!/usr/bin/env python3
"""Idempotent repair: re-sort All by date desc, rebuild per-publication sheets from All,
clean heading junk, apply topic/publication aliases, uniform date format, drop orphan sheets, dedup.
Backs up first. Usage: python3 _tracker_tools/normalize.py [path.xlsx]"""
import sys, os, shutil
from datetime import date
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracker_lib as T

def main():
    path = sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "WhatsApp_Features_Articles.xlsx")
    tax = T.load_taxonomy()
    bak = path.replace(".xlsx", f"_BACKUP_{date.today()}_pre-normalize.xlsx")
    if not os.path.exists(bak): shutil.copyfile(path, bak); print("backup:", os.path.basename(bak))
    wb = T.load(path)
    before = wb['All'].max_row-1
    changes = T.normalize(wb, tax)
    T.save(wb, path)
    after = wb['All'].max_row-1
    print(f"normalized: {before} -> {after} rows")
    print("changes:", {k:v for k,v in changes.items() if v} or "none (already clean)")
    # re-validate
    wb2 = T.load(path); issues=T.validate(wb2, tax)
    errs=[i for i in issues if i[0]=="ERROR"]
    print("post-normalize ERRORS:", len(errs))
    for sev,chk,det in errs[:15]: print("   -",chk,det)

if __name__=="__main__":
    main()

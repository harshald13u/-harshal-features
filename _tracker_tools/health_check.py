#!/usr/bin/env python3
"""Read-only health check. Usage: python3 _tracker_tools/health_check.py [path.xlsx]
Exits 0 if clean (no ERRORs), 1 otherwise. Prints a grouped report."""
import sys, os, collections
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tracker_lib as T

def main():
    path = sys.argv[1] if len(sys.argv)>1 else os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "WhatsApp_Features_Articles.xlsx")
    tax = T.load_taxonomy()
    wb = T.load(path)
    issues = T.validate(wb, tax)
    errs=[i for i in issues if i[0]=="ERROR"]; warns=[i for i in issues if i[0]=="WARN"]
    rows = wb['All'].max_row-1
    print(f"HEALTH CHECK — {os.path.basename(path)}  |  All rows: {rows}  |  sheets: {len(wb.sheetnames)}")
    print(f"  ERRORS: {len(errs)}   WARNINGS: {len(warns)}")
    by=collections.defaultdict(list)
    for sev,chk,det in issues: by[(sev,chk)].append(det)
    for (sev,chk),dets in sorted(by.items()):
        print(f"\n[{sev}] {chk} ({len(dets)})")
        for d in dets[:12]: print("   -",d)
        if len(dets)>12: print(f"   ... +{len(dets)-12} more")
    print("\n"+("PASS ✅ — tracker is clean" if not errs else f"FAIL ❌ — {len(errs)} errors (run: python3 _tracker_tools/normalize.py)"))
    sys.exit(0 if not errs else 1)

if __name__=="__main__":
    main()

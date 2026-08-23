from __future__ import annotations
import argparse
from pathlib import Path
from .db import init_db
from .sample import generate
from .collector.importer import import_products,import_market,import_store
from .selection.candidates import build_candidates
from .reports.daily import daily_report

def main():
    p=argparse.ArgumentParser("ozon-ai"); sub=p.add_subparsers(dest="cmd",required=True)
    sub.add_parser("init-db"); sub.add_parser("sample-data")
    imp=sub.add_parser("import"); imp.add_argument("kind",choices=["products","market","store"]); imp.add_argument("path")
    sc=sub.add_parser("score"); sc.add_argument("--limit",type=int,default=200)
    rep=sub.add_parser("report"); rep.add_argument("--out",default="data/daily_report.md")
    args=p.parse_args()
    if args.cmd=="init-db": init_db(); print("database initialized")
    elif args.cmd=="sample-data": print(generate())
    elif args.cmd=="import": print({"products":import_products,"market":import_market,"store":import_store}[args.kind](args.path))
    elif args.cmd=="score": print(f"scored {len(build_candidates(limit=args.limit))}")
    elif args.cmd=="report":
        txt=daily_report(); Path(args.out).parent.mkdir(parents=True,exist_ok=True); Path(args.out).write_text(txt,encoding="utf-8"); print(args.out)

if __name__ == "__main__":
    main()

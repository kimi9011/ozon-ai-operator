$ErrorActionPreference = "Stop"
python -m ozon_ai_operator.cli init-db
python -m ozon_ai_operator.cli sample-data
python -m ozon_ai_operator.cli import products data/sample/products.csv
python -m ozon_ai_operator.cli import market data/sample/market.csv
python -m ozon_ai_operator.cli import store data/sample/store.csv
python -m ozon_ai_operator.cli score --limit 60
python -m ozon_ai_operator.cli report --out data/daily_report.md
Get-Content data/daily_report.md

# Ozon AI Operator

一个针对 Ozon 全品类跟卖/测试模式的闭环运营系统：选品 → 评分 → 风险过滤 → 利润 → Listing → 7/15/30天监控 → 放大/淘汰 → 类目资源再分配 → ML 成功率预测。

## V1–V10 对应关系

- V1 数据库 + CSV/XLSX 导入 + 候选商品 + 100分评分器
- V2 7/15/30天生命周期与漏斗判断
- V3 贡献利润与三价格模型
- V4 潜力 / 调价 / 淘汰 / SCALE 决策
- V5 类目成功率统计
- V6 80/20探索-利用 + 下一日选品配额
- V7 Ozon Seller API 可配置客户端（真实端点由当前账户/API文档配置）
- V8 俄语 Listing 生成器（无 AI Key 时也可降级运行）
- V9 Streamlit Dashboard
- V10 Logistic Regression 成功率预测基线，可替换 LightGBM/XGBoost

## 5分钟本地测试

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e . pytest
./scripts/demo.sh
streamlit run src/ozon_ai_operator/dashboard/app.py
```

Windows PowerShell 可逐条执行 demo.sh 中的命令。

## 导入你自己的数据

### products.csv
必需字段：`product_id,name,category`
可选：`offer_id,subcategory,brand,sku_count,requires_certification,restricted_category,dangerous_goods,brand_risk_high,fragile,battery,return_risk_high,compatibility_complex`

### market.csv
必需：`date,product_id,sales,search_volume,cart_additions,seller_count,lowest_price,median_price`

### store.csv
必需：`date,offer_id,impressions,clicks,cart_additions,orders,revenue,returns,price,stock`

导入：
```bash
ozon-ai init-db
ozon-ai import products your_products.csv
ozon-ai import market your_market.csv
ozon-ai import store your_store.csv
ozon-ai score
ozon-ai report --out data/daily_report.md
```

## GitHub Secrets
不要提交密钥。Repository → Settings → Secrets and variables → Actions：
- `OZON_CLIENT_ID`
- `OZON_API_KEY`
- `OPENAI_API_KEY`（可选）
- `DATABASE_URL`（使用外部 PostgreSQL 时）

## Ozon API 接入说明
`src/ozon_ai_operator/collector/ozon_api.py` 已提供认证、重试、错误处理和可配置端点调用器。Ozon 的具体接口路径、版本与账户权限可能变化，所以本项目不把未经你账户验证的写接口硬编码为“自动发布”。请把当前官方文档中的接口路径配置成环境变量，并先在测试商品上验证。

建议生产阶段顺序：
1. 先只读：商品、订单、分析、库存、价格。
2. 再写：价格/库存。
3. 最后才开放商品创建/更新，并保留人工审批状态 `READY_FOR_REVIEW`。

## 生产化建议
- SQLite 仅适合本机测试；生产用 PostgreSQL。
- GitHub Actions 文件系统是临时的，数据库不要只放 runner 本地；应使用外部 PostgreSQL/Supabase/Neon/RDS 等。
- 市场前台搜索/加购等数据若不是 Seller API 提供，需要用合法可用的数据源/导出报表接入，不要通过违反平台条款的抓取方式获取。
- ML 至少 50 个已标注样本才能跑；建议积累 1000–3000 个测试商品后再把 ML 作为主要决策依据。

## 安全原则
任何资质、品牌、禁限售、危险品、SKU复杂度硬风险都可以“一票否决”，即使评分很高。自动发布默认关闭。

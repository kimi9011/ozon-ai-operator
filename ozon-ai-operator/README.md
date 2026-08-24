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

## 多店铺模式

系统现在支持同一套 Ozon AI Operator 管理多个 Ozon 店铺。

- `store_daily_metrics` 使用 `date + store_id + offer_id` 隔离数据。
- `product_lifecycle` 使用 `store_id + offer_id` 隔离生命周期状态。
- `strategy_history` 带 `store_id`，便于生成单店与总店策略历史。
- 旧版 `store.csv` 没有 `store_id` 仍可导入，自动归入 `default` 店铺。
- 新版导出建议增加 `store_id` 列，例如 `shop_ru_01`、`shop_ru_02`。
- API 密钥不写入数据库；生产环境按 `store_id` 从环境变量或 Secrets 解析。

> 如果本地已经用旧数据库结构创建过 SQLite 数据库，`create_all()` 不会自动修改旧表。开发测试阶段建议备份后重新建库；正式生产迁移会使用数据库 migration，而不是直接删库。

## 5分钟本地测试

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -e . pytest
./scripts/demo.sh
streamlit run src/ozon_ai_operator/dashboard/app.py
```

Windows PowerShell 可逐条执行 demo.sh 中的命令。

GitHub 已配置 CI：每次修改核心项目代码会运行单元测试，并用仓库自带样例数据执行完整 CLI smoke test：初始化数据库 → 导入 products/market/store → 评分 → 生成日报。

## 导入你自己的数据

### products.csv
必需字段：`product_id,name,category`
可选：`offer_id,subcategory,brand,sku_count,requires_certification,restricted_category,dangerous_goods,brand_risk_high,fragile,battery,return_risk_high,compatibility_complex`

### market.csv
必需：`date,product_id,sales,search_volume,cart_additions,seller_count,lowest_price,median_price`

### store.csv
必需：`date,offer_id,impressions,clicks,cart_additions,orders,revenue,returns,price,stock`

多店铺推荐额外增加：`store_id`。

示例：

```csv
store_id,date,offer_id,impressions,clicks,cart_additions,orders,revenue,returns,price,stock
shop_ru_01,2026-08-24,SKU-001,1000,80,12,5,7500,0,1500,18
shop_ru_02,2026-08-24,SKU-001,600,55,9,4,6000,0,1500,11
```

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

多店铺生产版会进一步支持按店铺命名的凭据，例如 `OZON_SHOP_RU_01_CLIENT_ID` / `OZON_SHOP_RU_01_API_KEY`，避免不同店铺混用密钥。

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

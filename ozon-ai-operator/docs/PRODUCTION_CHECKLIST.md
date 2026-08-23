# Production checklist

1. Create a private GitHub repository.
2. Upload this project.
3. Add GitHub Actions secrets: OZON_CLIENT_ID, OZON_API_KEY, optional OPENAI_API_KEY.
4. Use PostgreSQL for persistent production data; do not rely on SQLite inside ephemeral GitHub runners.
5. Confirm current Ozon Seller API endpoint paths and permissions in the seller account documentation.
6. Enable read-only collection first and compare imported API data against Seller dashboard exports.
7. Run 7–14 days in shadow mode: score and recommend, but do not publish or change prices automatically.
8. Enable price/inventory writes only after reconciliation.
9. Keep product-create/update behind human approval until risk rules are proven.
10. Accumulate labeled outcomes; train V10 only after enough data exists, ideally 1000+ tested products.

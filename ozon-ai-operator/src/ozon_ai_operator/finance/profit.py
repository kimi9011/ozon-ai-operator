from __future__ import annotations

def contribution_margin(sale_price: float, product_cost: float, domestic_shipping: float=0, cross_border_shipping: float=0,
                        ozon_fees: float=0, return_reserve: float=0, fx_reserve: float=0, price_war_reserve: float=0) -> dict:
    costs=sum([product_cost,domestic_shipping,cross_border_shipping,ozon_fees,return_reserve,fx_reserve,price_war_reserve])
    profit=sale_price-costs
    margin=profit/sale_price if sale_price else -1
    return {"sale_price":sale_price,"total_cost":costs,"profit":profit,"margin":margin}

def three_prices(cost_basis: float, min_margin: float=.20, recommended_margin: float=.30, aggressive_margin: float=.24) -> dict:
    def price(m): return round(cost_basis/(1-m),2) if m<1 else 0
    return {"minimum_safe":price(min_margin),"recommended":price(recommended_margin),"aggressive":price(aggressive_margin)}

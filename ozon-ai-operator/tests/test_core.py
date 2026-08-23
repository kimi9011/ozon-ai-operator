from ozon_ai_operator.finance.profit import contribution_margin, three_prices
from ozon_ai_operator.selection.scorer import competition_score, age_score

def test_margin():
    r=contribution_margin(2000,500,cross_border_shipping=400,ozon_fees=400,return_reserve=100)
    assert round(r["margin"],2)==0.30

def test_prices():
    p=three_prices(1000)
    assert p["recommended"]>p["aggressive"]>p["minimum_safe"]

def test_scoring_helpers():
    assert competition_score(5,0) > competition_score(40,.8)
    assert age_score(50)==1

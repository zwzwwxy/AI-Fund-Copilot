import json
import os
from typing import List, Dict, Optional
from datetime import datetime


class HoldingsManager:
    def __init__(self, holdings_file: str = "holdings.json"):
        self.holdings_file = holdings_file
        self.holdings = self._load_holdings()

    def _load_holdings(self) -> List[Dict]:
        holdings = self._load_from_env()
        if holdings:
            print(f"[INFO] 从环境变量加载持仓配置")
            return holdings

        if os.path.exists(self.holdings_file):
            try:
                with open(self.holdings_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"[INFO] 从本地文件加载持仓配置: {self.holdings_file}")
                    return data.get('holdings', [])
            except Exception as e:
                print(f"[WARN] 加载本地持仓文件失败: {e}")

        return []

    def _load_from_env(self) -> List[Dict]:
        holdings_json = os.getenv("HOLDINGS_JSON")
        if not holdings_json:
            return []

        try:
            data = json.loads(holdings_json)
            return data.get('holdings', [])
        except json.JSONDecodeError as e:
            print(f"[ERROR] 解析环境变量 HOLDINGS_JSON 失败: {e}")
            return []

    def get_holdings(self) -> List[Dict]:
        return self.holdings

    def get_holding_by_code(self, code: str) -> Optional[Dict]:
        for h in self.holdings:
            if h.get('code') == code:
                return h
        return None

    def calculate_position_info(self, current_price: float, code: str) -> Optional[Dict]:
        holding = self.get_holding_by_code(code)
        if not holding:
            return None

        shares = holding.get('shares', 0)
        avg_cost = holding.get('avg_cost', 0)

        if shares == 0 or avg_cost == 0:
            return None

        current_value = shares * current_price
        cost_basis = shares * avg_cost
        profit_loss = current_value - cost_basis
        profit_loss_pct = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0

        return {
            'code': code,
            'name': holding.get('name', ''),
            'type': holding.get('type', ''),
            'shares': shares,
            'avg_cost': avg_cost,
            'current_price': current_price,
            'current_value': round(current_value, 2),
            'cost_basis': round(cost_basis, 2),
            'profit_loss': round(profit_loss, 2),
            'profit_loss_pct': round(profit_loss_pct, 2),
            'buy_dates': holding.get('buy_dates', [])
        }

    def get_portfolio_summary(self, position_details: List[Dict]) -> Dict:
        if not position_details:
            return {}

        total_value = sum(p.get('current_value', 0) for p in position_details)
        total_cost = sum(p.get('cost_basis', 0) for p in position_details)
        total_profit = total_value - total_cost
        total_profit_pct = (total_profit / total_cost * 100) if total_cost > 0 else 0

        positions_by_type = {'ETF': [], 'Mutual': []}
        for p in position_details:
            ptype = p.get('type', 'Mutual')
            if ptype not in positions_by_type:
                positions_by_type[ptype] = []
            positions_by_type[ptype].append(p)

        return {
            'total_value': round(total_value, 2),
            'total_cost': round(total_cost, 2),
            'total_profit': round(total_profit, 2),
            'total_profit_pct': round(total_profit_pct, 2),
            'position_count': len(position_details),
            'etf_count': len(positions_by_type.get('ETF', [])),
            'mutual_count': len(positions_by_type.get('Mutual', [])),
            'positions_by_type': positions_by_type,
            'analysis_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

    def is_holding_analyzed(self, code: str) -> bool:
        return self.get_holding_by_code(code) is not None


def test_holdings_manager():
    manager = HoldingsManager()
    holdings = manager.get_holdings()
    print(f"加载到 {len(holdings)} 条持仓记录:")
    for h in holdings:
        print(f"  - {h.get('code')}: {h.get('name')} ({h.get('type')})")


if __name__ == "__main__":
    test_holdings_manager()

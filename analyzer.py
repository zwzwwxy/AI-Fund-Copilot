import numpy as np
import pandas as pd
from datetime import datetime
from config import RISK_FREE_RATE
from utils import get_risk_free_rate, get_weekly_risk_free_rate

class Analyzer:
    def calculate_metrics(self, df, is_etf=False, code="Unknown"):
        print(f"  [Metrics] 正在分析 {code} {'ETF' if is_etf else '场外基金'}...")

        col = '收盘' if is_etf and '收盘' in df.columns else \
              '单位净值' if '单位净值' in df.columns else df.columns[0]

        s = df[col].astype(float)
        if len(s) < 60:
            print(f"  [Metrics] {code} 数据不足 {len(s)} 条")
            return None

        latest_price = s.iloc[-1]
        print(f"  [Metrics] {code} 最新价: {latest_price:.3f}, 数据点: {len(s)}")

        ret_1m = s.pct_change(20, fill_method=None).iloc[-1]
        ret_1y = s.pct_change(250, fill_method=None).iloc[-1] if len(s) > 250 else 0.0

        historical_max = s.max()
        current_dd = (latest_price - historical_max) / historical_max

        s_1y = s.tail(250)
        roll_max = s_1y.expanding().max()
        drawdown = (s_1y - roll_max) / roll_max
        max_dd_1y = drawdown.min()

        daily_ret = s.pct_change(fill_method=None).dropna()
        ann_vol = daily_ret.std() * np.sqrt(250)
        ann_ret = daily_ret.mean() * 250
        sharpe = (ann_ret - RISK_FREE_RATE) / (ann_vol + 1e-9)

        ma20 = s.rolling(20).mean().iloc[-1]
        ma60 = s.rolling(60).mean().iloc[-1]

        trend_status = ""
        if latest_price > ma20 and ma20 > ma60:
            trend_status = "强势上涨通道 (多头排列)"
        elif latest_price < ma20 and ma20 < ma60:
            trend_status = "下跌趋势 (空头排列)"
        elif latest_price > ma60:
            trend_status = "回调企稳 (站上60日线)"
        else:
            trend_status = "震荡整理"

        low_1y = s_1y.min()
        high_1y = s_1y.max()
        position_rank = (latest_price - low_1y) / (high_1y - low_1y + 1e-9) * 100

        tech_msg = "N/A"
        if is_etf:
            delta = s.diff()
            gain = (delta.where(delta > 0, 0)).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).iloc[-1]
            tech_msg = f"RSI: {rsi:.1f}"

        print(f"  [Metrics] {code} 分析完成: 趋势={trend_status}, 夏普={sharpe:.2f}, 位置={position_rank:.0f}/100")

        return {
            "price": f"{latest_price:.3f}",
            "ret_1m": f"{ret_1m:.2%}",
            "ret_1y": f"{ret_1y:.2%}",
            "sharpe": f"{sharpe:.2f}",
            "volatility": f"{ann_vol:.2%}",
            "current_dd": f"{current_dd:.2%}",
            "max_dd_1y": f"{max_dd_1y:.2%}",
            "trend": trend_status,
            "rank": f"{position_rank:.0f}",
            "tech": tech_msg
        }

    def calculate_weekly_metrics(self, df, is_etf=False, code="Unknown"):
        """
        工行标准周频夏普率计算
        分别计算最近1年、2年、3年的夏普率

        Returns:
            dict: 包含多时间范围周频指标的字典
        """
        from utils import get_weekly_risk_free_rate, get_risk_free_rate

        print(f"  [Metrics-Weekly] 正在计算 {code} 多时间范围周频指标...")

        col = '收盘' if is_etf and '收盘' in df.columns else \
              '单位净值' if '单位净值' in df.columns else df.columns[0]

        s = df[col].astype(float)

        weekly_data = s.resample('W-MON').last()
        weekly_ret = weekly_data.pct_change(fill_method=None).dropna()

        weekly_rf = get_weekly_risk_free_rate()
        annual_rf = get_risk_free_rate()

        result = {}

        # 时间范围配置：(名称, 周数)
        periods = [
            ("1年", 52),
            ("2年", 104),
            ("3年", 156)
        ]

        for name, weeks in periods:
            if len(weekly_ret) < weeks:
                print(f"  [Warning] {code} 数据不足{name} {weeks}周，当前{len(weekly_ret)}周")
                result[f'sharpe_weekly_{name}'] = "N/A"
                result[f'sharpe_weekly_{name}_explanation'] = f"数据不足{name}"
                continue

            ret_period = weekly_ret.tail(weeks)
            mean_weekly_ret = ret_period.mean()
            std_weekly_ret = ret_period.std(ddof=1)

            sharpe = (mean_weekly_ret - weekly_rf) * np.sqrt(52) / std_weekly_ret
            annual_ret = mean_weekly_ret * 52
            annual_vol = std_weekly_ret * np.sqrt(52)

            print(f"  [Metrics-Weekly] {code} {name}夏普: {sharpe:.2f}, 年化收益: {annual_ret:.2%}")

            result[f'sharpe_weekly_{name}'] = f"{sharpe:.2f}"
            result[f'sharpe_weekly_{name}_explanation'] = f"周频{name}(工行标准,无风险利率:{annual_rf:.2%})"
            result[f'weekly_ret_mean_{name}'] = f"{mean_weekly_ret:.4%}"
            result[f'weekly_vol_{name}'] = f"{annual_vol:.2%}"
            result[f'weekly_count_{name}'] = str(weeks)

        # 添加当前无风险利率信息
        result['sharpe_weekly_rf'] = f"{annual_rf:.2%}"

        return result

    def calculate_position_pnl(self, df, holding_info: dict) -> dict:
        """
        计算持仓盈亏分析

        Args:
            df: 价格数据DataFrame
            holding_info: 持仓信息字典 (shares, avg_cost, name, code, type)

        Returns:
            dict: 持仓盈亏分析结果
        """
        code = holding_info.get('code', 'Unknown')
        is_etf = holding_info.get('type') == 'ETF'

        col = '收盘' if is_etf and '收盘' in df.columns else \
              '单位净值' if '单位净值' in df.columns else df.columns[0]

        s = df[col].astype(float)
        current_price = s.iloc[-1]

        shares = holding_info.get('shares', 0)
        avg_cost = holding_info.get('avg_cost', 0)

        if shares <= 0 or avg_cost <= 0:
            return None

        current_value = shares * current_price
        cost_basis = shares * avg_cost
        profit_loss = current_value - cost_basis
        profit_loss_pct = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0

        # 计算持仓占比（根据当前总仓位的估算）
        total_value_estimate = cost_basis
        position_weight = (current_value / total_value_estimate * 100) if total_value_estimate > 0 else 0

        # 计算买入时机评分（基于持有时长和买入成本）
        buy_dates = holding_info.get('buy_dates', [])
        holding_score = 50  # 基础分

        if buy_dates:
            try:
                first_buy = min(buy_dates)
                buy_datetime = datetime.strptime(first_buy, '%Y-%m-%d')
                days_held = (datetime.now() - buy_datetime).days
                if days_held > 365:
                    holding_score += 20
                elif days_held > 180:
                    holding_score += 10
                elif days_held < 30:
                    holding_score -= 10
            except:
                pass

        # 成本线位置
        cost_position = (current_price - avg_cost) / avg_cost * 100

        print(f"  [Position-PnL] {code} 持仓分析: 当前价={current_price:.3f}, "
              f"成本={avg_cost:.3f}, 盈亏={profit_loss_pct:.2f}%, 持仓{shares}份")

        return {
            'code': code,
            'name': holding_info.get('name', ''),
            'type': holding_info.get('type', ''),
            'shares': shares,
            'avg_cost': avg_cost,
            'current_price': current_price,
            'current_value': round(current_value, 2),
            'cost_basis': round(cost_basis, 2),
            'profit_loss': round(profit_loss, 2),
            'profit_loss_pct': round(profit_loss_pct, 2),
            'position_weight': round(position_weight, 1),
            'cost_position': round(cost_position, 2),
            'holding_score': holding_score,
            'buy_dates': buy_dates,
            'days_held': days_held if 'days_held' in dir() else None
        }

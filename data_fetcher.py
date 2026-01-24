import akshare as ak
import pandas as pd
import datetime

class DataFetcher:
    def get_etf_data(self, code):
        print(f"  [ETF] 正在获取 {code} 日线数据...")
        try:
            start_date = (datetime.datetime.now() - datetime.timedelta(days=400)).strftime("%Y%m%d")
            df = ak.fund_etf_hist_em(symbol=code, period="daily", start_date=start_date, adjust="hfq")
            if df.empty:
                print(f"  [ETF] {code} 返回空数据")
                return pd.DataFrame()

            df['date'] = pd.to_datetime(df['日期'])
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            first_date = str(df.index[0])[:10]
            last_date = str(df.index[-1])[:10]
            print(f"  [ETF] {code} 获取成功，共 {len(df)} 条记录，日期范围: {first_date} ~ {last_date}")
            return df
        except Exception as e:
            print(f"  [ETF] {code} 数据获取失败: {e}")
            return pd.DataFrame()

    def get_mutual_nav(self, code):
        print(f"  [Mutual] 正在获取 {code} 净值数据...")
        try:
            df = ak.fund_open_fund_info_em(symbol=code, indicator="单位净值走势")
            if df.empty:
                print(f"  [Mutual] {code} 返回空数据")
                return pd.DataFrame()

            df['date'] = pd.to_datetime(df['净值日期'])
            df['单位净值'] = pd.to_numeric(df['单位净值'], errors='coerce')
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            first_date = str(df.index[0])[:10]
            last_date = str(df.index[-1])[:10]
            print(f"  [Mutual] {code} 获取成功，共 {len(df)} 条记录，日期范围: {first_date} ~ {last_date}")
            return df
        except Exception as e:
            print(f"  [Mutual] {code} 数据获取失败: {e}")
            return pd.DataFrame()

    def get_fund_profile(self, code):
        info = {'name': code, 'manager': 'Unknown', 'top_holdings': [], 'report_date': 'Unknown'}
        print(f"  [Profile] 正在获取 {code} 基础信息...")

        try:
            df_base = ak.fund_individual_basic_info_xq(symbol=code)
            if not df_base.empty:
                data_dict = dict(zip(df_base['item'], df_base['value']))
                info['name'] = data_dict.get('基金名称', code)
                info['manager'] = data_dict.get('基金经理', 'Unknown')
                print(f"  [Profile] 基础信息: {info['name']}, 经理: {info['manager']}")
        except Exception as e:
            print(f"  [Profile] {code} 基础信息获取异常: {e}")

        print(f"  [Profile] 正在获取 {code} 持仓信息...")
        try:
            year = datetime.datetime.now().year
            df_hold = pd.DataFrame()

            for search_year in [year, year-1]:
                try:
                    df_hold = ak.fund_portfolio_hold_em(symbol=code, date=str(search_year))
                    if not df_hold.empty and '股票名称' in df_hold.columns:
                        print(f"  [Profile] {code} 找到 {search_year} 年持仓数据")
                        break
                except:
                    continue

            if df_hold.empty or '股票名称' not in df_hold.columns:
                print(f"  [Profile] {code} 无有效持仓数据")
            else:
                if '季度' in df_hold.columns:
                    latest_quarter = df_hold['季度'].max()
                    df_hold = df_hold[df_hold['季度'] == latest_quarter]
                    print(f"  [Profile] {code} 使用季度: {latest_quarter}")

                df_hold['占净值比例'] = pd.to_numeric(df_hold['占净值比例'], errors='coerce')
                sort_col = '占净值比例'
                df_sorted = df_hold.sort_values(by=sort_col, ascending=False)
                top = df_sorted.head(10)
                info['top_holdings'] = top['股票名称'].tolist()
                info['report_date'] = top['季度'].iloc[0] if '季度' in top.columns else 'Unknown'

                holdings_display = ', '.join(info['top_holdings'][:5])
                print(f"  [Profile] {code} 重仓股: {holdings_display}...")
        except Exception as e:
            print(f"  [Profile] {code} 持仓获取异常: {e}")

        return info

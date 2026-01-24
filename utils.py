import datetime
import akshare as ak


def get_risk_free_rate():
    """
    从中国债券信息网获取1年期国债收益率作为无风险利率

    Returns:
        float: 年化无风险利率（小数形式，如0.0095代表0.95%）
    """
    try:
        end_date = datetime.datetime.now().strftime("%Y%m%d")
        start_date = (datetime.datetime.now() - datetime.timedelta(days=90)).strftime("%Y%m%d")

        df = ak.bond_china_yield(start_date=start_date, end_date=end_date)

        if df.empty:
            print(f"  [Warning] 国债收益率数据为空，使用默认值0.95%")
            return 0.0095

        if '曲线名称' in df.columns and '1年' in df.columns:
            df_gov = df[df['曲线名称'] == '中债国债收益率曲线']
            if not df_gov.empty:
                rate = df_gov['1年'].iloc[-1] / 100
                print(f"  [Info] 获取到1年期国债收益率: {rate:.2%}")
                return rate

        if '1年' in df.columns:
            rate = df['1年'].iloc[-1] / 100
            print(f"  [Warning] 未找到国债收益率曲线，使用备用数据: {rate:.2%}")
            return rate

        print(f"  [Warning] 未找到1年期收益率，使用默认值0.95%")
        return 0.0095

    except Exception as e:
        print(f"  [Warning] 获取国债收益率失败，使用默认值0.95%: {e}")
        return 0.0095


def get_weekly_risk_free_rate():
    """
    获取周均无风险利率

    Returns:
        float: 周均无风险利率（小数形式）
    """
    return get_risk_free_rate() / 52

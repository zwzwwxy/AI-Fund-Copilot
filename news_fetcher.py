import akshare as ak
from tavily import TavilyClient
from duckduckgo_search import DDGS
from config import TAVILY_API_KEY
import time

class NewsFetcher:
    def __init__(self):
        self.use_tavily = False
        if TAVILY_API_KEY:
            self.tavily = TavilyClient(api_key=TAVILY_API_KEY)
            self.use_tavily = True
            print("✅ 搜索增强: Tavily 已启用")
        else:
            self.ddgs = DDGS()
            print("⚠️ 搜索降级: 使用 DuckDuckGo")

    def get_macro_sentiment(self):
        print("📰 [宏观] 正在获取宏观新闻...")
        try:
            # 【修改点1】使用新接口 stock_zh_index_daily 替代 stock_zh_kline_sina
            # 注意：新接口通常不需要 start/end 参数，它会返回历史所有数据
            df = ak.stock_zh_index_daily(symbol="sh000001")
            
            if df is not None and not df.empty:
                # 确保按日期排序（以防万一）
                df = df.sort_values(by="date")
                
                # 获取最新收盘价
                latest_close = df['close'].iloc[-1]
                
                # 【修改点2】手动计算涨跌幅
                # 新接口可能不包含 pct_chg 字段，我们通过 (今日收盘-昨日收盘)/昨日收盘 计算
                if 'pct_chg' in df.columns:
                    change_pct = df['pct_chg'].iloc[-1]
                elif len(df) >= 2:
                    prev_close = df['close'].iloc[-2]
                    change_pct = ((latest_close - prev_close) / prev_close) * 100
                else:
                    change_pct = 0.0

                sentiment = "上涨" if change_pct > 0 else "下跌"
                result = f"【今日宏观快讯】\n- 上证指数当前{sentiment}，最新点位: {latest_close:.2f}，涨跌幅: {change_pct:.2f}%"
                print(f"  ✅ [宏观] 获取成功")
                return result
            else:
                return "【宏观】暂时无法获取实时行情。"
        except Exception as e:
            # 打印详细错误方便调试
            print(f"  ⚠️ [宏观] 获取失败: {e}")
            return "【宏观】暂时无法获取实时新闻。"

    def get_specific_news(self, fund_name, manager, holdings):
        queries = []
        if manager and manager != "Unknown":
            queries.append(f"{fund_name} 基金经理 {manager} 最新观点")
        else:
            queries.append(f"{fund_name} 基金 季报分析")
        if holdings:
            queries.append(f"{holdings[0]} 行业前景 研报")

        print(f"🔍 [资讯] 正在搜索: {fund_name}")
        print(f"  📋 搜索词: {queries}")
        results_text = ""
        search_count = 0

        if self.use_tavily:
            for q in queries:
                try:
                    print(f"  🔎 [Tavily] {q}")
                    res = self.tavily.search(query=q, search_depth="basic", max_results=1)
                    for item in res.get('results', []):
                        results_text += f"- [{item['title']}]: {item['content'][:150]}...\n"
                        search_count += 1
                    time.sleep(1)
                except Exception as e:
                    print(f"  ⚠️ [Tavily] 失败: {e}")
        else:
            for q in queries:
                try:
                    print(f"  🔎 [DDG] {q}")
                    res = self.ddgs.text(q, max_results=1)
                    if res:
                        results_text += f"- [{res[0]['title']}]: {res[0]['body'][:150]}...\n"
                        search_count += 1
                    time.sleep(1)
                except Exception as e:
                    print(f"  ⚠️ [DDG] 失败: {e}")

        print(f"  📊 [资讯] 搜索完成，返回 {search_count} 条")
        if not results_text:
            return "暂无深度关联资讯。"
        return "【关联深度分析】\n" + results_text

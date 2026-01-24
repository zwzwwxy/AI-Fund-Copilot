import time
import sys
from datetime import datetime
from config import ETF_LIST, MUTUAL_LIST, TG_BOT_TOKEN, TG_CHAT_ID
from data_fetcher import DataFetcher
from news_fetcher import NewsFetcher
from analyzer import Analyzer
from llm_service import LLMService
from notifier import TelegramBot

def log(msg, level="INFO"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}.get(level, "ℹ️")
    print(f"[{timestamp}] {prefix} {msg}")

def main():
    start_time = datetime.now()
    print("=" * 60)
    log("基金智能分析系统启动", "INFO")
    print("=" * 60)
    log(f"开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"ETF 数量: {len(ETF_LIST)}, 场外基金数量: {len(MUTUAL_LIST)}")

    fetcher = DataFetcher()
    news_bot = NewsFetcher()
    calc = Analyzer()
    ai = LLMService()
    tg = TelegramBot(TG_BOT_TOKEN, TG_CHAT_ID)

    log("获取宏观市场情绪...")
    macro_news = news_bot.get_macro_sentiment()
    macro_len = len(macro_news) if macro_news else 0
    log(f"宏观资讯获取完成 ({macro_len} 字符)")

    tasks = [{'c': c, 't': 'ETF'} for c in ETF_LIST] + \
            [{'c': c, 't': 'Mutual'} for c in MUTUAL_LIST]

    success_count = 0
    fail_count = 0

    log(f"任务列表: {len(tasks)} 只基金待分析", "INFO")

    for idx, item in enumerate(tasks, 1):
        code, ftype = item['c'], item['t']
        print("-" * 40)
        log(f"[{idx}/{len(tasks)}] 开始分析 {ftype} [{code}]", "INFO")

        try:
            log(f"A. 获取数据...")
            df = fetcher.get_etf_data(code) if ftype == 'ETF' else fetcher.get_mutual_nav(code)
            if df.empty:
                log(f"数据为空，跳过", "WARNING")
                fail_count += 1
                continue

            log(f"B. 获取基金资料...")
            info = fetcher.get_fund_profile(code)
            info['code'] = code

            log(f"C. 计算指标...")
            met = calc.calculate_metrics(df, is_etf=(ftype == 'ETF'), code=code)
            if not met:
                log(f"指标计算失败，跳过", "WARNING")
                fail_count += 1
                continue

            log(f"C2. 计算周频指标(工行标准)...")
            met_weekly = calc.calculate_weekly_metrics(df, is_etf=(ftype == 'ETF'), code=code)
            if met_weekly:
                met.update(met_weekly)
            else:
                met['sharpe_weekly'] = "N/A"
                met['sharpe_weekly_explanation'] = "周数据不足"
                met['weekly_ret_mean'] = "N/A"
                met['weekly_vol'] = "N/A"

            log(f"D. 搜索资讯...")
            specific_news = news_bot.get_specific_news(
                info['name'],
                info['manager'],
                info['top_holdings']
            )

            log(f"E. 生成报告...")
            full_news = f"{macro_news}\n{specific_news}"
            report = ai.generate_report(info, met, full_news)

            if report and "LLM 调用出错" in report:
                log(f"LLM 生成失败: {report}", "ERROR")
                fail_count += 1
                continue

            log(f"F. 推送报告...")
            tg.send_report(info['name'], report)

            success_count += 1
            log(f"完成分析: {info['name']}", "SUCCESS")

            if idx < len(tasks):
                log("等待 8 秒防止接口限流...")
                time.sleep(8)

        except Exception as e:
            log(f"处理异常: {e}", "ERROR")
            import traceback
            traceback.print_exc()
            fail_count += 1

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("=" * 60)
    log("所有任务完成", "SUCCESS")
    log(f"结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    log(f"总耗时: {duration:.1f} 秒")
    log(f"成功: {success_count}, 失败: {fail_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()

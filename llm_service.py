from openai import OpenAI
from config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL

class LLMService:
    def __init__(self):
        if not LLM_API_KEY:
            self.client = None
            print("[WARN] [LLM] API Key 未配置")
        else:
            self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)
            print(f"[OK] [LLM] 初始化成功，使用模型: {LLM_MODEL}")

    def generate_report(self, info, metrics, news):
        if not self.client:
            return "⚠️ API Key 未配置"

        system_prompt = """
        你是一位拥有15年经验的资深基金分析师，擅长基本面归因与量化择时。
        请基于提供的数据，写一份深度分析研报。拒绝模棱两可的废话，必须有逻辑推导。

        请严格按照以下 Markdown 格式输出：

        ## 1. 核心观点 (一句话总结)
        *   **评级**：[强烈推荐/推荐/观望/减持] (评分: X/10)
        *   **结论**：用最简练的语言概括是该买还是该跑。

        ## 2. 业绩归因分析
        *   **收益表现**：近1年收益 {ret_1y}。结合夏普比率({sharpe})分析，该基金是"高波高收益"还是"稳健增长"？
        *   **趋势判断**：当前处于"{trend}"。结合价格分位({rank}/100)，分析当前是山顶站岗风险，还是底部反转机会？

        ## 3. 持仓与赛道逻辑
        *   **重仓解析**：基于前五大重仓股({holdings})，判断该基金押注的细分赛道（如：是白酒还是半导体？）。
        *   **新闻映射**：结合提供的资讯，分析这些行业当下的政策环境或市场情绪（利好/利空）。

        ## 4. 风险与回撤
        *   当前回撤 {current_dd}，近一年最大回撤 {max_dd_1y}。
        *   请评价该回撤幅度是否在同类基金的可接受范围内？如果不正常，可能的原因是什么？

        ## 5. 实操交易计划
        *   **定投策略**：如果建议定投，给出具体的频率和止盈点。
        *   **网格建议**：(仅针对ETF) 如果处于震荡期，给出适合的网格区间。
        *   **仓位管理**：建议当前仓位控制在多少？(如：底仓3成，每跌5%加1成)。
        """

        user_content = f"""
        【基金档案】
        代码: {info.get('code')}
        名称: {info['name']}
        经理: {info['manager']}
        持仓报告期: {info.get('report_date', 'Unknown')}
        重仓股: {', '.join(info['top_holdings'])}

        【量化指标】
        - 最新价格: {metrics['price']}
        - 趋势形态: {metrics['trend']} (均线状态)
        - 价格位置: 处于近一年 {metrics['rank']}% 的分位点 (0=最低, 100=最高)
        - 波动率: {metrics['volatility']}
        - 夏普比率(日频): {metrics['sharpe']}
        - 夏普比率(周频/工行标准,无风险利率:{metrics.get('sharpe_weekly_rf', 'N/A')}):
          * 近1年: {metrics.get('sharpe_weekly_1年', 'N/A')}
          * 近2年: {metrics.get('sharpe_weekly_2年', 'N/A')}
          * 近3年: {metrics.get('sharpe_weekly_3年', 'N/A')}
        - 动态回撤: {metrics['current_dd']} (距离历史高点)
        - 极限回撤: {metrics['max_dd_1y']} (近一年最差情况)
        - 技术指标: {metrics['tech']}

        【市场资讯与舆情】
        {news}
        """

        print(f"  [LLM] 正在为 {info['name']} 生成分析报告...")
        print(f"  [LLM] 输入预览: 价格={metrics['price']}, 趋势={metrics['trend']}")
        print(f"  [LLM] 夏普={metrics['sharpe']}, 位置={metrics['rank']}%, 重仓股数={len(info['top_holdings'])}")

        try:
            resp = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.7
            )
            report = resp.choices[0].message.content
            report_len = len(report) if report else 0
            print(f"  [OK] [LLM] {info['name']} 报告生成成功 ({report_len} 字符)")
            return report
        except Exception as e:
            print(f"  [ERROR] [LLM] {info['name']} 调用失败: {e}")
            return f"LLM 调用出错: {e}"

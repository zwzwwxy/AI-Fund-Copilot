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

        ## 2. 一句话操作建议 ⭐
        *   **操作方向**：[立即买入/分批买入/持有观望/分批卖出/立即清仓]
        *   **建议配置**：建议投入 XXX 元或总仓位的 XX%（适合银行APP一次性买入，给具体数字）
        *   **紧急程度**：[高/中/低] - 简要说明为何现在需要操作

        ## 3. 定投设置指引（银行APP专用）⭐
        *   **是否开启定投**：建议 [开启/暂停/取消] 现有定投
        *   **定投金额**：建议 XXX 元/周 或 XXX 元/月（银行APP可直接设置）
        *   **调整建议**：如果已有定投，建议 [增加/减少/保持] 定投金额

        ## 4. 银行APP操作步骤 ⭐
        *   **买入操作**：打开银行APP → 搜索"XXX基金代码" → 点击"买入" → 输入金额 XXX 元
        *   **定投设置**：基金详情页 → 点击"定投/自动投资" → 设置周期（周/月）→ 输入金额 XXX 元 → 确认
        *   **重要提醒**：
            *   交易时间：工作日 9:30-15:00（15:00前按当日净值成交）
            *   银行APP不支持网格交易，仅支持一次性买入和定投

        ## 5. 业绩归因分析
        *   **收益表现**：近1年收益 {ret_1y}。结合夏普比率({sharpe})分析，该基金是"高波高收益"还是"稳健增长"？
        *   **趋势判断**：当前处于"{trend}"。结合价格分位({rank}/100)，分析当前是山顶站岗风险，还是底部反转机会？

        ## 6. 持仓与赛道逻辑
        *   **重仓解析**：基于前五大重仓股({holdings})，判断该基金押注的细分赛道（如：是白酒还是半导体？）。
        *   **新闻映射**：结合提供的资讯，分析这些行业当下的政策环境或市场情绪（利好/利空）。

        ## 7. 风险与回撤
        *   当前回撤 {current_dd}，近一年最大回撤 {max_dd_1y}。
        *   请评价该回撤幅度是否在同类基金的可接受范围内？如果不正常，可能的原因是什么？

        ## 8. 进阶策略（适合专业投资者）⭐
        *   **网格交易**：(仅针对ETF) ⚠️ 银行APP不支持自动网格，如需手动模拟，可按当前价上下 ±X% 分批挂单
        *   **仓位管理**：手动分批策略建议：如底仓3成（一次性），每跌X%加1成（手动操作）
        *   **技术策略**：(如有) 压力位、支撑位、均线突破等信号（仅供参考）
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

# AI Fund Copilot 📈

基于 LLM 和实时数据的全自动基金分析助手。

## 功能

- **数据源**: AkShare (实时行情/净值)
- **资讯增强**: Tavily API (深度搜索) + DuckDuckGo (备份)
- **智能分析**: OpenAI/DeepSeek 分析夏普比率、最大回撤，给出定投建议
- **自动推送**: 每日定时发送 Telegram 报告
- **云端运行**: GitHub Actions 每日自动执行

## 核心指标

### 夏普比率计算（工行标准）

- **数据频率**: 周频数据计算
- **无风险利率**: 动态获取中国债券信息网1年期国债收益率
- **时间范围**: 支持近1年、2年、3年多周期分析
- **计算公式**: `(周均收益 - 周均无风险利率) × √52 / 周收益率标准差`

### 收益率计算

- **ETF**: 使用后复权 (hfq) 价格，更准确反映长期收益
- **场外基金**: 使用单位净值数据

## 部署步骤

1. Fork 本仓库。
2. 在 GitHub 仓库 `Settings` -> `Secrets and variables` -> `Actions` 配置以下内容：

### Secrets (加密)

- `LLM_API_KEY`: 你的 OpenAI/DeepSeek API Key
- `LLM_BASE_URL`: API 地址 (如 `https://api.deepseek.com`)
- `TAVILY_API_KEY`: Tavily Search API Key
- `TG_BOT_TOKEN`: Telegram Bot Token
- `TG_CHAT_ID`: 接收消息的 Chat ID

### Variables (公开)

- `ETF_LIST`: 逗号分隔的 ETF 代码 (如 `510300,512480`)
- `MUTUAL_LIST`: 逗号分隔的场外基金代码 (如 `000478,005827`)
- `LLM_MODEL`: 模型名称 (如 `gpt-4-turbo` 或 `deepseek-chat`)

### 个人持仓分析（可选）

支持个人持仓分析功能，开启后会生成个性化持仓报告并推送。

#### 方式一：本地文件（推荐本地运行使用）

在项目根目录创建 `holdings.json` 文件：

```json
{
    "holdings": [
        {
            "code": "510300",
            "name": "沪深300ETF",
            "type": "ETF",
            "shares": 10000,
            "avg_cost": 3.5,
            "buy_dates": ["2024-01-15", "2024-03-20"]
        }
    ],
    "risk_tolerance": "medium"
}
```

> ⚠️ `holdings.json` 已被 `.gitignore` 忽略，**不会上传到 GitHub**

#### 方式二：GitHub Secrets（用于 GitHub Actions）

将持仓配置转为 JSON 字符串，存入 `HOLDINGS_JSON` Secret：

```
HOLDINGS_JSON = {"holdings":[{"code":"510300","name":"沪深300ETF","type":"ETF","shares":10000,"avg_cost":3.5,"buy_dates":["2024-01-15"]}],"risk_tolerance":"medium"}
```

> 注意：所有字符串必须使用双引号，环境变量中需要转义特殊字符。

## 本地运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 设置环境变量 (Linux/Mac)
export LLM_API_KEY="your_api_key"
export LLM_BASE_URL="https://api.deepseek.com"
export TAVILY_API_KEY="your_tavily_key"
export TG_BOT_TOKEN="your_bot_token"
export TG_CHAT_ID="your_chat_id"
export ETF_LIST="510300,512480"
export MUTUAL_LIST="000478,005827"

# 3. 运行
python main.py
```

## 项目结构

```
AI-Fund-Copilot/
├── main.py              # 主程序入口
├── analyzer.py          # 指标计算 (日频/周频夏普率)
├── data_fetcher.py      # 数据获取 (AkShare)
├── llm_service.py       # LLM 分析服务
├── news_fetcher.py      # 资讯搜索
├── notifier.py          # Telegram 推送
├── utils.py             # 工具函数 (无风险利率获取)
├── config.py            # 配置文件
├── requirements.txt     # 依赖列表
├── .github/workflows/   # GitHub Actions 配置
└── README.md            # 说明文档
```

## 更新日志

### v2.0 (2026-01-24)

- ✅ 支持多时间范围夏普率计算（近1年、2年、3年）
- ✅ 动态获取无风险利率（1年期国债收益率）
- ✅ ETF 数据改用后复权 (hfq)
- ✅ 工行标准周频夏普率计算公式
- ✅ 更详细的 LLM 分析报告

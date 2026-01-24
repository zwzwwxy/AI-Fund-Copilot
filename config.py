import os

# --- LLM 配置 (GitHub Secrets) ---
LLM_API_KEY = os.getenv("LLM_API_KEY")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://api.openai.com/v1")
LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4-turbo")

# --- 搜索配置 (GitHub Secrets) ---
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# --- Telegram 配置 (GitHub Secrets) ---
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")

# --- 基金列表 (GitHub Variables) ---
# 格式: "112233,445566" (逗号分隔)
etf_str = os.getenv("ETF_LIST", "")
ETF_LIST = [x.strip() for x in etf_str.split(",") if x.strip()]

mutual_str = os.getenv("MUTUAL_LIST", "")
MUTUAL_LIST = [x.strip() for x in mutual_str.split(",") if x.strip()]

# --- 兜底默认值 ---
if not ETF_LIST and not MUTUAL_LIST:
    print("[Warning] No cloud config loaded, using default test data")
    MUTUAL_LIST = ["481004"]

# --- 财务参数 ---
# 注意：无风险利率已改为动态获取，详情见 utils.py
# 原有配置保留用于向后兼容
# 新版动态获取使用 utils.get_risk_free_rate()
RISK_FREE_RATE = 0.02

import requests

class TelegramBot:
    def __init__(self, token, chat_id):
        self.token = token
        self.chat_id = chat_id
        if token and chat_id:
            print("[OK] [Telegram] Bot 已初始化")
        else:
            print("[WARN] [Telegram] Token 或 Chat_ID 未配置")

    def send_report(self, fund_name, content):
        if not self.token or not self.chat_id:
            print(f"  [WARN] [Telegram] {fund_name} 推送跳过: 配置缺失")
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        clean_content = content.replace("*", "").replace("_", "")

        text = f"📊 *{fund_name} 分析日报*\n\n{clean_content}"

        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }

        content_len = len(content)
        print(f"  [推送] [Telegram] 正在发送 {fund_name} ({content_len} 字符)...")

        try:
            resp = requests.post(url, json=payload, timeout=10)
            if resp.status_code == 200:
                print(f"  [OK] [Telegram] {fund_name} 推送成功")
            else:
                print(f"  [ERROR] [Telegram] {fund_name} 推送失败: HTTP {resp.status_code}")
        except Exception as e:
            print(f"  [ERROR] [Telegram] {fund_name} 推送异常: {e}")

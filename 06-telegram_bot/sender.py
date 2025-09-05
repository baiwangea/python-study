import os
import telegram
import asyncio
from typing import Optional

# 从环境变量中获取 Token 和 Chat ID
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# --- 模板定义 (已彻底解决语法警告，并确保 Telegram 渲染正确) ---

# 模板1: 系统状态报告
SYSTEM_STATUS_TEMPLATE = r"""
*📊 系统状态报告*

*服务状态:*
🟢 `API 服务` \\- 运行正常
🟢 `数据库`   \\- 连接成功
🟠 `缓存服务` \\- 响应延迟

*资源使用率:*
CPU: `85%` 🌡️
内存: `60%` 🧠

`一切尽在掌握之中\\.`
"""

# 模板2: 版本更新日志
CHANGELOG_TEMPLATE = r"""
*🚀 版本 v1\\.2\\.0 更新日志*

*✨ 新功能*
\\- 用户现在可以导出 CSV 格式的报告
\\- 新增了仪表盘小组件

*🐛 Bug 修复*
\\- 修复了移动端导航栏错位的问题

*查看完整详情:* `https://example\\.com/changelog/v1-2-0`
"""

# 模板3: 错误警报 (带树状结构和代码块)
ERROR_ALERT_TEMPLATE = r"""
*🚨 严重错误警报*

在处理用户请求时发生了一个未捕获的异常\\.

*Details:*
```
Traceback (most recent call last):
  File "/app/main.py", line 42, in process_request
    result = process_data(data)
  File "/app/utils.py", line 15, in process_data
    raise ValueError("Invalid data format")
ValueError: Invalid data format
```

*请立即检查日志以获取更多信息\\!* 🗂️
"""


async def _get_bot():
    """初始化并返回 Bot 对象，如果配置缺失则返回 None。"""
    if not BOT_TOKEN or not CHAT_ID:
        print("错误：请先设置 TELEGRAM_BOT_TOKEN 和 TELEGRAM_CHAT_ID 环境变量。")
        return None
    return telegram.Bot(token=BOT_TOKEN)

async def send_text_message(message: str) -> bool:
    """发送纯文本消息。"""
    bot = await _get_bot()
    if not bot:
        return False
    try:
        await bot.send_message(chat_id=CHAT_ID, text=message)
        print(f"文本消息发送成功: {message}")
        return True
    except Exception as e:
        print(f"文本消息发送失败: {e}")
        return False

async def send_markdown_message(text: str) -> bool:
    """
    发送 MarkdownV2 格式的富文本消息。

    Args:
        text: 符合 Telegram MarkdownV2 格式的文本。

    Returns:
        True: 发送成功, False: 发送失败
    """
    bot = await _get_bot()
    if not bot:
        return False
    try:
        await bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='MarkdownV2')
        print(f"Markdown 消息发送成功。")
        return True
    except Exception as e:
        print(f"Markdown 消息发送失败: {e}")
        return False

async def send_photo(photo_path: str, caption: Optional[str] = None) -> bool:
    """发送本地图片。"""
    bot = await _get_bot()
    if not bot or not os.path.exists(photo_path):
        if not bot: return False
        print(f"错误：图片文件不存在 -> {photo_path}")
        return False
    try:
        with open(photo_path, 'rb') as photo_file:
            await bot.send_photo(chat_id=CHAT_ID, photo=photo_file, caption=caption)
        print(f"图片发送成功: {photo_path}")
        return True
    except Exception as e:
        print(f"图片发送失败: {e}")
        return False

async def send_document(document_path: str, caption: Optional[str] = None) -> bool:
    """发送本地文件作为文档。"""
    bot = await _get_bot()
    if not bot or not os.path.exists(document_path):
        if not bot: return False
        print(f"错误：文件不存在 -> {document_path}")
        return False
    try:
        with open(document_path, 'rb') as document_file:
            await bot.send_document(chat_id=CHAT_ID, document=document_file, caption=caption)
        print(f"文件发送成功: {document_path}")
        return True
    except Exception as e:
        print(f"文件发送失败: {e}")
        return False

async def main():
    """这是一个示例，展示如何使用所有发送功能。"""
    print("--- 开始执行 Telegram Bot 发送示例 ---")

    # 1. 发送纯文本
    await send_text_message("这是一个普通的纯文本消息。")
    await asyncio.sleep(1)

    # 2. 发送 Markdown 模板消息
    print("\n--- 发送 Markdown 模板 ---")
    await send_markdown_message(SYSTEM_STATUS_TEMPLATE)
    await asyncio.sleep(1)
    await send_markdown_message(CHANGELOG_TEMPLATE)
    await asyncio.sleep(1)
    await send_markdown_message(ERROR_ALERT_TEMPLATE)

    print("\n--- 示例执行完毕 ---")

if __name__ == '__main__':
    asyncio.run(main())

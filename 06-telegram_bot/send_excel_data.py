import pandas as pd
import asyncio
import os
import signal
import sys
from sender import send_text_message, send_markdown_message

# --- 配置 ---
EXCEL_FILE_PATH = '1.xlsx'
DELAY_BETWEEN_MESSAGES = 2

# 用于控制优雅退出的事件
stop_event = asyncio.Event()

def signal_handler(sig, frame):
    print("\nCtrl+C detected! Initiating graceful shutdown...")
    stop_event.set()

async def process_and_send():
    """
    读取 Excel 文件的第一列和第三列，并逐条发送。
    """
    # 1. 检查文件是否存在
    if not os.path.exists(EXCEL_FILE_PATH):
        error_msg = f"❌ 错误：Excel 文件 '{EXCEL_FILE_PATH}' 不存在。\n\n请将 `1.xlsx` 文件放置在与此脚本相同的目录下。"
        print(error_msg)
        await send_text_message(error_msg)
        return

    try:
        # 2. 读取 Excel 文件，跳过前两行（包括标题行），不使用标题
        df = pd.read_excel(EXCEL_FILE_PATH, header=None, skiprows=2)

        # 3. 检查表格是否至少有三列
        if df.shape[1] < 3:
            error_msg = f"❌ 错误：Excel 文件 '{EXCEL_FILE_PATH}' 的列数少于三列。\n\n请确保文件至少包含三列数据。"
            print(error_msg)
            await send_text_message(error_msg)
            return

    except Exception as e:
        error_msg = f"❌ 读取 Excel 文件时出错: {e}"
        print(error_msg)
        await send_text_message(error_msg)
        return

    # 4. 遍历数据行并发送消息
    total_rows = len(df)
    await send_text_message(f"🚀 开始发送任务，将读取第一列和第三列数据，共 {total_rows} 条记录。")
    await asyncio.sleep(1)

    success_count = 0
    interrupted = False
    for index, row in df.iterrows():
        if stop_event.is_set():
            interrupted = True
            break # 检测到中断信号，跳出循环

        # 通过位置索引（iloc）获取第一列和第三列的数据
        col1_data = row.iloc[0]
        col3_data = row.iloc[2]

        # 跳过存在空值的行
        # +3 是因为跳过了标题行（2行），且iterrows从0开始（+1），所以是当前Excel的行号
        excel_row_num = index + 3 
        if pd.isna(col1_data) or pd.isna(col3_data):
            print(f"- 跳过第 {excel_row_num} 行（Excel行号），因为存在空值。")
            continue

        # 确保第一列数据是整数类型，移除小数点
        if isinstance(col1_data, (int, float)) and not pd.isna(col1_data):
            col1_data = int(col1_data)

        # 发送第一列数据 (纯文本)
        await send_text_message(f"{col1_data}")
        await asyncio.sleep(0.5)

        # 发送第三列数据 (用户地址，使用 Markdown 的代码块格式使其可复制)
        markdown_message = f"`{col3_data}`"
        
        if await send_markdown_message(markdown_message):
            success_count += 1
            print(f"✅ 成功发送第 {excel_row_num} 行的记录。")
        else:
            print(f"❌ 发送第 {excel_row_num} 行的记录失败。")

        # 在每组消息后等待
        await asyncio.sleep(DELAY_BETWEEN_MESSAGES)

    if interrupted:
        summary_message = f"⚠️ 任务已中断！\n\n- 已处理记录数: {index + 1}\n- 成功发送: {success_count}"
    else:
        summary_message = f"🎉 任务完成！\n\n- 总记录数: {total_rows}\n- 成功发送: {success_count}"
        
    await send_text_message(summary_message)

async def main():
    # 注册 Ctrl+C 信号处理函数
    signal.signal(signal.SIGINT, signal_handler)

    # 运行前最后检查一次环境变量
    if not os.getenv('TELEGRAM_BOT_TOKEN') or not os.getenv('TELEGRAM_CHAT_ID'):
        print("❌ 致命错误：请首先在您的环境中设置 `TELEGRAM_BOT_TOKEN` 和 `TELEGRAM_CHAT_ID` 环境变量。")
        sys.exit(1) # 退出程序
    else:
        await process_and_send()

if __name__ == '__main__':
    asyncio.run(main())

import requests
from datetime import datetime
from collections import defaultdict

# API URL
url = "https://crcchainpro.com/api"
params = {
    "module": "account",
    "action": "txlist",
    "address": "0x9b9f2530b2c64da53A2B49C945EdafF8578fc530",
    "sort": "desc"  # 从最新开始
}
response = requests.get(url, params=params)
data = response.json()
if data["status"] != "1":
    print("API error:", data["message"])
    exit()

transactions = data["result"]
daily_amounts = defaultdict(float)
daily_transactions = defaultdict(list)

for tx in transactions:
    input_data = tx["input"]
    if input_data.startswith("0x94b918de"):
        # 提取 amount (假设 input[10:74] 是 64 位 hex，防止有额外数据)
        raw_amount_hex = input_data[10:74]
        raw_amount = int(raw_amount_hex, 16)
        amount = raw_amount / 10**18

        # 时间戳转换为日期和格式化时间
        timestamp = int(tx["timeStamp"])
        date = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d")

        daily_amounts[date] += amount
        daily_transactions[date].append((timestamp, tx["hash"], amount))

# 输出结果（按日期排序，从最早到最新）
for date in sorted(daily_amounts.keys()):
    print(f"--- {date} ---")
    # 按时间戳升序排序交易
    sorted_txs = sorted(daily_transactions[date], key=lambda x: x[0])
    for timestamp, tx_hash, amount in sorted_txs:
        formatted_time = datetime.utcfromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{formatted_time} - Hash: {tx_hash} - Amount: {amount:.2f} CRA")
    print(f"Total for {date}: {daily_amounts[date]:.2f} CRA")
    print()
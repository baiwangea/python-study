import redis
import time

r = redis.Redis(host='localhost', port=6379, db=0)

def producer():
    for i in range(5):
        r.lpush('my_queue', f"消息{i}")
        print(f"生产：消息{i}")
        time.sleep(1)

def consumer():
    while True:
        msg = r.brpop('my_queue', timeout=5)
        if msg:
            print(f"消费：{msg[1].decode()}")

# 可分别运行在不同机器上
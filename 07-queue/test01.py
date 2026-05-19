import queue
import threading
import time

q = queue.Queue()

def producer():
    for i in range(5):
        q.put(f"消息{i}")
        print(f"生产：消息{i}")
        time.sleep(1)

def consumer():
    while True:
        msg = q.get()
        if msg is None:
            break
        print(f"消费：{msg}")

threading.Thread(target=producer).start()
threading.Thread(target=consumer).start()
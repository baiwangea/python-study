from multiprocessing import Process, Queue

def producer(q):
    for i in range(5):
        q.put(f"消息{i}")
        print(f"生产：消息{i}")

def consumer(q):
    while True:
        msg = q.get()
        if msg is None:
            break
        print(f"消费：{msg}")

if __name__ == "__main__":
    q = Queue()
    p1 = Process(target=producer, args=(q,))
    p2 = Process(target=consumer, args=(q,))
    p1.start()
    p2.start()
    p1.join()
    q.put(None)  # 结束信号
    p2.join()
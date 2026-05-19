#!/usr/bin/env python3
import pika, sys
from lib.rabbitmq_utils import get_connection_parameters


def publish(msg: str, queue: str = "hello"):
    # 1. 建立 TCP 连接
    params = get_connection_parameters()
    conn = pika.BlockingConnection(params)
    ch = conn.channel()

    # 2. 声明队列（幂等操作，已存在则跳过）
    ch.queue_declare(queue=queue, durable=False)

    # 3. 发送消息
    ch.basic_publish(exchange="",  # 使用默认 direct 交换机
                     routing_key=queue,  # 队列名即路由键
                     body=msg.encode(),
                     properties=pika.BasicProperties(
                         delivery_mode=2))  # 2=持久化（需队列 durable=True 才完全生效）

    print(f" [x] Sent '{msg}'")
    conn.close()


if __name__ == "__main__":
    msg = " ".join(sys.argv[1:]) or "Hello World!"
    publish(msg)
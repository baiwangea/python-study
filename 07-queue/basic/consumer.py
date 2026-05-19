#!/usr/bin/env python3
import pika
from lib.rabbitmq_utils import get_connection_parameters

def callback(ch, method, properties, body):
    print(f" [x] Received {body.decode()}")
    # 手动 ack，确保消息真正处理完再告知 MQ
    ch.basic_ack(delivery_tag=method.delivery_tag)

def consume(queue: str = "hello"):
    params = get_connection_parameters()
    conn   = pika.BlockingConnection(params)
    ch     = conn.channel()

    ch.queue_declare(queue=queue, durable=False)

    # 一次只拿一条，处理完再取下一条（公平分发）
    ch.basic_qos(prefetch_count=1)
    ch.basic_consume(queue=queue, on_message_callback=callback, auto_ack=False)

    print(" [*] Waiting for messages. To exit press CTRL+C")
    ch.start_consuming()

if __name__ == "__main__":
    consume()
#!/usr/bin/env python3
# consumer_ttl_dlx.py
import pika, signal, sys
from lib.rabbitmq_utils import get_connection_parameters

Q_REAL = 'order.pay.delayed'


def process(body: bytes) -> bool:
    """
    真正的业务逻辑，返回 True 表示成功，False 表示需要重试。
    """
    print(f'[x] 处理订单: {body.decode()}')
    # TODO: 调用 DB/HTTP，捕获异常
    return True


def callback(ch, method, properties, body):
    if process(body):
        ch.basic_ack(delivery_tag=method.delivery_tag)
        print('[√] 业务成功，已 ACK')
    else:
        # 失败时拒绝并 requeue=False，让消息再次成为死信
        # 同时给 TTL 队列再发一次，实现阶梯重试
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
        # 这里简单地把原消息再丢回延迟队列，形成 30s 后重试
        # 生产环境可换不同 TTL 队列（5s/30s/5min/30min）
        ch.basic_publish(exchange='',
                         routing_key='order.pay',  # 又回到 TTL 队列
                         body=body,
                         properties=pika.BasicProperties(delivery_mode=2))
        print('[!] 业务失败，已 NACK 并重新进入延迟循环')


def main():
    params = get_connection_parameters()
    conn = pika.BlockingConnection(params)
    ch = conn.channel()
    ch.queue_declare(Q_REAL, durable=True)  # 确保队列存在
    ch.basic_qos(prefetch_count=1)  # 公平分发
    ch.basic_consume(queue=Q_REAL,
                     on_message_callback=callback,
                     auto_ack=False)

    print('[*] 等待延迟消息，按 CTRL+C 退出')

    # 优雅退出：收到 SIGINT 后先停消费、再关连接
    def _shutdown(sig, frame):
        print('\n 关闭中…')
        ch.stop_consuming()
        conn.close()
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    ch.start_consuming()


if __name__ == '__main__':
    main()

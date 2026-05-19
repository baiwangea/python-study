import pika
from lib.rabbitmq_utils import get_connection_parameters

ex_name = 'ex.delayed'
params = get_connection_parameters()
conn = pika.BlockingConnection(params)
ch = conn.channel()

# 1. 声明类型为 x-delayed-message 的交换机
ch.exchange_declare(exchange=ex_name,
                    exchange_type='x-delayed-message',
                    arguments={'x-delayed-type': 'direct'})

# 2. 发送带 x-delay 头（毫秒）的消息
delay_ms = 60_000   # 1 min
props = pika.BasicProperties(
    headers={'x-delay': delay_ms},
    delivery_mode=2
)
ch.basic_publish(exchange=ex_name,
                 routing_key='order.pay',
                 body=b'orderId=67890',
                 properties=props)
print('[x] 消息将在 60 s 后投递')
conn.close()
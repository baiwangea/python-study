import pika, json, time
from lib.rabbitmq_utils import get_connection_parameters

TTL = 30_000          # 30 s 后过期
EX_DLX = 'ex.dlx'     # 死信交换机
Q_REAL = 'order.pay.delayed'  # 真正消费队列
Q_DELAY= 'order.pay'          # 延迟队列（无消费者）

params = get_connection_parameters()
conn = pika.BlockingConnection(params)
ch = conn.channel()

# 1. 死信交换机和业务队列
ch.exchange_declare(EX_DLX, exchange_type='direct', durable=True)
ch.queue_declare(Q_REAL, durable=True)
ch.queue_bind(Q_REAL, EX_DLX, routing_key=Q_REAL)

# 2. 延迟队列（关键参数）
args = {
    'x-dead-letter-exchange': EX_DLX,     # 到期后转投 DLX
    'x-dead-letter-routing-key': Q_REAL,  # 指定路由键
    'x-message-ttl': TTL                  # 队列级 TTL
}
ch.queue_declare(Q_DELAY, durable=True, arguments=args)

# 3. 发送延迟消息
body = json.dumps({'orderId': 12345, 'ttl': TTL})
ch.basic_publish('', Q_DELAY, body,
                 properties=pika.BasicProperties(delivery_mode=2))
print('[x] 延迟消息已发送，30 s 后可见')
conn.close()
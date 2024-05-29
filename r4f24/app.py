import dramatiq

from dramatiq.brokers.redis import RedisBroker
from dramatiq_dashboard import DashboardApp

broker = RedisBroker(host="127.0.0.1", port=6379)
broker.declare_queue("default")
dramatiq.set_broker(broker)
app = DashboardApp(broker=broker, prefix="")

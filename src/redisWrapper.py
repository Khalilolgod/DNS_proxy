import redis
import os

class RedisSingleton:
    _instance = None

    @staticmethod
    def get_instance(host=os.environ.get('REDIS_HOST'), port=os.environ.get('REDIS_PORT')):
        if not RedisSingleton._instance:
            RedisSingleton._instance = redis.Redis(
                host=host, port=port, socket_keepalive=True)
        return RedisSingleton._instance

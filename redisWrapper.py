import redis


class RedisSingleton:
    _instance = None

    @staticmethod
    def get_instance(host='localhost', port=6379):
        if not RedisSingleton._instance:
            RedisSingleton._instance = redis.Redis(
                host=host, port=port, socket_keepalive=True)
        return RedisSingleton._instance

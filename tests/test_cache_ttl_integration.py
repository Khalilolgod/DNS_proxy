import unittest
import os
import sys
import time

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import dns.resolver
from src.redisWrapper import RedisSingleton as r

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 5005

class CachePersistIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.proxy_resolver = dns.resolver.Resolver(configure=False)
        self.proxy_resolver.nameservers = [PROXY_HOST]
        self.proxy_resolver.port = PROXY_PORT
        self.redis_service = r.get_instance('127.0.0.1', 6379)

    def test_api(self):
        query = 'google.com'
        query_msg = dns.message.make_query(query, 'A')
        redis_key = query_msg.to_wire()[12:]

        self.proxy_resolver.resolve(query, 'A').response.to_wire()
        self.redis_service.pexpire(redis_key, 50)

        time.sleep(0.1)

        response_redis = self.redis_service.get(redis_key)
        self.assertIsNone(response_redis)


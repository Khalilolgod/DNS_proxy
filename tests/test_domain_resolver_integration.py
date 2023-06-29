import unittest

import dns.resolver

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 5005

DNS_HOST = '8.8.8.8'
DNS_PORT = 53

class DomainResolverIntegrationTest(unittest.TestCase):
    def setUp(self):
        self.proxy_resolver = dns.resolver.Resolver(configure=False)
        self.proxy_resolver.nameservers = [PROXY_HOST]
        self.proxy_resolver.port = PROXY_PORT

        self.resolver = dns.resolver.Resolver(configure=False)
        self.resolver.nameservers = [DNS_HOST]
        self.resolver.port = DNS_PORT

    def test_api(self):
        queries = ['digikala.com', 'google.com', 'stackoverflow.com', 'aparat.com',
                   'varzesh3.com', 'namnak.com', 'linkedin.com', 'apple.com', 'amazon.com', 'yasdl.com']

        default_results = {}
        proxy_results = {}
        for query in queries:
            for answer in self.resolver.resolve(query, 'A'):
                if (query not in default_results):
                    default_results[query] = [answer.to_text()]
                else:
                    default_results[query].append(answer.to_text())
                default_results[query] = sorted(default_results[query])

            for answer in self.proxy_resolver.resolve(query, 'A'):
                if (query not in proxy_results):
                    proxy_results[query] = [answer.to_text()]
                else:
                    proxy_results[query].append(answer.to_text())
                proxy_results[query] = sorted(proxy_results[query])

        self.assertEqual(default_results, proxy_results)

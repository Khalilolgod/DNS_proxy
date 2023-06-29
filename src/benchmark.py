import dns.resolver
import time
import numpy as np
import matplotlib.pyplot as plt

PROXY_HOST = '127.0.0.1'
PROXY_PORT = 5005

domains = ['digikala.com', 'google.com', 'stackoverflow.com', 'aparat.com',
           'varzesh3.com', 'namnak.com', 'linkedin.com', 'apple.com', 'amazon.com', 'yasdl.com']

num_requests = 100

queries = np.repeat(domains, num_requests // len(domains) + 1)[:num_requests]

default_response_times = {}
proxy_response_times = {}

for query in queries:
    start_time = time.time()
    answers = dns.resolver.resolve(query, 'A')
    end_time = time.time()
    request_time = (end_time - start_time) * 1000
    if query not in default_response_times:
        default_response_times[query] = [request_time]
    else:
        default_response_times[query].append(request_time)

for query in queries:
    start_time = time.time()
    resolver = dns.resolver.Resolver(configure=False)
    resolver.nameservers = [PROXY_HOST]
    resolver.port = PROXY_PORT
    answers = resolver.resolve(query, 'A')
    end_time = time.time()
    request_time = (end_time - start_time) * 1000
    if query not in proxy_response_times:
        proxy_response_times[query] = [request_time]
    else:
        proxy_response_times[query].append(request_time)

default_mean_times = {}
proxy_mean_times = {}
for domain, times in default_response_times.items():
    mean_time = sum(times) / len(times)
    default_mean_times[domain] = mean_time
for domain, times in proxy_response_times.items():
    mean_time = sum(times) / len(times)
    proxy_mean_times[domain] = mean_time

sorted_domains = sorted(default_mean_times.keys(),
                        key=lambda x: default_mean_times[x])

fig, ax = plt.subplots()
ax.bar(sorted_domains, [default_mean_times[d]
       for d in sorted_domains], label='Default resolver')
ax.bar(sorted_domains, [proxy_mean_times[d]
       for d in sorted_domains], label='Resolver with proxy')
ax.set_xticklabels(sorted_domains, rotation=90)
ax.set_xlabel('Domain name')
ax.set_ylabel('Mean response time (ms)')
ax.set_title('DNS request times')
ax.legend()
plt.show()

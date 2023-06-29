import dns.resolver
import time
import numpy as np
import matplotlib.pyplot as plt

PROXY_HOST = '127.0.0.1';
PROXY_PORT = 5005;

domains = ['digikala.com', 'google.com', 'stackoverflow.com', 'aparat.com', 'varzesh3.com', 'namnak.com', 'linkedin.com', 'apple.com', 'amazon.com', 'yasdl.com']

num_requests = 100

queries = np.repeat(domains, num_requests // len(domains) + 1)[:num_requests]

default_results = {}
proxy_results = {}

for query in queries:
    start_time = time.time()
    request_size = len(dns.message.make_query(query, 'A').to_wire())
    answers = dns.resolver.resolve(query, 'A')
    response_size = len(answers.response.to_wire())
    end_time = time.time()
    request_time = (end_time - start_time) * 1000
    traffic_volume = (request_size + response_size) * 2
    if query not in default_results:
        default_results[query] = {'response_times': [request_time], 'traffic_volumes': [traffic_volume]}
    else:
        default_results[query]['response_times'].append(request_time)
        default_results[query]['traffic_volumes'].append(traffic_volume)

resolver_cache = {}
for query in queries:
    start_time = time.time()
    if query not in resolver_cache:
        resolver = dns.resolver.Resolver(configure=False)
        resolver.nameservers = [PROXY_HOST]
        resolver.port = PROXY_PORT
        resolver_cache[query] = resolver
    else:
        resolver = resolver_cache[query]
    request_size = len(dns.message.make_query(query, 'A').to_wire())
    answers = resolver.resolve(query, 'A')
    response_size = len(answers.response.to_wire())
    traffic_volume = request_size + response_size
    if query not in proxy_results:
        proxy_results[query] = {'response_times': [], 'traffic_volumes': []}
        traffic_volume *= 2
    end_time = time.time()
    request_time = (end_time - start_time) * 1000
    proxy_results[query]['response_times'].append(request_time)
    proxy_results[query]['traffic_volumes'].append(traffic_volume)

default_mean_times = {}
default_mean_volumes = {}
for domain, results in default_results.items():
    mean_time = sum(results['response_times']) / len(results['response_times'])
    mean_volume = sum(results['traffic_volumes']) / len(results['traffic_volumes'])
    default_mean_times[domain] = mean_time
    default_mean_volumes[domain] = mean_volume

proxy_mean_times = {}
proxy_mean_volumes = {}
for domain, results in proxy_results.items():
    mean_time = sum(results['response_times']) / len(results['response_times'])
    mean_volume = sum(results['traffic_volumes']) / len(results['traffic_volumes'])
    proxy_mean_times[domain] = mean_time
    proxy_mean_volumes[domain] = mean_volume

sorted_domains = sorted(default_mean_times.keys(), key=lambda x: default_mean_times[x])

# Plot results
fig, ax = plt.subplots()
ax.bar(sorted_domains, [default_mean_times[d] for d in sorted_domains], label='Default resolver')
ax.bar(sorted_domains, [proxy_mean_times[d] for d in sorted_domains], label='Resolver with proxy')
ax.set_xticks(range(len(sorted_domains)))
ax.set_xticklabels(sorted_domains, rotation=90)
ax.set_xlabel('Domain name')
ax.set_ylabel('Mean response time (ms)')
ax.set_title('DNS request times')

fig2, ax2 = plt.subplots()
ax2.bar(sorted_domains, [default_mean_volumes[d] for d in sorted_domains], label='Default resolver')
ax2.bar(sorted_domains, [proxy_mean_volumes[d] for d in sorted_domains], label='Resolver with proxy')
ax2.set_xticks(range(len(sorted_domains)))
ax2.set_xticklabels(sorted_domains, rotation=90)
ax2.set_xlabel('Domain name')
ax2.set_ylabel('Mean traffic volume (bytes)')
ax2.set_title('DNS traffic volumes')
ax2.legend()
plt.show()
from time import sleep
from nvitop import ResourceMetricCollector

collector = ResourceMetricCollector()

print(collector.devices)

fib_numbers: list[int] = []

def fib(n: int) -> int:
    if n <= 2:
        return 1
    
    # no optimisations for the little hardware :(
    # if n < len(fib_numbers):
    #     return fib_numbers[n]
    
    fib_numbers.append(fib(n - 1) + fib(n - 2))
    return fib_numbers[-1]

nvi_tag = 'test'
result = None
with collector.context(tag=nvi_tag) as col:
    print([fib(x) for x in range(1, 35)])
    result = col.collect()
    
    
print(result)


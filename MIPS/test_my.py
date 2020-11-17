# from django.contrib.staticfiles import finders
#
# result = finders.find('css/style.css')
# searched_locations = finders.searched_locations

# print(str('AERV').decode('utf-8').lower())

import random, timeit
from pympler import asizeof

def size_mb(obj):
    return round(asizeof.asizeof(obj)/1024**2)


set_ = set(str(random.random()) for _ in range(1_000_000))
num = str(random.random())
print(timeit.timeit(lambda: num in set_, number=1000))
print(size_mb(set_))



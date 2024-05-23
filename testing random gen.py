import time
import random
from pprint import pprint

def _timer(iterations:int = 1, timeLimit:int = 0):
	import time
	def decorator(func):
		def inner(*args, **kwargs):
			numbers = []
			print(f"""----------
Timing function: {func.__name__}
----------""")
			for x in range(iterations):
				if timeLimit and sum(numbers) > timeLimit:
					break
				start = time.time()
				result = func(*deepcopy(args), **deepcopy(kwargs))
				print(f'iteration count: {x+1}')
				end = time.time()
				numbers.append(end-start)

			print(f"""----------
Timing done on function: {func.__name__}""")

			avg = sum(numbers)/len(numbers)
			_max = max(numbers)
			_min = min(numbers)
			if avg > 60:
				avg /= 60
				_max /= 60
				_min /= 60
				print(f'avg min: {avg}, max: {_max}, min: {_min}')
			else:
				print(f'avg sec: {avg}, max: {_max}, min: {_min}')

			if len(numbers) != iterations:
				print(f'Timer ended early with {len(numbers)} test(s) run instead of {iterations}')

			print('----------')


			return result
		return inner
	return decorator

def option1(width, height, key, num_bits):
	#random.seed(key)

	all_pixels:list[tuple]  = []
	for x in range(width):
		for y in range(height):
			all_pixels.append((x, y))

	random.shuffle(all_pixels)
	num = random.randint(1, 3)
	direction = random.choice([-1, 1])
	bits = list(range(num_bits))
	random.shuffle(bits)
	for _ in range(3):
		for x, y in all_pixels:
			for bit in bits:
				yield x, y, (x+y+num)%3, bit
			random.shuffle(bits)
		num += direction

gen = option1(4000, 4000, 'testing', 3)
for x in gen:
	thingy = [x, next(gen), next(gen)]
	input(thingy)
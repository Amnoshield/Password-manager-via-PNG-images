from copy import deepcopy
import time

import numpy as np
from PIL import Image
import secrets

def timer(itirations:int = 1, timeLimit:int = None):
	def decorator(func):
		def inner(*args, **kwargs):
			numbers = []
			for x in range(itirations):
				if timeLimit and sum(numbers) > timeLimit:
					break
				start = time.time()
				result = func(*deepcopy(args), **deepcopy(kwargs))
				end = time.time()
				numbers.append(end-start)
			
			print(f'avg sec: {sum(numbers)/len(numbers)}, max: {max(numbers)}, min: {min(numbers)}')

			if len(numbers) != itirations:
				print(f'Timer ended early with {len(numbers)} tests run instead of {itirations}')

			
			return result
		return inner
	return decorator


def swap_bits(num:int, bit_index:int, bit_value:int|str) -> int:
	num = int(num)
	new_num = list(format(num.to_bytes()[0], '08b'))
	new_num[-(bit_index+1)] = str(bit_value)
	return int(''.join(new_num), 2)

#@timer(100, 30)
def numpy_func(image:Image.Image, custom_function):
	# Get the dimensions of the image
	width, height = image.size

	# Get the RGBA values of all pixels at once using NumPy indexing
	all_rgba_values = np.array(image.getdata())
	all_rgba_values = all_rgba_values.reshape((height, width, 4))

	# Modify each random pixel and its color channel using the custom function
	func = np.vectorize(custom_function)
	print('starting to run numpy func now')
	all_rgba_values = func(all_rgba_values)

def func_to_use(value):
	for x in range(4):
		value = swap_bits(value, x, secrets.randbits(1))
	return value
	
""" for x in range(255):
	x+=1
	print(f'{x}:', func_for_numpy(x)) """

#C:\Users\CST\Desktop\testing.png
image = Image.open(input('Please enter image path: '))
image = image.convert('RGBA')

numpy_func(image, func_to_use)

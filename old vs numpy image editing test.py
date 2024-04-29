from copy import deepcopy
import time

import numpy as np
from PIL import Image

def timer(itirations:int = 1):
	def decorator(func):
		def inner(*args, **kwargs):
			numbers = []
			for x in range(itirations):
				start = time.time()
				result = func(*deepcopy(args), **deepcopy(kwargs))
				end = time.time()
				numbers.append(end-start)
			
			print(f'avg sec: {sum(numbers)/len(numbers)}, max: {max(numbers)}, min: {min(numbers)}')

			
			return result
		return inner
	return decorator


def swap_bits(num:int, bit_index:int, bit_value:int|str) -> int:
	new_num = list(format(num.to_bytes()[0], '08b'))
	new_num[-(bit_index+1)] = str(bit_value)
	return int(''.join(new_num), 2)

def numpy_func(image:Image.open, custom_function):
    # Load the image
    
    image = image.convert('RGBA')
    
    # Get the dimensions of the image
    width, height = image.size
    print(width, height)

    # Calculate the total number of pixels in the image
    total_pixels = width * height

    # Get the RGBA values of all pixels at once using NumPy indexing
    all_rgba_values = np.array(image.getdata())
    all_rgba_values = all_rgba_values.reshape((height, width, 4))

    # Modify each random pixel and its color channel using the custom function
    all_rgba_values = np.vectorize(custom_function)(all_rgba_values)


""" @timer(100)
def add(x, y):
	time.sleep(0.1)
	return x+y

add(1, 2) """

def func_for_numpy(value):
	for x in range(4):
		swap_bits(value, x)


image = Image.open(input('Please enter image path: '))

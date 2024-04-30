from copy import deepcopy
import random
import time
from typing import Generator

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
				print(f'itiration count: {x+1}')
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

#numpy func
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

#my func
def create_4d_array4(width:int, hight:int, key:str, colors:int = 4, num_bits = 3) -> Generator[list[list[list[tuple[int, int, int, int]]]], None, None]:
	random.seed(key)
	xList = list(range(width))
	random.shuffle(xList)
	yList = list(range(hight))
	random.shuffle(yList)

	counter = 0

	y=yList[counter]
	yield [[[(x, y, z, w) for w in range(num_bits)] for z in range(colors)] for x in range(width)]
	#print('swap')
	while True:
		#print('X avoiding', yList[:counter+1])

		x=xList[counter]
		yield [[[(x, y, z, w) for w in range(num_bits)] for z in range(colors)] for y in range(hight) if y not in yList[:counter+1]]

		counter += 1
		if counter >= min([width, hight]): break

		#print('swap')

		#print('Y avoiding', xList[:counter])

		y=yList[counter]
		yield [[[(x, y, z, w) for w in range(num_bits)] for z in range(colors)] for x in range(width) if x not in xList[:counter]]
		
		#print('swap')

	#input(f'{counter}, {[width, hight]}, {min([width, hight])}')
	
def create_Order3(width:int, hight:int, key:str, colors:int = 4, bits:int = 3)-> Generator[tuple[int, int, int, int], None, None]:
	array: Generator[list[list[list[tuple[int, int, int, int]]]], None, None] = create_4d_array4(width, hight, key, colors)
	random.seed(key)

	for y in array:
		random.shuffle(y)
		for z in y:
			random.shuffle(z)
			for w in z:
				random.shuffle(w)
	
		while len(y):
			randY = random.randint(0, len(y)-1)
			randZ = random.randint(0, len(y[randY])-1)
			
			yield from y[randY][randZ]
			
			y[randY].pop(randZ)
			if not len(y[randY]):
				y.pop(randY)

@timer(100, 30)
def mine(image:Image.Image, func):
	pixel_data = image.load()
	width, height = image.size
	order = create_Order3(width, height, 'nerd', bits=width*height)
	for _ in range(width*height):
		x, y, z, w = next(order)
		color = list(pixel_data[x, y])
		color[z] = func(color[z])

		pixel_data[x, y] = tuple(color)

#func to use
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

print('starting ')
mine(image, func_to_use)
print('------------')
numpy_func(image, func_to_use)

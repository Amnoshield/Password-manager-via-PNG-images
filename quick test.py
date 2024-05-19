import random
from numpy.random import MT19937
from numpy.random import RandomState, SeedSequence
from pprint import pprint
from math import floor
import sys
from time import sleep
import time
from copy import deepcopy

from typing import Generator
import numpy as np

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64

def timer(iterations:int = 1, timeLimit:int = 0):
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


def make_key(key:str, salt_:str = '', iterations:int = 0) -> bytes:
	input_bytes: bytes = key.encode('utf-8')
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=f'salt{key}{salt_}'.encode(),  # You should use a different salt value for each password
		iterations=100000+iterations,  # Adjust the number of iterations as needed
		backend=default_backend()
	)
	return base64.urlsafe_b64encode(kdf.derive(input_bytes))


def create_4d_array4(width:int, hight:int, key:str, colors:int = 4, num_bits = 3) -> Generator[list[list[list[tuple[int, int, int, int]]]], None, None]:
	random.seed(make_key(key, 'nerd', 20))
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
	array: Generator[list[list[list[tuple[int, int, int, int]]]], None, None] = create_4d_array4(width, hight, key, colors, num_bits=bits)
	random.seed(make_key(key, 'hehe', 7))

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

def bytes_string_formatting(obj:bytes):
	""" This makes a string of 1s and 0s from bytes. """
	global num_of_bits
	binary_data: str = ''.join(format(byte, '08b') for byte in obj)
	binary_data += '1' + '0'*(-(len(binary_data)+1)%num_of_bits)
	return binary_data

@timer(iterations=10)
def np_version(width:int, hight:int, key:str, colors:int = 4):
	array = np.empty([width, hight, colors, 3], dtype=int)
	for w in range(width):
		for h in range(hight):
			for c in range(colors):
				array[w,h,c] = (w, h, c)

	array = array.reshape((-1, 3))
	
	key = int(''.join(format(byte, '08b') for byte in make_key(key)), 2)
	while key > 2**32 - 1:
		key = floor(key/1.1)
	np.random.seed(key)

	np.random.shuffle(array)

	""" for x in array:
		yield x """

num_of_bits = 3

np_version(4000, 3000, key='testing')

""" for x in np_version(3, 2, colors=1, key='testing'):
	print(x) """

sleep(1)
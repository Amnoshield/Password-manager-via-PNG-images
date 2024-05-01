#This is a program for making the table for the swap bits function
import json
import pprint


def swap_bits(num:int, bit_index:int, bit_value:int|str) -> int:
	new_num = list(format(num.to_bytes()[0], '08b'))
	new_num[-(bit_index+1)] = str(bit_value)
	return int(''.join(new_num), 2)

print(swap_bits(255, 0, 0))

#quit()

swap_table = dict()

for x in range(256):
	for y in range(8):
		for z in range(2):
			swap_table[x,y,z] = swap_bits(x, y, z)

pprint.pprint(swap_table)

""" class swap_bits_table:
	def __init__(self, path:str = 'bit_swap_table.json'):
		import json
		with open(path) as json_file:
			self.data = json.load(json_file)
	
	def swap_bits(self, num:int, bit_index:int, bit_value:int) -> int:
		return self.data[str(num)][str(bit_index)][str(bit_value)]

bit_swap = swap_bits_table(path='bit_swap_table.json')

while True:
	number = int(input('Please enter an 8 bit number: '))
	print(number)
	print(format(number.to_bytes()[0], '08b'))
	index = int(input('Please enter a bit index: '))
	value = int(input('Please enter a bit value: '))
	
	new_num = bit_swap.swap_bits(number, index, value)
	
	print(new_num)
	print(format(new_num.to_bytes()[0], '08b')) """
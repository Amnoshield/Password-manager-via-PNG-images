#By Asa Kramer

import base64
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Generator
import random
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from time import sleep

#funcions
def swap_bits(num:int, bit_index:int, bit_value:int|str) -> int:
	new_num = list(format(num.to_bytes()[0], '08b'))
	new_num[-(bit_index+1)] = str(bit_value)
	return int(''.join(new_num), 2)

def to_binary(num:int, num_bits) -> str:
	return format(num.to_bytes()[0], f'0{num_bits+1}b')

def make_key(key:str) -> bytes:
	input_bytes: bytes = key.encode('utf-8')
	kdf = PBKDF2HMAC(
		algorithm=hashes.SHA256(),
		length=32,
		salt=f'salt{key}'.encode(),  # You should use a different salt value for each password
		iterations=100000,  # Adjust the number of iterations as needed
		backend=default_backend()
	)
	return base64.urlsafe_b64encode(kdf.derive(input_bytes))

def encrypt(text:str, key:str) -> str:
	""" This encrypts and then compresses a string into a string of 1's and 0'1 """
	new_key: bytes = make_key(key)

	cipher_suite = Fernet(new_key)
	new_text: bytes = cipher_suite.encrypt(text.encode())

	return compress(new_text)

def decrypt(text:str, key:str) -> str:
	""" This decompresses and then decrypts a string of 1's and 0's """
	new_key: bytes = make_key(key)

	cipher_suite = Fernet(new_key)
	new_text: str = cipher_suite.decrypt(decompress(text)).decode()

	return new_text

def compress(data:bytes) -> str:
	""" This compresses bytes into a string of 1's and 0's. """
	compressed: bytes = zlib.compress(data, level=9)
	binary_data: str = ''.join(format(byte, '08b') for byte in compressed)
	binary_data += '1' + '0'*(-(len(binary_data)+1)%3)
	#print(len(binary_data), len(binary_data)%3)
	return binary_data
	
def decompress(data:str) -> bytes:
	""" This decompresses a string of 1's and 0's into bytes. """
	bit = data[-1]
	while bit == '0':
		data = data[:-1]
		bit = data[-1]
	data = data[:-1]

	data_bytes = bytes(int(data[i:i+8], 2) for i in range(0, len(data), 8))
	return zlib.decompress(data_bytes)

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

#GUI
def loading_screen(text:str = 'Please wait...'):
	def decorator(func):
		def inner(*args, **kwargs):
			print(text)
			global loading_screen_label
			global loading_frame
			global root
			try: loading_screen_label.destroy()
			except: pass
			loading_screen_label = tk.Label(loading_frame, text=text)
			loading_screen_label.pack()
			loading_frame.update_idletasks()

			try:
				result = func(*args, **kwargs)
			except Exception as e:
				print(e)

				@loading_screen(f'{e}')
				def error_timer():
					[(sleep(0.1), root.update()) for x in range(15)]
				error_timer()
			else:
				loading_screen_label.destroy()
				loading_frame.update_idletasks()
				return result
		return inner
	return decorator

class ListEntry:
	def __init__(self, master, text:list[str] = ['', '', '', ''], make_pass = False):
		global list_entries

		if make_pass == True: text[1] = gen_pass()
		
		self.frame = tk.Frame(master)
		self.frame.grid(sticky="nswe")

		row_pos = 0

		self.entreis:list[tk.Entry] = []
		for idx, x in enumerate(text):
			temp = tk.StringVar()
			temp.set(x)
			self.entreis.append(tk.Entry(self.frame, width=20, textvariable=temp))
			self.entreis[-1].grid(row = row_pos, column=idx)

		self.strength = tk.Label(self.frame)
		self.strength.grid(row=row_pos, column=len(self.entreis))
		self.entreis[1].bind(sequence='<KeyRelease>', func=lambda a:self.check_pass_strength())
		self.check_pass_strength()

		self.delete_button = tk.Button(self.frame, text="-", command=self.delete_entry)
		self.delete_button.grid(row=row_pos, column=2+len(self.entreis), padx=5, pady=5)

		if not list_entries:
			self.top()

	def delete_entry(self):
		global list_entries
		global pass_frame

		self.frame.destroy()
		pass_frame.update_idletasks()
		list_entries.remove(self)
		if list_entries:
			list_entries[0].top()

	def check_pass_strength(self):
		self.strength.config(text=f'{check_password_strength(self.entreis[1].get()):.1f}%')
		self.frame.update_idletasks()

	def top(self):
		tk.Button(self.frame, text='Name').grid(sticky="nswe", row=0, column=0)
		tk.Button(self.frame, text='Password').grid(row=0, column=1)
		tk.Button(self.frame, text='Email').grid(row=0, column=2)
		tk.Button(self.frame, text='Username').grid(row=0, column=3)
		tk.Button(self.frame, text='Strenth').grid(row=0, column=4)

		for x in self.entreis:
			x.grid(row = 1)

		self.delete_button.grid(row=1)
		self.strength.grid(row=1)

def check_password_strength(password:str) -> float:
   # Count the number of uppercase letters, lowercase letters, digits, and special characters
   num_uppercase = sum(1 for char in password if char.isupper())
   num_lowercase = sum(1 for char in password if char.islower())
   num_digits = sum(1 for char in password if char.isdigit())
   num_special = sum(1 for char in password if char in '!@#$%^&*()-_=+[{]};:\'",<.>/?\\|`~')

   # Calculate the average quantity of each character type
   avg_quantity = (num_uppercase + num_lowercase + num_digits + num_special) / 4

   # Calculate the imbalance score based on differences from the average quantity
   imbalance_score = sum([abs(num_uppercase - avg_quantity), abs(num_lowercase - avg_quantity), abs(num_digits - avg_quantity), abs(num_special - avg_quantity)])/4

   #start the final score
   base_score = sum([1 for x in [num_digits, num_lowercase, num_special, num_uppercase] if x > 0])
   balanced_score = max(0, 2-imbalance_score/4)
   length_bonus = min((len(password) - 8)*0.5, 4)
   adjusted_score = balanced_score + base_score + length_bonus
   percentage = (adjusted_score / 10) * 100
   
   return percentage

@loading_screen('Please Select file')
def select_file():
	global file_path
	global file_image
	global details_frame
	global tk_image
	global file_details

	temp = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])

	if temp:
		file_path = temp
		image = Image.open(file_path)
		image = image.resize((100, 100))
		tk_image = ImageTk.PhotoImage(image)
		file_details.config(text=file_path.split('/')[-1])
		file_image.config(text=file_path.split('/')[-1], image=tk_image)
		details_frame.update_idletasks()

def save_data(data:str, key:str):
	global file_path
	global num_of_bits
	image = Image.open(file_path)
	pixel_data = image.load()

	width, hight = image.size
	order = create_Order3(width, hight, key, bits=num_of_bits)

	for bit in data:
		x, y, z, w = next(order)
		color = list(pixel_data[x, y])
		color[z] = swap_bits(color[z], w, bit)
		color[z] = swap_bits(color[z], num_of_bits, 0)

		pixel_data[x, y] = tuple(color)

	x, y, z, w = next(order)
	color = list(pixel_data[x, y])
	color[z] = swap_bits(color[z], num_of_bits, 1)
	pixel_data[x, y] = tuple(color)

	image.save(file_path)

def read_data(key:str):
	global file_path
	global num_of_bits


	image = Image.open(file_path)
	pixel_data = image.load()
	width, hight = image.size
	order = create_Order3(width, hight, key, bits=num_of_bits)

	data = ''
	while True:
		x, y, z, w = next(order)
		#print(to_binary(pixel_data[x, y][z], num_of_bits)[::-1])
		if to_binary(pixel_data[x, y][z], num_of_bits)[::-1][num_of_bits] == '1': break
		data += to_binary(pixel_data[x, y][z], num_of_bits)[::-1][w]

	return data

@loading_screen('Saving...')
def save_file():
	global password
	new = []
	temp = get_data()
	for x in temp:
		new.append('\t'.join(x))
	long:str = '\n'.join(new)

	data = encrypt(long, key=password)
	save_data(data, key=password)

	print('saved')

@loading_screen('Loading...')
def load_file():
	global password
	global passwords

	binary = read_data(password)

	new = []
	temp = decrypt(binary, password).split('\n')
	for x in temp:
		new.append(x.split('\t'))
	
	if len(new[0]) == 4:
		passwords = new
	else:
		passwords = []
	load_all()

def load_all() -> None:
	global list_entries
	global passwords
	global pass_frame

	while len(list_entries) > 0:
		list_entries[0].delete_entry()

	for x in passwords:
		list_entries.append(ListEntry(pass_frame, x))

	canvas.config(scrollregion=canvas.bbox("all"))
	pass_frame.update_idletasks()

def finish_pass(text:tk.Entry, root):
	global password
	password = text.get()
	root.destroy()

def get_pass(root) -> None:
	top= tk.Toplevel(root)
	top.geometry("750x250")
	top.title("Enter Password")

	label = tk.Label(top, text="Please enter password:")

	password_box = tk.Entry(top)
	
	done = tk.Button(top, text='Done', command=lambda:finish_pass(password_box, top))

	label.pack(fill=tk.BOTH)
	password_box.pack()
	done.pack()

def get_data() -> list[list[str]]:
	global list_entries
	global passwords
	passwords = [[y.get() for y in x.entreis] for x in list_entries]

	return(passwords)

def add_pass():
	global list_entries
	global pass_frame
	list_entries.append(ListEntry(pass_frame, make_pass=True))
	#load_all()
	canvas.config(scrollregion=canvas.bbox('all'))
	pass_frame.update_idletasks()

def gen_pass():
	while True:
		password = ''.join(random.choices(k=16, population='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-_=+[{]};:\'",<.>/?\\|`~'))
		if check_password_strength(password) == 100: return password

def wipe_file():
	global file_path
	global num_of_bits


	image = Image.open(file_path)
	pixel_data = image.load()
	width, hight = image.size
	
	for x in range(width):
		for y in range(hight):
			pixel_data[x, y] = int(('0'*num_of_bits + to_binary(pixel_data[x, y], num_of_bits)[::-1][:num_of_bits])[::-1], 2)

def add_noise():
	pass

def main() -> None:
	global list_entries
	global pass_frame
	global file_image
	global password
	global passwords
	global new_passwords
	global num_of_bits
	global canvas
	global details_frame
	global file_details
	global loading_frame
	global loading_screen_label
	global root
	num_of_bits = 3
	password = ''
	list_entries = []
	new_passwords = []
	passwords=[]

	# Create the main window
	width = 800
	hieght = 500
	root = tk.Tk()
	root.title("Password manager")
	root.geometry(f"{width}x{hieght}")
	root.pack_propagate(False)

	#detils
	details_frame = tk.Frame(root)
	
	#Toplevel
	
	load = tk.Button(details_frame, text='Load', command=load_file)
	file_image = tk.Label(details_frame)
	file_details = tk.Label(details_frame, text='No file selected')
	set_pass = tk.Button(details_frame, text='Set key', command=lambda:get_pass(get_pass_frame))
	file_details.grid(row=1, column=2, pady= 10)
	load.grid(row=1, column=1, pady= 10)
	set_pass.grid(row=1, column=3, pady= 10)
	file_image.grid(row=0, column=2)

	#top bar
	menu = tk.Menu(root)
	root.config(menu=menu)
	filemenu = tk.Menu(menu)
	menu.add_cascade(label='File', menu=filemenu)
	filemenu.add_command(label='Save...', command=save_file)
	filemenu.add_separator()
	filemenu.add_command()
	filemenu.add_separator()
	filemenu.add_command(label='Open...', command=select_file)
	""" filemenu.add_separator()
	filemenu.add_command(label='Exit', command=root.quit) """

	#canvas
	canvas = tk.Canvas(root)
	scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	canvas.configure(yscrollcommand=scrollbar.set)
	pass_frame = tk.Frame(canvas)
	canvas.create_window((0, 0), window=pass_frame, anchor='nw')
	
	get_pass_frame = tk.Frame(root)

	new = tk.Button(root, text='+', command=add_pass)

	loading_frame = tk.Frame(root)

	loading_screen_label = tk.Label(loading_frame, text='')
	
	#pack
	loading_screen_label.pack()
	get_pass_frame.pack()
	loading_frame.pack()
	details_frame.pack()
	new.pack(side=tk.BOTTOM)
	canvas.pack(side=tk.BOTTOM, fill='y', expand=True, ipadx=100, padx=50)

	load_all()

	root.mainloop()

if __name__ == '__main__': main()

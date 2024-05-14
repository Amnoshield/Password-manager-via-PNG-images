#By Asa Kramer

import base64
from pprint import pprint
import zlib
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Generator, Literal
import random
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from PIL import Image, ImageTk
from time import sleep
from copy import deepcopy
import threading
from functools import lru_cache
import json
import pyperclip as pc

#decorators
def loading_screen(text:str = 'Please wait...'):
	def decorator(func):
		def inner(*args, **kwargs):
			global loading_screen_label
			global loading_frame
			global root
			try: loading_screen_label.destroy()
			except: pass
			loading_screen_label = tk.Label(loading_frame, text=text)
			loading_screen_label.pack()
			loading_frame.update_idletasks()

			try:
				result = []
				def run_func():
					try: result.append(func(*args, **kwargs))
					except: pass
				
				t1 = threading.Thread(target=run_func, name='t1')
				t1.start()
				while t1.is_alive():
					sleep(0.1)
					root.update()
				
				result = result[0]
			except Exception as e:
				print(e)

				@loading_screen(f'{e}')
				def error_timer():
					sleep(1.5)
				error_timer()
			else:
				loading_screen_label.destroy()
				loading_frame.update_idletasks()
				return result
		return inner
	return decorator

#functions
@lru_cache(maxsize=None)
def swap_bits(num: int, bit_index: int, bit_value: int) -> int:
    mask = 1 << bit_index
    if bit_value:
        return num | mask
    else:
        return num & ~mask

def to_binary(num:int, num_bits) -> str:
	return format(num.to_bytes()[0], f'0{num_bits+1}b')

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

@loading_screen('Sorting ...')
def sort_list(unsorted:list, idx:int):
	temp = deepcopy(unsorted)

	key = lambda a:a[idx]
	unsorted.sort(key=key)
	
	if temp == unsorted:
		unsorted.sort(key=key, reverse=True)

def change_setting(setting:Literal['bits', 'image_path'], value):
	settings = json.load(open('setting.json', 'r'))
	settings[setting] = value
	json.dump(settings, open('setting.json', 'w'))

def read_setting(setting:Literal['bits', 'image_path']):
	settings = json.load(open('setting.json', 'r'))
	
	return settings[setting]

#GUI
class ListEntry:
	def __init__(self, master, text:list[str] = ['', '', '', ''], make_pass = False):
		global list_entries

		if make_pass == True: text[1] = gen_password()
		
		self.frame = tk.Frame(master)
		self.frame.grid(sticky="nswe")

		row_pos = 0

		self.entries:list[tk.Entry] = []
		for idx, x in enumerate(text):
			temp = tk.StringVar()
			temp.set(x)
			self.entries.append(tk.Entry(self.frame, width=20, textvariable=temp))
			self.entries[-1].grid(row = row_pos, column=idx)

		self.strength = tk.Label(self.frame)
		self.strength.grid(row=row_pos, column=len(self.entries))
		self.entries[1].bind(sequence='<KeyRelease>', func=lambda a:self.check_pass_strength())
		self.check_pass_strength()

		self.delete_button = tk.Button(self.frame, text="-", command=self.delete_entry)
		self.delete_button.grid(row=row_pos, column=2+len(self.entries), padx=5, pady=5)

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
		self.strength.config(text=f'{check_password_strength(self.entries[1].get()):.1f}%')
		self.frame.update_idletasks()

	def top(self):
		self.b_name = tk.Button(self.frame, text='Name', command=lambda:(sort_list(get_data(), 0), load_all()))
		self.b_password = tk.Button(self.frame, text='Password', command=lambda:(sort_list(get_data(), 1), load_all()))
		self.b_email = tk.Button(self.frame, text='Email', command=lambda:(sort_list(get_data(), 2), load_all()))
		self.b_username = tk.Button(self.frame, text='Username', command=lambda:(sort_list(get_data(), 3), load_all()))
		self.b_strength = tk.Button(self.frame, text='Strength', command=lambda:(sort_list(get_data(), 4), load_all()))
		
		self.b_name.grid(row=0, column=0)
		self.b_password.grid(row=0, column=1)
		self.b_email.grid(row=0, column=2)
		self.b_username.grid(row=0, column=3)
		self.b_strength.grid(row=0, column=4)

		for x in self.entries:
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

def select_file(path = None):
	global file_path
	global file_image
	global details_frame
	global tk_image
	global file_details

	if path == None:
		path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])

	if path:
		file_path = path
		change_setting('image_path', path)
		image: Image.Image = Image.open(file_path)

		if image.mode != 'RGBA':
			image = image.convert('RGBA')
			image.save(file_path)

		image = image.resize((100, 100))
		
		tk_image = ImageTk.PhotoImage(image)
		file_details.config(text=file_path.split('/')[-1])
		file_image.config(text=file_path.split('/')[-1], image=tk_image)
		details_frame.update_idletasks()

def save_data(password_ = None):
	if not password_: global password
	else: password = password_

	new = []
	for x in [x[:-1] for x in get_data()]:
		new.append('\t'.join(x))
	long:str = '\n'.join(new)

	data = encrypt(long, key=password)

	return data
	
def read_data(data:str, password_ = None):
	global passwords
	if not password_: global password
	else: password = password_

	new = []
	for x in decrypt(data, password).split('\n'):
		new.append(x.split('\t'))
	
	if len(new[0]) == 4:
		passwords = new
	else:
		passwords = []
	
	load_all()

@loading_screen('Saving...')
def save_file():
	global file_path
	global num_of_bits

	data = save_data()
	
	image = Image.open(file_path)
	pixel_data = image.load()

	width, hight = image.size
	order = create_Order3(width, hight, password, bits=num_of_bits)

	for bit in data:
		x, y, z, w = next(order)
		color = list(pixel_data[x, y])
		color[z] = swap_bits(color[z], w, int(bit))
		color[z] = swap_bits(color[z], num_of_bits, 0)

		pixel_data[x, y] = tuple(color)

	x, y, z, w = next(order)
	color = list(pixel_data[x, y])
	color[z] = swap_bits(color[z], num_of_bits, 1)
	pixel_data[x, y] = tuple(color)

	image.save(file_path)

	print('saved')

@loading_screen('Loading...')
def load_file():
	global file_path
	global num_of_bits
	global password

	image = Image.open(file_path)
	pixel_data = image.load()
	width, hight = image.size
	order = create_Order3(width, hight, password, bits=num_of_bits)

	data = ''
	while True:
		x, y, z, w = next(order)
		#print(to_binary(pixel_data[x, y][z], num_of_bits)[::-1])
		if to_binary(pixel_data[x, y][z], num_of_bits)[::-1][num_of_bits] == '1': break
		data += to_binary(pixel_data[x, y][z], num_of_bits)[::-1][w]
	
	read_data(data)

def load_all() -> None:
	global list_entries
	global passwords
	global pass_frame

	while len(list_entries) > 0:
		list_entries[0].delete_entry()

	for x in passwords:
		x=x[:4]
		list_entries.append(ListEntry(pass_frame, x))

	canvas.config(scrollregion=canvas.bbox("all"))
	pass_frame.update_idletasks()

def ask_for_pass():
	global password
	global root
	user_input: str | None = simpledialog.askstring(title="key", prompt="Please enter key:", parent=root)
	if isinstance(user_input, str):
		password = user_input

def get_data() -> list[list[str]]:
	global list_entries
	global passwords
	passwords = [[y.get() for y in x.entries] for x in list_entries]

	strengths = [[float(x.strength.cget("text")[:-1])] for x in list_entries]

	passwords = [x+y for x, y in zip(passwords, strengths)]

	return passwords

def add_pass():
	global list_entries
	global pass_frame
	list_entries.append(ListEntry(pass_frame, make_pass=True))

	canvas.config(scrollregion=canvas.bbox('all'))
	pass_frame.update_idletasks()

def gen_password():
	while True:
		password = ''.join(random.choices(k=16, population='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-_=+[{]};:\'",<.>/?\\|`~'))
		if check_password_strength(password) == 100: return password

def add_noise():
	global file_path
	global num_of_bits
	global root

	percent = simpledialog.askinteger(title='percent', prompt='Please enter a percent of bits to be ones:', initialvalue=50, minvalue=0, maxvalue=100, parent=root)
	if isinstance(percent, int):
		percent /= 100
	else:
		return
	
	@loading_screen('Adding noise now')
	def inner():
		image = Image.open(file_path)
		pixel_data = image.load()
		width, hight = image.size

		random.seed()
		
		for x in range(width):
			for y in range(hight):
				for z in range(num_of_bits):
					pixel_data[x, y] = (
						swap_bits(pixel_data[x, y][0], z, random.random()<percent),
						swap_bits(pixel_data[x, y][1], z, random.random()<percent),
						swap_bits(pixel_data[x, y][2], z, random.random()<percent),
						swap_bits(pixel_data[x, y][3], z, random.random()<percent)
							)
		
		image.save(file_path)

	inner()

def change_bits():
	global num_of_bits
	temp = simpledialog.askinteger(title='bits', prompt='Please enter a number of bits to be affected:', initialvalue=num_of_bits, minvalue=1, maxvalue=7, parent=root)
	if isinstance(temp, int):
		num_of_bits = temp
		change_setting('bits', num_of_bits)
		print('Changed bits to', num_of_bits)

def temp():
	global loading_frame
	temp1 = tk.Frame(root, takefocus=1)
	temp1.place(in_=loading_frame, anchor='center')
	for y in range(5):
		for x in range(5):
			label = tk.Label(temp1, text=f'{(x, y)}')
			label.grid(column=x, row=y)

def filter_data(data:str):
	return ''.join(filter(lambda a:a in '01', data))

def export():
	global root
	data = save_data(password_='')
	win = tk.Toplevel(master=root)
	win.title('Export')
	width = 250
	height = 150
	win.geometry(f"{width}x{height}")
	tk.Button(win, text='Copy data', command=lambda:pc.copy(data)).pack()
	text = tk.Text(win, height=5)
	text.insert(tk.END, data)
	text.config(state='disabled')
	text.pack(fill='both')
	tk.Button(win, text='Close', command=win.destroy).pack()

def import_data():
	global root

	def paste():
		text.insert(tk.END, filter_data(pc.paste()))

	def import_submit(save = True):
		@loading_screen('Unable to import. Please try again')
		def no_load():
			sleep(1.5)
		
		try:
			read_data(filter_data(text.get("1.0", "end-1c")), password_='')
			win.destroy()
			if save:
				save_file()
			
		except Exception as e:
			print(e)
			win.destroy()
			no_load()

	win = tk.Toplevel(master=root)
	win.title('Import')
	width = 350
	height = 180
	win.geometry(f"{width}x{height}")
	tk.Label(win, text='After pasting and saving data make sure to delete any copy').pack()
	
	tk.Button(win, text='Past data', command=paste).pack()
	text = tk.Text(win, height=5)
	text.pack(fill='both', pady=5)
	
	submit = tk.Frame(win)
	submit.pack()
	tk.Button(submit, text='Import and save', command=lambda:import_submit(True)).grid(row=0, column=0, padx=5)
	tk.Button(submit, text='Import', command=lambda:import_submit(False)).grid(row=0, column=1, padx=5)
	tk.Button(submit, text='Close', command=win.destroy).grid(row=0, column=2, padx=5)

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

	num_of_bits = read_setting('bits')
	password = ''
	list_entries = []
	new_passwords = []
	passwords=[]

	# Create the main window
	width = 800
	height = 500
	root = tk.Tk()
	root.title("Password manager")
	root.geometry(f"{width}x{height}")
	root.pack_propagate(False)

	#details
	details_frame = tk.Frame(root)
	
	#Toplevel
	
	load = tk.Button(details_frame, text='Load', command=load_file)
	file_image = tk.Label(details_frame)
	file_details = tk.Label(details_frame, text='No file selected')
	set_pass = tk.Button(details_frame, text='Set key', command=ask_for_pass)
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
	filemenu.add_command(label='Clear', command=add_noise)
	filemenu.add_command(label='Change bits', command=change_bits)
	filemenu.add_command(label='Export', command=export)
	filemenu.add_command(label='Import', command=import_data)
	filemenu.add_command(label='In testing', command=temp)
	filemenu.add_separator()
	filemenu.add_command(label='Open...', command=select_file)

	#canvas
	canvas = tk.Canvas(root)
	scrollbar = tk.Scrollbar(root, orient=tk.VERTICAL, command=canvas.yview)
	scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
	canvas.configure(yscrollcommand=scrollbar.set)
	pass_frame = tk.Frame(canvas)
	canvas.create_window((0, 0), window=pass_frame, anchor='nw')

	def _bound_to_mousewheel(event):
		canvas.bind_all('<MouseWheel>', _on_mousewheel)

	def _unbound_to_mousewheel(event):
		canvas.unbind_all("<MouseWheel>")

	def _on_mousewheel(event):
		canvas.yview_scroll(int(-1*(event.delta/120)), "units")

	pass_frame.bind('<Enter>', _bound_to_mousewheel)
	pass_frame.bind('<Leave>', _unbound_to_mousewheel)

	get_pass_frame = tk.Frame(root)

	new = tk.Button(root, text='+', command=add_pass)

	loading_frame = tk.Frame(root)

	loading_screen_label = tk.Label(loading_frame, text='')
	
	#pack
	loading_screen_label.pack()
	get_pass_frame.pack()
	loading_frame.pack()
	details_frame.pack()
	canvas.pack(fill='y', expand=True, ipadx=100, padx=50)
	new.pack()

	load_all()

	select_file(read_setting('image_path'))

	root.mainloop()

	swap_bits.cache_clear()	

if __name__ == '__main__': main()

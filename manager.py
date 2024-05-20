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
from tkinter import filedialog, simpledialog
from PIL import Image, ImageTk
from time import sleep
from copy import deepcopy
import threading
from functools import lru_cache
import json
import pyperclip as pc
import os

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

			
			result = []
			worked = [True]
			def run_func():
				try:
					output = func(*args, **kwargs)
					result.append(output)
				except Exception as e:
					worked.insert(0, e)
				
			t1 = threading.Thread(target=run_func, name='t1')
			t1.start()
			while t1.is_alive():
				sleep(0.1)
				root.update()
			
			if not isinstance(worked[0], bool):
				e = worked[0]
				print(e)

				@loading_screen(f'{e}')
				def error_timer():
					sleep(1.5)
				error_timer()
			else:
				loading_screen_label.destroy()
				loading_frame.update_idletasks()
				if len(result):
					return result[0]
		return inner
	return decorator

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

def bytes_string_formatting(obj:bytes):
	""" This makes a string of 1s and 0s from bytes. """
	global num_of_bits
	binary_data: str = ''.join(format(byte, '08b') for byte in obj)
	binary_data += '1' + '0'*(-(len(binary_data)+1)%num_of_bits)
	return binary_data

def string_bytes_formatting(obj:str):
	""" This makes bytes from a string of 1s and 0s. """
	bit = obj[-1]
	while bit == '0':
		obj = obj[:-1]
		bit = obj[-1]
	obj = obj[:-1]

	return bytes(int(obj[i:i+8], 2) for i in range(0, len(obj), 8))

def encrypt(text:str, key:str) -> str:
	""" This encrypts and then compresses a string into a string of 1's and 0'1 """
	new_key: bytes = make_key(key)

	cipher_suite = Fernet(new_key)
	new_text: bytes = cipher_suite.encrypt(compress(text.encode()))

	return bytes_string_formatting(compress(new_text))

def decrypt(text:str, key:str) -> str:
	""" This decompresses and then decrypts a string of 1's and 0's """
	new_key: bytes = make_key(key)

	cipher_suite = Fernet(new_key)
	new_text: str = decompress(cipher_suite.decrypt(decompress(string_bytes_formatting(text)))).decode()

	return new_text

def compress(data:bytes) -> bytes:
	""" This compresses bytes. """
	return zlib.compress(data, level=9)
	
def decompress(data:bytes) -> bytes:
	""" This decompresses bytes. """
	return zlib.decompress(data)

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
def sort_list(unsorted:list, key:str):
	temp = deepcopy(unsorted)

	func = lambda a:a[key]
	unsorted.sort(key=func)
	
	if temp == unsorted:
		unsorted.sort(key=func, reverse=True)

def change_setting(setting:Literal['bits', 'image_path', 'open_image_on_start', 'ask_for_key_on_start', 'edit_popup_after_creation', 'how_save_image_path'], value):
	global settings_path
	settings = json.load(open(settings_path, 'r'))
	settings[setting] = value
	json.dump(settings, open(settings_path, 'w'))

def read_setting(setting:Literal['bits', 'image_path', 'open_image_on_start', 'ask_for_key_on_start', 'edit_popup_after_creation', 'how_save_image_path']):
	global settings_path
	return json.load(open(settings_path, 'r'))[setting]

#GUI
class ListEntry:
	def __init__(self, master, data:dict = {"name":'', "password":'', "email":'', "username":'', "info":''}):
		global list_entries
		
		self.frame = tk.Frame(master)
		self.frame.grid(sticky="nswe")

		self.entries:list[tk.Entry] = []
		self.data:dict = {}
		for x in data.items():
			key = x[0]
			self.data[key] = tk.StringVar(None, data[key])

		self.fake_pass = tk.StringVar(None)

		self.entries.append(tk.Button(self.frame, width=15, textvariable=self.data['name'], command=lambda:pc.copy(self.data['name'].get())))
		self.entries.append(tk.Button(self.frame, width=15, textvariable=self.fake_pass, command=lambda:pc.copy(self.data['password'].get())))
		self.entries.append(tk.Button(self.frame, width=15, textvariable=self.data['email'], command=lambda:pc.copy(self.data['email'].get())))
		self.entries.append(tk.Button(self.frame, width=15, textvariable=self.data['username'], command=lambda:pc.copy(self.data['username'].get())))

		for idx, x in enumerate(self.entries):
			x.grid(row = 0, column=idx+1)

		self.strength = tk.StringVar(None)
		self.check_pass_strength()
		self.entries.append(tk.Label(self.frame, textvariable=self.strength, padx=8, pady=5))
		self.entries[-1].grid(row=0, column=5)

		self.edit_button = tk.Button(self.frame, text="Edit", command=self.edit)
		self.edit_button.grid(row=0, column=0, padx=5, pady=5)
		
		self.delete_button = tk.Button(self.frame, text="-", command=self.delete_entry)
		self.delete_button.grid(row=0, column=6, padx=5, pady=5)

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
		self.strength.set(f'{check_password_strength(self.data["password"].get()):.1f}%')
		self.fake_pass.set('•'*len(self.data['password'].get()))
		self.frame.update_idletasks()

	def top(self):
		b_name = tk.Button(self.frame, text='Name', command=lambda:(sort_list(get_data(), "name"), load_all()))
		b_password = tk.Button(self.frame, text='Password', command=lambda:(sort_list(get_data(), "password"), load_all()))
		b_email = tk.Button(self.frame, text='Email', command=lambda:(sort_list(get_data(), "email"), load_all()))
		b_username = tk.Button(self.frame, text='Username', command=lambda:(sort_list(get_data(), "username"), load_all()))
		b_strength = tk.Button(self.frame, text='Strength', command=lambda:(sort_list(get_data(), "strength"), load_all()))
		
		b_name.grid(row=0, column=1)
		b_password.grid(row=0, column=2)
		b_email.grid(row=0, column=3)
		b_username.grid(row=0, column=4)
		b_strength.grid(row=0, column=5)

		for x in self.entries:
			x.grid(row = 1)

		self.edit_button.grid(row=1)
		self.delete_button.grid(row=1)

	def get_data(self):
		data:dict = {}
		for x in self.data.items():
			key, value = x
			data[key] = value.get()
		
		data["strength"] = self.strength.get()
		return data

	def edit(self):
		global root
		win = tk.Toplevel(master=root)
		win.title('Edit')
		width = 500
		height = 400
		win.geometry(f"{width}x{height}")
		win.focus()
		win.grab_set()
		aline_windows(root, win)

		tk.Label(win, text='Name / site').pack()
		tk.Entry(win, textvariable=self.data['name']).pack(pady=5)

		tk.Label(win, text='Password').pack()
		frame = tk.Frame(win)
		frame.pack()
		tk.Button(frame, text='Generate password', command=lambda:(self.data['password'].set(gen_password()), self.check_pass_strength())).grid(row=0, column=0, padx=5)
		password = tk.Entry(frame, textvariable=self.data['password'])
		password.bind(sequence='<KeyRelease>', func=lambda a:self.check_pass_strength())
		password.grid(row=0, column=1, padx=5)
		tk.Label(frame, textvariable=self.strength).grid(row=0, column=2, padx=5)
		tk.Label(frame).grid(row=0, column=3, padx=31)

		tk.Label(win, text='Email').pack()
		tk.Entry(win, textvariable=self.data['email']).pack(pady=5)

		tk.Label(win, text='Username').pack()
		tk.Entry(win, textvariable=self.data['username']).pack(pady=5)

		tk.Label(win, text='Info').pack()
		text_box = tk.Text(win, height=8, width=50)
		text_box.insert(tk.END, self.data['info'].get())
		text_box.bind('<KeyRelease>', lambda a:self.data['info'].set(text_box.get("1.0", "end-1c")))
		text_box.pack(pady=5)

		tk.Button(win, text='Close', command=win.destroy).pack()

		win.bind('<Return>', lambda a: win.destroy())

		win.mainloop()

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

def convert_to_png():
	path = filedialog.askopenfilename(
        filetypes=[
            ("All image files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif;*.tiff;*.tif;*.ico;*.webp;*.ppm;*.pgm;*.pbm"),
			("All files", "*.*"),
            ("PNG files", "*.png"),
            ("JPEG files", "*.jpg;*.jpeg"),
            ("Bitmap files", "*.bmp;*.dib"),
            ("GIF files", "*.gif"),
            ("TIFF files", "*.tiff;*.tif"),
            ("ICO files", "*.ico"),
            ("WebP files", "*.webp"),
            ("PPM files", "*.ppm"),
            ("PGM files", "*.pgm"),
            ("PBM files", "*.pbm"),
            ("XBM files", "*.xbm"),
            ("XPM files", "*.xpm"),
            ("PCX files", "*.pcx"),
            ("TGA files", "*.tga"),
            ("SVG files", "*.svg"),
            ("MSP files", "*.msp")
        ]
    )

	image: Image.Image = Image.open(path)

	if image.mode != 'RGBA':
		image = image.convert('RGBA')

		directory, filename = os.path.split(path)
		filename_without_ext = os.path.splitext(filename)[0]

		path = filedialog.asksaveasfilename(
			initialdir=directory,
			initialfile=f"{filename_without_ext}.png",
			defaultextension=".png",
			filetypes=[("PNG files", "*.png")]
		)
		if path.endswith('.png'):
			image.save(path)

	if path.endswith('.png'):
		select_file(path)

def select_file(path = None):
	global file_path
	global file_image
	global details_frame
	global tk_image
	global file_details

	if path == None:
		path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])

	if path:
		try:
			file_path = path
			if read_setting('how_save_image_path') == 'recent':
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
		except FileNotFoundError as e:
			print(e)

def save_data(password_ = None):
	if not password_: global password
	else: password = password_

	new = []
	for x in get_data(exclude=['strength']):
		new.append('\t'.join(x.values()))
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
	
	passwords = []
	if len(new[0]) == 5:
		for x in new:
			passwords.append({"name":x[0], "password":x[1], "email":x[2], "username":x[3], "info":x[4]})
	
	load_all()

@loading_screen('Saving...')
def save_file(check_pass = None):
	global file_path
	global num_of_bits
	global password
	
	if check_pass != None and check_pass != password:
		raise Exception("Keys did not match")

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
	print('Loaded')

def load_all() -> None:
	global list_entries
	global passwords
	global pass_frame

	while len(list_entries) > 0:
		list_entries[0].delete_entry()

	for x in passwords:
		if "strength" in x.keys():
			x.pop("strength")
		list_entries.append(ListEntry(pass_frame, x))

	canvas.config(scrollregion=canvas.bbox("all"))
	pass_frame.update_idletasks()

def ask_for_pass():
	global password
	global root
	user_input: str | None = simpledialog.askstring(title="key", prompt="Please enter key:", parent=root)
	if isinstance(user_input, str):
		password = user_input

def get_data(exclude:list = []) -> list[dict]:
	global list_entries
	global passwords
	passwords = []
	for x in list_entries:
		temp = x.get_data()
		for z in exclude:
			temp.pop(z)
		passwords.append(temp)

	return passwords

def add_pass():
	global list_entries
	global pass_frame
	global canvas
	
	list_entries.append(ListEntry(pass_frame))

	canvas.config(scrollregion=canvas.bbox('all'))
	pass_frame.update_idletasks()

	if read_setting('edit_popup_after_creation'):
		list_entries[-1].edit()

def gen_password():
	while True:
		password = ''.join(random.choices(k=16, population='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*()-_=+[{]};:\'",<.>/?\\|`~'))
		if check_password_strength(password) == 100: return password

def aline_windows(win1:tk.Tk|tk.Toplevel, win2:tk.Tk|tk.Toplevel, wait_for_size = True):
	"""
	:win1: The base window that will be below the second.
	:win2: The window that will be placed on top of the first
	:wait_for_size: Determines if the program will wait for both windows to not be of size and position: 1x1+0+0
	"""
	
	if wait_for_size:
		while win1.geometry() == '1x1+0+0' or win2.geometry() == '1x1+0+0':
			sleep(0.1)
			root.update()

	wh, x, y = win1.geometry().split('+')
	x = int(x)
	y = int(y)
	w1, h1 = [int(x) for x in wh.split('x')]
	w2, h2 = [int(x) for x in win2.geometry().split('+')[0].split('x')]
	win2.geometry(f"+{round(x+(w1/2)-(w2/2))}+{round(y+(h1/2)-(h2/2))}")

#Menu
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

def filter_data(data:str):
	return ''.join(filter(lambda a:a in '01', data))

def export_binary():
	global root
	data = save_data(password_='')
	win = tk.Toplevel(master=root)
	win.title('Export')
	width = 280
	height = 180
	win.geometry(f"{width}x{height}")
	win.focus()
	win.grab_set()
	aline_windows(root, win)

	text = tk.Text(win, height=5)
	text.insert(tk.END, data)
	text.config(state='disabled')

	tk.Label(win,text='This exported data is not secure\nand should be deleted after use.').pack()
	tk.Button(win, text='Copy data', command=lambda:pc.copy(data)).pack()
	text.pack(fill='x')
	tk.Button(win, text='Close', command=win.destroy).pack()

def import_binary():
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
	win.focus()
	win.grab_set()
	aline_windows(root, win)

	tk.Label(win, text='After pasting and saving data make sure to delete any copy').pack()
	
	tk.Button(win, text='Past data', command=paste).pack()
	text = tk.Text(win, height=5)
	text.pack(fill='x', pady=5)
	
	submit = tk.Frame(win)
	submit.pack()
	tk.Button(submit, text='Import and save', command=lambda:import_submit(True)).grid(row=0, column=0, padx=5)
	tk.Button(submit, text='Import', command=lambda:import_submit(False)).grid(row=0, column=1, padx=5)
	tk.Button(submit, text='Close', command=win.destroy).grid(row=0, column=2, padx=5)

def change_bits():
	global num_of_bits
	temp = simpledialog.askinteger(title='bits', prompt='Please enter a number of bits to be affected:', initialvalue=num_of_bits, minvalue=1, maxvalue=7, parent=root)
	if isinstance(temp, int):
		num_of_bits = temp
		change_setting('bits', num_of_bits)
		print('Changed bits to', num_of_bits)

def change_open_file():
	global root
	win = tk.Toplevel(master=root)
	win.title('Change open file setting')
	width = 200
	height = 130
	win.geometry(f"{width}x{height}")
	win.focus()
	win.grab_set()
	aline_windows(root, win)

	tk.Label(win,text='Open image on start').pack()

	thingy = tk.StringVar(win, read_setting('open_image_on_start'))
	yes = tk.Radiobutton(win, text='yes', value='yes', variable=thingy, command=lambda:change_setting('open_image_on_start', 'yes'))
	ask = tk.Radiobutton(win, text='ask', value='ask', variable=thingy, command=lambda:change_setting('open_image_on_start', 'ask'))
	no  = tk.Radiobutton(win, text='no ', value='no', variable=thingy, command=lambda:change_setting('open_image_on_start', 'no'))

	yes.pack()
	ask.pack()
	no.pack()

	tk.Button(win, text='Close', command=win.destroy).pack()

	win.mainloop()

def set_default():
	global settings_path
	base_path = os.path.dirname(os.path.abspath(__file__))
	default_path = os.path.join(base_path, 'default_settings.json')
	
	settings = json.load(open(default_path, 'r'))
	json.dump(settings, open(settings_path, 'w'))

def image_path_setting():
	global root
	win = tk.Toplevel(master=root)
	win.title('Image path')
	width = 220
	height = 150
	win.geometry(f"{width}x{height}")
	win.focus()
	win.grab_set()
	aline_windows(root, win)

	tk.Label(win,text='Note: these features will only take effect\nwith {open image on start} set to yes').pack()

	how_save = tk.StringVar(None, read_setting('how_save_image_path'))

	tk.Radiobutton(win, variable=how_save, value='recent', text='Most recently opened', command=lambda:change_setting('how_save_image_path', how_save.get())).pack()

	tk.Radiobutton(win, variable=how_save, value='this', text='Only this file', command=lambda:change_setting('how_save_image_path', how_save.get())).pack()

	def inner():
		new_path = filedialog.askopenfilename(filetypes=[("PNG files", "*.png")])
		if new_path:
			path.set(new_path)
			change_setting('image_path', new_path)

	frame = tk.Frame(win)
	frame.pack()
	path = tk.StringVar(value=read_setting('image_path'))
	tk.Entry(frame, textvariable=path, state='readonly').grid(row=0, column=0)
	tk.Button(frame, text='Select file', command=inner).grid(row=0, column=1)

	tk.Button(win, text='Close', command=win.destroy).pack()

	win.mainloop()

#Main
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
	global settings_path

	base_path = os.path.dirname(os.path.abspath(__file__))
	settings_path = os.path.join(base_path, 'settings.json')

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
	
	load = tk.Button(details_frame, text='Load', command=load_file)
	file_image = tk.Label(details_frame)
	file_details = tk.Label(details_frame, text='No file selected')
	set_pass = tk.Button(details_frame, text='Set key', command=ask_for_pass)
	file_details.grid(row=1, column=2, pady= 10)
	load.grid(row=1, column=1, pady= 10)
	set_pass.grid(row=1, column=3, pady= 10)
	file_image.grid(row=0, column=2)

	#Menus
	menu = tk.Menu(root)
	root.config(menu=menu)

	filemenu = tk.Menu(menu)
	menu.add_cascade(label='File', menu=filemenu)
	filemenu.add_command(label='Save...', command=lambda:save_file(simpledialog.askstring(title="key", prompt="Please enter key:", parent=root)))
	filemenu.add_separator()
	filemenu.add_command(label='Export', command=export_binary)
	filemenu.add_command(label='Import', command=import_binary)
	filemenu.add_separator()
	filemenu.add_command(label='Clear', command=add_noise)
	filemenu.add_separator()
	filemenu.add_command(label='Open...', command=select_file)
	filemenu.add_command(label="Convert file", command=convert_to_png)

	settings_menu = tk.Menu(menu)
	menu.add_cascade(label='Settings', menu=settings_menu)
	settings_menu.add_command(label='Change bits', command=change_bits)
	settings_menu.add_separator()
	settings_menu.add_command(label='Startup image', command=change_open_file)
	settings_menu.add_command(label='Image path', command=image_path_setting)
	settings_menu.add_command(label='Delete image path', command=lambda:change_setting('image_path', None))
	settings_menu.add_separator()
	ask_value = tk.BooleanVar(None, read_setting('ask_for_key_on_start'))
	settings_menu.add_checkbutton(label='Ask for key', variable=ask_value, onvalue=True, offvalue=False, command=lambda:change_setting('ask_for_key_on_start', ask_value.get()))
	edit_popup = tk.BooleanVar(None, read_setting('edit_popup_after_creation'))
	settings_menu.add_checkbutton(label='Edit new passwords', variable=edit_popup, onvalue=True, offvalue=False, command=lambda:change_setting('edit_popup_after_creation', edit_popup.get()))
	settings_menu.add_separator()
	settings_menu.add_command(label='Reset to default', command=set_default)

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

	option = read_setting('open_image_on_start')
	if option == 'yes':
		select_file(read_setting('image_path'))
	elif option == 'ask':
		select_file()
	del option

	if read_setting('ask_for_key_on_start'):
		ask_for_pass()
			
	root.mainloop()

	swap_bits.cache_clear()	

if __name__ == '__main__': main()

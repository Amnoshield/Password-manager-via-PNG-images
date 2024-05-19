from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import zlib
import time
from copy import deepcopy

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
				#print(f'iteration count: {x+1}')
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

def bytes_string_formatting(obj:bytes):
	binary_data: str = ''.join(format(byte, '08b') for byte in obj)
	binary_data += '1' + '0'*(-(len(binary_data)+1)%num_of_bits)
	return binary_data

def string_bytes_formatting(obj:str):
	bit = data[-1]
	while bit == '0':
		data = data[:-1]
		bit = data[-1]
	data = data[:-1]

	return bytes(int(data[i:i+8], 2) for i in range(0, len(data), 8))

def bytes_to_str(byte:bytes|str):
	if isinstance(byte, bytes):
		return byte.decode()
	elif isinstance(byte, str):
		return byte

def str_to_bytes(string:str|bytes):
	if isinstance(string, str):
		return string.encode()
	elif isinstance(string, bytes):
		return string

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

@timer(100, 30)
def encrypt1(text:str, key:str) -> bytes:
	""" This encrypts and then compresses a string into a string of 1's and 0'1 """
	new_key: bytes = make_key(key)

	cipher_suite = Fernet(new_key)
	new_text: bytes = cipher_suite.encrypt(str_to_bytes(text))

	return compress(new_text)

@timer(100, 30)
def decrypt1(text:str, key:str) -> str:
	""" This decompresses and then decrypts a string of 1's and 0's """
	new_key: bytes = make_key(key)

	cipher_suite = Fernet(new_key)
	new_text: str = bytes_to_str(cipher_suite.decrypt(decompress(text)))

	return new_text

@timer(100, 30)
def encrypt2(text:str, key:str) -> bytes:
	""" This encrypts and then compresses a string into a string of 1's and 0'1 """
	new_key: bytes = make_key(key)

	cipher_suite = Fernet(new_key)
	new_text: bytes = cipher_suite.encrypt(compress(str_to_bytes(text)))

	return compress(new_text)

@timer(100, 30)
def decrypt2(text:bytes, key:str) -> str:
	""" This decompresses and then decrypts a string of 1's and 0's """
	new_key: bytes = make_key(key)

	cipher_suite = Fernet(new_key)
	new_text: str = bytes_to_str(decompress(cipher_suite.decrypt(decompress(text))))

	return new_text

def compress(data:bytes):
	""" This compresses bytes into a string of 1's and 0's. """
	global num_of_bits
	return zlib.compress(data, level=9)
	
def decompress(data:bytes) -> bytes:
	""" This decompresses a string of 1's and 0's into bytes. """
	return zlib.decompress(data)


num_of_bits = 3

text = """ 
<h1>Et natus quibusdam et Quis voluptas aut tempora laborum. </h1><p>Lorem ipsum dolor sit amet. Et distinctio rerum non enim erroreos debitis aut commodi quidem non nobis unde! Sit molestias optio <a href="https://www.loremipzum.com" target="_blank">Aut consequatur</a> ad error ipsa. Nam libero perspiciatisA voluptatem sit distinctio vitae ad reiciendis quasi id nostrum odit. Quo aspernatur isteQui eligendi est reprehenderit optio ea rerum accusamus quo quod perspiciatis aut tenetur libero. Non dolor harum <strong>Ad voluptas est voluptas delectus est necessitatibus aspernatur</strong> et dolor accusamus in error illo. Aut expedita natus quo iusto atquequo aspernatur non odio dolore. Non autem quiaEos officia ea tenetur odit et voluptatum quas et similique totam qui consequatur illum. Vel sunt doloribusEt accusantium rem eaque possimus vel odio saepe non nulla nisi aut omnis quisquam. </p><h2>In rerum autem aut excepturi accusamus eum magni molestias! </h2><p>In cupiditate repudiandae et quod saepeEt sequi id praesentium amet et autem atque qui quia ipsum et deserunt laboriosam. Vel reiciendis assumenda qui quod labore <a href="https://www.loremipzum.com" target="_blank">Sed neque ut dicta tempore sed laboriosam libero</a>. Vel eveniet laborum quo optio ipsumsit error qui temporibus doloremque ad voluptate voluptatem. Ea consequatur temporibus <em>Rem neque</em> vel voluptates nulla sit velit quas. Id illum quos cum eius oditid velit sit repellendus repudiandae sed rerum recusandae? Et totam accusamusHic enim est veniam officiis sed natus earum qui perferendis iusto ea commodi reiciendis eos recusandae quam! Cum veritatis esseEum alias cum porro rerum. Ut numquam culpa eum totam recusandaeEum laborum aut recusandae dignissimos in provident quis eos consequatur consequatur. </p><h3>Ut molestiae sapiente ad amet delectus.
 """

bytes_to_str(str_to_bytes('hahaha'))

print(len(text))
binary_data: str = ''.join(format(byte, '08b') for byte in str_to_bytes(text))
print(len(binary_data))

key = 'nerd'

temp = encrypt1(text, key)
binary_data: str = ''.join(format(byte, '08b') for byte in temp)
print(len(binary_data))
temp = decrypt1(temp, key)

print(temp == text)

temp = encrypt2(text, key)
binary_data: str = ''.join(format(byte, '08b') for byte in temp)
print(len(binary_data))
temp = decrypt2(temp, key)
print(temp == text)

#binary_data: str = ''.join(format(byte, '08b') for byte in compressed)
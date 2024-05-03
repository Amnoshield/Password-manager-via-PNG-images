""" find a way to use the GPU for the image processing??? """

import numpy as np
from PIL import Image

def modify_random_pixels(image_path, num_random_pixels, custom_function=None):
    # Load the image
    image = Image.open(image_path)
    image = image.convert('RGBA')
    
    # Get the dimensions of the image
    width, height = image.size
    print(width, height)

    # Calculate the total number of pixels in the image
    total_pixels = width * height

    # Check if the number of pixels to modify exceeds the total pixels
    if num_random_pixels > total_pixels:
        raise ValueError("Not enough space to modify {} pixels in an image with {} pixels.".format(num_random_pixels, total_pixels))

    # Generate random coordinates for n pixels wtf is this?????????
    """ random_x_coords = np.random.randint(0, width, size=num_random_pixels)
    random_y_coords = np.random.randint(0, height, size=num_random_pixels)
    random_channels = np.random.randint(0, 4, size=num_random_pixels) """

    # Get the RGBA values of all pixels at once using NumPy indexing
    print(list(image.getdata()))
    print('1---------')
    all_rgba_values = np.array(image.getdata())
    print(all_rgba_values)
    print('1.5-------')
    all_rgba_values = all_rgba_values.reshape((height, width, 4))
    print(all_rgba_values)

    # Modify each random pixel and its color channel using the custom function
    if custom_function is not None:
        all_rgba_values = np.vectorize(custom_function)(all_rgba_values)
        pass
        """ random_values = all_rgba_values[random_y_coords, random_x_coords, random_channels]
        modified_values = custom_function(random_values)
        all_rgba_values[random_y_coords, random_x_coords, random_channels] = modified_values """
    
    # Update the image with the modified RGBA values
    print('2------------')
    print(all_rgba_values)
    print(width, height)
    #temp = all_rgba_values.reshape(-1, 4)
    print('3------------')
    #print(temp)
    #for x in temp
    print('---')
    print(np.full((1, 1), 300))
    Image.fromarray(np.full((1, 1), 300), mode='RGB').show()
    im = Image.fromarray(all_rgba_values, mode='RGBA')
    
    #image.putdata()

    # Save the modified image
    output_path = r'C:\Users\asajk\Desktop\output_image_modified_pixels_3d.png'
    im.show()
    #im.save(output_path, bitmap_format='png')

    #print(f"Modified image with {num_random_pixels} random pixels saved to {output_path}")

# Example custom function (subtract 7 from the input value)
def subtract_seven(value):
    #print(value)
    return 0 if value <= 7 else value-7

# Example usage

""" img = Image.new("RGBA", (104, 104))  # single band 
newdata = list(range(0, 256, 4)) * 104
print(newdata)
img.putdata(newdata) 
img.show() """

#input('waiting')

try:
    modify_random_pixels(r'C:\Users\asajk\Desktop\small tesing.png', num_random_pixels=10, custom_function=subtract_seven)
except ValueError as e:
    print('aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', e)

"""  add a way to select the number of bits """

""" add restore / clear functions that only effect the selected bits.
Make restore function in between. (101 instead of 000 or 111) """

""" use a changed / encrypted password for the random.seed() and use np.random not random """

""" add password hide button???? """

""" use random.getrandbits(8)???? """

""" Use menu.post(300, 300) for password and settings popup
also look into using tkinter.messagebox.askyesno("ashyesno", "Is this an integer?") or something like that"""

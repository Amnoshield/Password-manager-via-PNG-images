""" find a way to use the GPU for the image prosessing. """
import numpy as np
from PIL import Image

def modify_random_pixels(image_path, num_random_pixels, custom_function=None):
    # Load the image
    image = Image.open(image_path)
    image = image.convert('RGBA')
    
    # Get the dimensions of the image
    width, height = image.size

    # Calculate the total number of pixels in the image
    total_pixels = width * height

    # Check if the number of pixels to modify exceeds the total pixels
    if num_random_pixels > total_pixels:
        raise ValueError("Not enough space to modify {} pixels in an image with {} pixels.".format(num_random_pixels, total_pixels))

    # Generate random coordinates for n pixels
    random_x_coords = np.random.randint(0, width, size=num_random_pixels)
    random_y_coords = np.random.randint(0, height, size=num_random_pixels)
    random_channels = np.random.randint(0, 4, size=num_random_pixels)

    # Get the RGBA values of all pixels at once using NumPy indexing
    all_rgba_values = np.array(image.getdata()).reshape((height, width, 4))

    # Modify each random pixel and its color channel using the custom function
    if custom_function is not None:
        random_values = all_rgba_values[random_y_coords, random_x_coords, random_channels]
        modified_values = custom_function(random_values)
        all_rgba_values[random_y_coords, random_x_coords, random_channels] = modified_values
    
    # Update the image with the modified RGBA values
    image.putdata(all_rgba_values.reshape(-1, 4))

    # Save the modified image
    output_path = 'output_image_modified_pixels_3d.png'
    image.save(output_path)

    print(f"Modified image with {num_random_pixels} random pixels saved to {output_path}")

# Example custom function (subtract 7 from the input value)
def subtract_seven(value):
    return value - 7

# Example usage
try:
    modify_random_pixels('path_to_your_image.png', num_random_pixels=10, custom_function=subtract_seven)
except ValueError as e:
    print(e)

"""  add a way to select the number of bits """

""" add restore / clear functions that only effect the selected bits.
Make restore function a inbetween. (101 instead of 000 or 111) """

""" use a changed / encrypted password for the random.seed() """

""" add password hide button???? """

""" use random.getrandbits(8)???? """



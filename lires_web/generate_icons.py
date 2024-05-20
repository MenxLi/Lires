"""
Generate icons for the different devices
"""

import os
from PIL import Image
from PIL import ImageFilter
import numpy as np

this_dir = os.path.dirname(os.path.abspath(__file__))
public_dir = os.path.join(this_dir, 'public')

src_icon = os.path.join(public_dir, 'icon.png')

def resizeAndFillWhite(im: Image.Image, size, fill_white=True, crop_fn = lambda x: x):

    # fill all transparent areas with white
    im = im.convert("RGBA")
    data = np.array(im)

    if fill_white:
        red, green, blue, alpha = data.T
        white_areas = alpha < 10
        # data[..., :-1][white_areas.T] = (255, 255, 255)
        data[white_areas.T] = (255, 255, 255, 255)
    
    im = Image.fromarray(data)
    im = crop_fn(im)

    im = im.resize((size, size))
    return im

def cropCircle(im: Image.Image):
    # crop to circle, leave the rest transparent
    # assert square image
    im_array = np.array(im)
    h, w, c = im_array.shape
    assert h == w
    assert c == 4
    mask = np.zeros((h, w), dtype=np.uint8)
    ij = np.indices((h, w), dtype=np.float32)
    mask = np.linalg.norm(ij - np.array([h, w], dtype=np.float32)[:, None, None]/2, axis=0) < float(h)/2
    mask = Image.fromarray(mask)
    im.putalpha(mask)
    return im

def cropMacSquare(im: Image.Image):
    raise NotImplementedError

def generateIcons():
    input_im = Image.open(src_icon)
    site_icon_dir = os.path.join(public_dir, 'site-icons')

    output_name = 'favicon-16x16.png'
    output_im = resizeAndFillWhite(input_im, 16, crop_fn=cropCircle)
    output_im.save(os.path.join(site_icon_dir, output_name))
    
    output_name = 'favicon-32x32.png'
    output_im = resizeAndFillWhite(input_im, 32, crop_fn=cropCircle)
    output_im.save(os.path.join(site_icon_dir, output_name))

    output_name = 'apple-touch-icon.png'
    output_im = resizeAndFillWhite(input_im, 180, crop_fn=lambda x: x)
    output_im.save(os.path.join(site_icon_dir, output_name))

    output_name = 'android-chrome-192x192.png'
    output_im = resizeAndFillWhite(input_im, 192, crop_fn=cropCircle)
    output_im.save(os.path.join(site_icon_dir, output_name))
    
    output_name = 'android-chrome-512x512.png'
    output_im = resizeAndFillWhite(input_im, 512, crop_fn=cropCircle)
    output_im.save(os.path.join(site_icon_dir, output_name))
    

if __name__ == '__main__':
    generateIcons()
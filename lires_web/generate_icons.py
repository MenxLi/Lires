"""
Generate icons for the different devices
"""

from __future__ import annotations
import os
from PIL import Image
from PIL import ImageFilter
import numpy as np

this_dir = os.path.dirname(os.path.abspath(__file__))
public_dir = os.path.join(this_dir, 'public')

src_icon = os.path.join(public_dir, 'icon.png')

def convolution(im: Image.Image, kernel: np.ndarray):
    # kernel is a 2D array shape (3, 3)
    # kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
    im_array = np.array(im)
    h, w, c = im_array.shape
    assert c == 4
    new_array = np.zeros((h, w, c), dtype=np.uint8)
    def convolve2d(a, conv_filter):
        submatrices = np.array([
            [a[:-2,:-2], a[:-2,1:-1], a[:-2,2:]],
            [a[1:-1,:-2], a[1:-1,1:-1], a[1:-1,2:]],
            [a[2:,:-2], a[2:,1:-1], a[2:,2:]]])
        multiplied_subs = np.einsum('ij,ijkl->ijkl',conv_filter,submatrices)
        return np.sum(np.sum(multiplied_subs, axis = -3), axis = -3)
    for i in range(4):
        channel = im_array[..., i]
        new_array[..., i][0:1, :] = channel[0:1, :]
        new_array[..., i][-1:, :] = channel[-1:, :]
        new_array[..., i][:, 0:1] = channel[:, 0:1]
        new_array[..., i][:, -1:] = channel[:, -1:]
        new_array[..., i][1:-1, 1:-1] = convolve2d(channel, kernel)
    new_array[..., 3] = im_array[..., 3]
    return Image.fromarray(new_array)

def resizeAndFill(
    im: Image.Image, size, 
    re_color = None,
    fill_color = (255, 255, 255, 255),
    crop_fn = lambda x: x):

    # fill all transparent areas with white
    im = im.convert("RGBA")
    data = np.array(im)

    if re_color:
        red, green, blue, alpha = data.T
        none_white_areas = alpha > 10
        data[none_white_areas.T] = re_color

    if fill_color:
        red, green, blue, alpha = data.T
        white_areas = alpha < 10
        # data[..., :-1][white_areas.T] = (255, 255, 255)
        if len(fill_color) == 3:
            data[..., :-1][white_areas.T] = fill_color
        else:
            data[white_areas.T] = fill_color
    
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

    # output_name = 'favicon-16x16.png'
    # output_im = resizeAndFill(input_im, 16, crop_fn=cropCircle)
    # output_im.save(os.path.join(site_icon_dir, output_name))
    
    # output_name = 'favicon-32x32.png'
    # output_im = resizeAndFill(input_im, 32, crop_fn=cropCircle)
    # output_im.save(os.path.join(site_icon_dir, output_name))

    output_name = 'apple-touch-icon.png'
    output_im = resizeAndFill(input_im, 180, crop_fn=lambda x: x)
    output_im.save(os.path.join(site_icon_dir, output_name))

    output_name = 'android-chrome-192x192.png'
    output_im = input_im.copy()
    output_im = resizeAndFill(
        output_im, 192, 
        crop_fn=cropCircle, 
        re_color=(255, 255, 255, 255), 
        fill_color=(50, 100, 255)
        )
    output_im.save(os.path.join(site_icon_dir, output_name))
    
    output_name = 'android-chrome-512x512.png'
    output_im = input_im.copy()
    output_im = resizeAndFill(
        output_im, 512, 
        crop_fn=cropCircle, 
        re_color=(255, 255, 255, 255), 
        fill_color=(50, 100, 255)
        )
    output_im.save(os.path.join(site_icon_dir, output_name))
    

if __name__ == '__main__':
    generateIcons()
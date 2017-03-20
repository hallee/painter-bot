from __future__ import print_function
import numpy as np
import argparse
from PIL import Image, ImageFilter
import time

import chainer
from chainer import cuda, Variable, serializers
from net import *

# parser = argparse.ArgumentParser(description='Real-time style transfer image generator')
# parser.add_argument('input')
# parser.add_argument('--gpu', '-g', default=-1, type=int,
#                     help='GPU ID (negative value indicates CPU)')
# parser.add_argument('--model', '-m', default='models/style.model', type=str)
# parser.add_argument('--out', '-o', default='out.jpg', type=str)
# parser.add_argument('--median_filter', default=3, type=int)
# parser.add_argument('--padding', default=50, type=int)
# parser.add_argument('--keep_colors', action='store_true')
# parser.set_defaults(keep_colors=False)
# args = parser.parse_args()


# from 6o6o's fork. https://github.com/6o6o/chainer-fast-neuralstyle/blob/master/generate.py
def original_colors(original, stylized):
    h, s, v = original.convert('HSV').split()
    hs, ss, vs = stylized.convert('HSV').split()
    return Image.merge('HSV', (h, s, vs)).convert('RGB')


def stylize(input, median_filter = 3, padding = 50, keep_colors = False):
    model = FastStyleNet()
    model_in = 'neuralstyle/models/candy_512_2_49000.model'
    serializers.load_npz(model_in, model)

    cuda.get_device(0).use()
    model.to_gpu()
    
    xp = cuda.cupy

    start = time.time()
    original = Image.fromarray(input).convert('RGB')
    image = np.asarray(original, dtype=np.float32).transpose(2, 0, 1)
    image = image.reshape((1,) + image.shape)
    image = np.pad(image, [[0, 0], [0, 0], [padding, padding], [padding, padding]], 'symmetric')
    image = xp.asarray(image)
    x = Variable(image)

    y = model(x)
    result = cuda.to_cpu(y.data)

    result = result[:, :, padding:-padding, padding:-padding]
    result = np.uint8(result[0].transpose((1, 2, 0)))
    med = Image.fromarray(result)
    med = med.filter(ImageFilter.MedianFilter(median_filter))
    if keep_colors:
        med = original_colors(original, med)
    print(time.time() - start, 'sec')

    return np.asarray(med)

import numpy as np
import PIL

def FloatImage3DToUintImage1D(floatImage):
    uintImage = np.zeros(shape=(floatImage.size // 3,), dtype=np.uint32)
    for i in range(floatImage.shape[0]):
        for j in range(floatImage.shape[1]):
            for k in range(floatImage.shape[2]):
                uintImage[i * floatImage.shape[1] + j] |= int(floatImage[i, j, k] * 255) << (8 * k)
            uintImage[i * floatImage.shape[1] + j] |= 255 << 24
    return uintImage
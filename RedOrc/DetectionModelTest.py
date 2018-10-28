from DetectionModelEvaluator import *
from TextRenderer import *
import os

for f in os.listdir("ProgressReports"):
    os.remove("ProgressReports\\" + f)

for f in os.listdir("TensorboardLogs"):
    os.remove("TensorboardLogs\\" + f)

filterCounts = [32, 64, 128, 256, 512] + [3]
kernelSizes = [(7, 7)] + [(3, 3)] * (len(filterCounts) - 1)
poolingStrides = [(2, 2)] * len(filterCounts)
poolingSizes = [(2, 2)] * len(filterCounts)

TextRenderer.Initialize()

imageProps = ImageProperties(128, 128, 96, WicGuid.WicPixelFormat96bppRGBFloat())
TextRenderer.SetImageProperties(imageProps)

textProps = TextProperties("Arial", FontWeight.Normal, FontStretch.Normal, FontStyle.Normal, 0, 24)
TextRenderer.SetTextProperties(textProps)

textPool = "abcdefghijklmopqrstuvwxyz"
textBounds = D2D1_RECT_F(20, 20, imageProps.imageWidth - 20, imageProps.imageHeight - 20)
textInfo = TextRenderer.GetRenderedTextInformation(textPool, textBounds)
text = GetRandomText(textInfo, textPool)

def dataGen():
    while True:
        imageBuffer = np.zeros(shape=(imageProps.imageHeight, imageProps.imageWidth, 3), dtype=np.float32)
        boundingBoxes = TextRenderer.RenderString(text, textBounds, True, False, imageBuffer.ctypes.data_as(ctypes.c_void_p))

        label = np.zeros(shape=(imageProps.imageHeight, imageProps.imageWidth, 3), dtype=np.float)
        for rect in boundingBoxes:
            label[int(rect.left), int(rect.top), 0] = 1                             # Confidence
            label[int(rect.left), int(rect.top), 1] = abs(rect.bottom - rect.top)   # Height
            label[int(rect.left), int(rect.top), 2] = abs(rect.right - rect.left)   # Width

        yield (imageBuffer, label)

dme = DetectionModelEvaluator(filterCounts, kernelSizes, poolingStrides, poolingSizes, dataGen, 1, 1)
dme.Benchmark(1000000, 1)

TextRenderer.Uninitialize()
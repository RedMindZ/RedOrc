from DetectionModel import *
from DetectionModelEvaluator import *
from TextRenderer import *
import os

for f in os.listdir("ProgressReports"):
    os.remove("ProgressReports\\" + f)

for f in os.listdir("TensorboardLogs"):
    os.remove("TensorboardLogs\\" + f)

#filterCounts = [20] * 20 + [3]
#kernelSizes = [(7, 7)] + [(3, 3)] * (len(filterCounts) - 1)
#poolingStrides = [(2, 2)] * len(filterCounts)
#poolingSizes = [(2, 2)] * len(filterCounts)
convProps =         [ConvProps(16, (7, 7)),     ConvProps(32, (5, 5)),     ConvProps(64, (3, 3)),     ConvProps(128, (3, 3)),    None,                           None,                          None,                          None,                          ConvProps(3, (3, 3))]
poolProps =         [PoolProps((2, 2), (2, 2)), PoolProps((2, 2), (2, 2)), PoolProps((2, 2), (2, 2)), PoolProps((2, 2), (2, 2)), None,                           None,                          None,                          None,                          None                ]
transConvProps =    [None,                      None,                      None,                      None,                      ConvProps(128, (3, 3), (2, 2)), ConvProps(64, (3, 3), (2, 2)), ConvProps(32, (5, 5), (2, 2)), ConvProps(16, (7, 7), (2, 2)), None                ]

TextRenderer.Initialize()

imageProps = ImageProperties(128, 128, 96, WicGuid.WicPixelFormat96bppRGBFloat())
TextRenderer.SetImageProperties(imageProps)

textProps = TextProperties("Arial", FontWeight.Normal, FontStretch.Normal, FontStyle.Normal, 0, 24)
TextRenderer.SetTextProperties(textProps)

textPool = "abcdefghijklmopqrstuvwxyz"
textBounds = D2D1_RECT_F(20, 20, imageProps.imageWidth - 20, imageProps.imageHeight - 20)
textInfo = TextRenderer.GetRenderedTextInformation(textPool, textBounds)


def dataGen():
    text = GetRandomText(textInfo, textPool)
    while True:
        imageBuffer = np.zeros(shape=(imageProps.imageHeight, imageProps.imageWidth, 3), dtype=np.float32)
        boundingBoxes = TextRenderer.RenderString(text, textBounds, True, False, imageBuffer.ctypes.data_as(ctypes.c_void_p))

        label = np.zeros(shape=(imageProps.imageHeight, imageProps.imageWidth, 3), dtype=np.float)
        for rect in boundingBoxes:
            label[round(rect.top), round(rect.left), 0] = 1                             # Confidence
            label[round(rect.top), round(rect.left), 1] = abs(rect.bottom - rect.top)   # Height
            label[round(rect.top), round(rect.left), 2] = abs(rect.right - rect.left)   # Width

        yield (imageBuffer, label)

#dme = DetectionModelEvaluator(filterCounts, kernelSizes, poolingStrides, poolingSizes, dataGen, 1, 1)
dme = DetectionModelEvaluator(convProps, poolProps, transConvProps, dataGen, 1, 1)
dme.Benchmark(1000000, 100)

TextRenderer.Uninitialize()
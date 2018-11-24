from tensorflow.keras.layers import Conv2D, MaxPooling2D, Conv2DTranspose
from DetectionModelEvaluator import *
from UNetModel import *
from ImageDataGenerator import *
from ProgressReporter import ProgressReporter
from MultiConv import MultiConv
import os

availableFonts = []
with open("ApprovedFonts.txt", "rt") as f:
    for font in f:
        availableFonts.append(font[:-1])

modelLayers = \
[
    Conv2D(32, (7, 7), padding="same", activation=tf.nn.relu),
    Conv2D(32, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(32, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(32, (7, 7), padding="same", activation=tf.nn.relu),
    Conv2D(32, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(32, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(32, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(64, (7, 7), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(64, (7, 7), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(64, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(128, (7, 7), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(128, (7, 7), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(256, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(3, (3, 3), padding="same", activation=tf.nn.relu)
]

modelLayersV2 = \
[
    MultiConv([Conv2D(16, (21, 1), padding="same", activation=tf.nn.relu), Conv2D(16, (1, 21), padding="same", activation=tf.nn.relu), Conv2D(32, (7, 7), padding="same", activation=tf.nn.relu)]),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(64, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    MultiConv([Conv2D(32, (21, 1), padding="same", activation=tf.nn.relu), Conv2D(32, (1, 21), padding="same", activation=tf.nn.relu), Conv2D(64, (7, 7), padding="same", activation=tf.nn.relu)]),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(128, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    MultiConv([Conv2D(64, (21, 1), padding="same", activation=tf.nn.relu), Conv2D(64, (1, 21), padding="same", activation=tf.nn.relu), Conv2D(128, (7, 7), padding="same", activation=tf.nn.relu)]),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(256, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(3, (3, 3), padding="same", activation=tf.nn.relu)
]

modelLayersV3 = \
[
    MultiConv([Conv2D(16, (21, 3), padding="same", activation=tf.nn.relu), Conv2D(16, (3, 21), padding="same", activation=tf.nn.relu), Conv2D(96, (13, 13), padding="same", activation=tf.nn.relu)]),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(64, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    MultiConv([Conv2D(32, (21, 3), padding="same", activation=tf.nn.relu), Conv2D(32, (3, 21), padding="same", activation=tf.nn.relu), Conv2D(64, (7, 7), padding="same", activation=tf.nn.relu)]),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(128, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    MultiConv([Conv2D(64, (21, 1), padding="same", activation=tf.nn.relu), Conv2D(64, (1, 21), padding="same", activation=tf.nn.relu), Conv2D(128, (7, 7), padding="same", activation=tf.nn.relu)]),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(256, (2, 2), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(3, (3, 3), padding="same", activation=tf.nn.relu)
]

modelLayersV4 = \
[
    MultiConv([Conv2D(16, (21, 3), padding="same", activation=tf.nn.relu), Conv2D(16, (3, 21), padding="same", activation=tf.nn.relu), Conv2D(96, (13, 13), padding="same", activation=tf.nn.relu)]),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(64, (4, 4), (2, 2), padding="same", activation=tf.nn.relu),

    MultiConv([Conv2D(32, (21, 3), padding="same", activation=tf.nn.relu), Conv2D(32, (3, 21), padding="same", activation=tf.nn.relu), Conv2D(64, (7, 7), padding="same", activation=tf.nn.relu)]),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(128, (4, 4), (2, 2), padding="same", activation=tf.nn.relu),

    MultiConv([Conv2D(64, (21, 1), padding="same", activation=tf.nn.relu), Conv2D(64, (1, 21), padding="same", activation=tf.nn.relu), Conv2D(128, (7, 7), padding="same", activation=tf.nn.relu)]),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2DTranspose(256, (4, 4), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(3, (3, 3), padding="same", activation=tf.nn.relu)
]

imageProps = ImageProperties(128, 128, 96, WicGuid.WicPixelFormat96bppRGBFloat())
textProps = TextProperties("Arial", FontWeight.Normal, FontStretch.Normal, FontStyle.Normal, 0, 24)
textBounds = D2D1_RECT_F(10, 10, imageProps.imageWidth - 10, imageProps.imageHeight - 10)
textPool = "abcdefghijklmopqrstuvwxyz"

ImageDataGenerator.Initialize()
ImageDataGenerator.SetImageProperties(imageProps)
ImageDataGenerator.SetTextProperties(textProps)
ImageDataGenerator.SetTextBounds(textBounds)
ImageDataGenerator.SetTextPool(textPool)
ImageDataGenerator.SetFontList(availableFonts)

#dme = DetectionModelEvaluator(modelLayersV4, ImageDataGenerator, 1, 1, 1e-5, ImageDataGenerator.GetImageShape(), ImageDataGenerator.GetLabelShape())
#dme.EvaluateInteractively(ProgressReporter(1000, "The quick brown fox jumps over the lazy dog."))

dme = UNetModelEvaluator(ImageDataGenerator, 1, 1, 1e-5, ImageDataGenerator.GetImageShape(), ImageDataGenerator.GetLabelShape())
dme.EvaluateInteractively(ProgressReporter(1000, "The quick brown fox jumps over the lazy dog."))

if TextRenderer.IsInitialized:
    TextRenderer.Uninitialize()

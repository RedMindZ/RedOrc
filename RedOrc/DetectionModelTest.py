from tensorflow.layers import Conv2D, MaxPooling2D, Conv2DTranspose
from DetectionModelEvaluator import *
from ImageDataGenerator import *
import os

for f in os.listdir("ProgressReports"):
    os.remove("ProgressReports\\" + f)

for f in os.listdir("TensorboardLogs"):
    os.remove("TensorboardLogs\\" + f)

modelLayers = \
[
    Conv2D(64, (7, 7), padding="same", activation=tf.nn.relu),
    Conv2D(96, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2DTranspose(128, (3, 3), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(192, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2DTranspose(256, (3, 3), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(192, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2DTranspose(128, (3, 3), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(96, (3, 3), padding="same", activation=tf.nn.relu),
    Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu),
    MaxPooling2D((2, 2), (2, 2), "same"),
    Conv2DTranspose(64, (3, 3), (2, 2), padding="same", activation=tf.nn.relu),

    Conv2D(3, (7, 7), padding="same", activation=tf.nn.relu)
]

availableFonts = []
with open("ApprovedFonts.txt", "rt") as f:
    for font in f:
        availableFonts.append(font[:-1])

imageProps = ImageProperties(256, 256, 96, WicGuid.WicPixelFormat96bppRGBFloat())
textProps = TextProperties("Arial", FontWeight.Normal, FontStretch.Normal, FontStyle.Normal, 0, 24)
textBounds = D2D1_RECT_F(20, 20, imageProps.imageWidth - 20, imageProps.imageHeight - 20)
textPool = "abcdefghijklmopqrstuvwxyz"

ImageDataGenerator.Initialize()
ImageDataGenerator.SetImageProperties(imageProps)
ImageDataGenerator.SetTextProperties(textProps)
ImageDataGenerator.SetTextBounds(textBounds)
ImageDataGenerator.SetTextPool(textPool)

dme = DetectionModelEvaluator(modelLayers, ImageDataGenerator, 1, 1, 1e-5, [imageProps.imageHeight, imageProps.imageWidth, 3], [imageProps.imageHeight, imageProps.imageWidth, 3])
dme.Benchmark(1000000, 100)

ImageDataGenerator.Uninitialize()
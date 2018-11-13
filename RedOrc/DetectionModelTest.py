from tensorflow.layers import Conv2D, MaxPooling2D, Conv2DTranspose
from DetectionModelEvaluator import *
from ImageDataGenerator import *
from ProgressReporter import ProgressReporter
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

dme = DetectionModelEvaluator(modelLayers, ImageDataGenerator, 1, 1, 1e-5, ImageDataGenerator.GetImageShape(), ImageDataGenerator.GetLabelShape())
dme.EvaluateInteractively(ProgressReporter(1000, "The quick brown fox jumps over the lazy dog."))

if TextRenderer.IsInitialized:
    TextRenderer.Uninitialize()

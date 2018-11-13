import os
import numpy as np
import scipy.misc
from time import clock
from datetime import datetime, timedelta
from TextRenderer import *
from ImageDataGenerator import ImageDataGenerator

class ProgressReporter:
    def __init__(self, saveInterval, testText):
        self._save_interval = saveInterval
        self._test_text = testText
        self._test_images = ImageDataGenerator.GetTestImages(self._test_text)
        self._total_time = 0
        self._iter_count = 0

    def Report(self, iter, iterTime, maxIter, model, session, modelOutput):
        loss = modelOutput[0]
        summary = modelOutput[1]

        self._total_time += iterTime
        self._iter_count += 1
        timeLeft = int((maxIter - iter) * (self._total_time / self._iter_count))
        td = timedelta(seconds = timeLeft)
        eta = datetime.now() + td
        print("Iteration:", iter + 1, "|", "Loss:", format(loss, ".4f"), "|", "FPS:", format(1/(self._total_time / self._iter_count), ".2f"), "|", "ETA:", str(eta.hour) + ":" + str(eta.minute), "|", "Time left:", timeLeft, end="        \r")

        if (iter + 1) % self._save_interval == 0:
            fontList = ImageDataGenerator.GetFontList()

            for (i, image) in enumerate(self._test_images):
                rects = []
                mo = model.Predict([image], session)
                prediction = mo[0][0]
                predictionIndices = mo[1]

                for index in predictionIndices:
                    pixelIndex = tuple(index[1:])
                    rects.append(D2D1_RECT_F(pixelIndex[1], pixelIndex[0], pixelIndex[1] + prediction[pixelIndex][2], pixelIndex[0] + prediction[pixelIndex][1]))

                imageBuffer = np.copy(image)
                TextRenderer.RenderRectangles(rects, imageBuffer.ctypes.data_as(ctypes.c_void_p))
                TextRenderer.SaveImageAsPng("ProgressReports\\" + fontList[i] + "\\Step" + str(iter + 1) + ".png", imageBuffer.ctypes.data_as(ctypes.c_void_p))

        model.LogToTensorboard(summary, iter + 1)

    def SaveActivations(self, fontIndex, iter, model, session):
        fontList = ImageDataGenerator.GetFontList()

        activations = model.ComputeActivations([self._test_images[fontIndex]], session)
        activations = [actv[0] for actv in activations]
        actvDir = "ProgressReports\\" + fontList[fontIndex] + "\\Activations\\Step" + str(iter) + "\\"
        os.mkdir(actvDir)
        for (i, actv) in enumerate(activations):
            os.mkdir(actvDir + "Layer" + str(i) + "\\")
            for j in range(actv.shape[2]):
                scipy.misc.imsave(actvDir + "Layer" + str(i) + "\\" + "Channel" + str(j) + ".png", actv[:, :, j])

    def SaveFilters(self, iter, model, session):
        filters = model.GetConvolutionFilters(session)
        
        filtersDir = "Filters\\Step" + str(iter) + "\\"
        os.mkdir(filtersDir)
        for (i, convKernel) in enumerate(filters):
            os.mkdir(filtersDir + "Convolution" + str(i))
            for j in range(convKernel.shape[3]):
                os.mkdir(filtersDir + "Convolution" + str(i) + "\\Filter" + str(j))
                for k in range(convKernel.shape[2]):
                    scaledChannel = scipy.misc.imresize(convKernel[:, :, k, j], (convKernel.shape[0] * 20, convKernel.shape[1] * 20), mode='L', interp='nearest')
                    scipy.misc.imsave(filtersDir + "Convolution" + str(i) + "\\Filter" + str(j) + "\\" + "Channel" + str(k) + ".png", scaledChannel)
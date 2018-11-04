import numpy as np
from time import clock
from TextRenderer import *
from ImageDataGenerator import ImageDataGenerator

class ProgressReporter:
    def __init__(self, saveInterval, testText):
        self._save_interval = saveInterval
        self._test_text = testText
        self._test_images = ImageDataGenerator.GetTestImages(self._test_text)
        self._last_time = clock()

    def __call__(self, iter, model, session, modelOutput):
        #inputImages = modelOutput[0]
        #prediction = modelOutput[1]
        #predictionIndices = modelOutput[2]
        loss = modelOutput[3]
        summary = modelOutput[4]
        #label = modelOutput[5]
        #lossWeights = modelOutput[6]

        currTime = clock()
        print("Iteration:", iter + 1, "|", "Loss:", loss, "|", "FPS:", 1/(currTime - self._last_time), end="                \r")
        self._last_time = currTime

        if (iter + 1) % self._save_interval == 0:

            #prediction = label
            #rects = [[]] * inputImages.shape[0]
            #for index in predictionIndices:
            #    batchIndex = index[0]
            #    pixelIndex = tuple(index[1:])
            #    rects[batchIndex].append(D2D1_RECT_F(pixelIndex[1], pixelIndex[0], pixelIndex[1] + prediction[batchIndex][pixelIndex][2], pixelIndex[0] + prediction[batchIndex][pixelIndex][1]))
            #
            #for j in range(inputImages.shape[0]):
            #    TextRenderer.RenderRectangles(rects[j], inputImages[j].ctypes.data_as(ctypes.c_void_p))
            #    TextRenderer.SaveImageAsPng("ProgressReports\\Test\\Step" + str(iter + 1) + "Index" + str(j) + ".png", inputImages[j].ctypes.data_as(ctypes.c_void_p))



            fontList = ImageDataGenerator.GetFontList()

            for (j, image) in enumerate(self._test_images):
                rects = []
                mo = model.Predict([image], session)
                prediction = mo[0][0]
                predictionIndices = mo[1]

                for index in predictionIndices:
                    pixelIndex = tuple(index[1:])
                    rects.append(D2D1_RECT_F(pixelIndex[1], pixelIndex[0], pixelIndex[1] + prediction[pixelIndex][2], pixelIndex[0] + prediction[pixelIndex][1]))

                imageBuffer = np.copy(image)
                TextRenderer.RenderRectangles(rects, imageBuffer.ctypes.data_as(ctypes.c_void_p))
                TextRenderer.SaveImageAsPng("ProgressReports\\" + fontList[j] + "\\Step" + str(iter + 1) + ".png", imageBuffer.ctypes.data_as(ctypes.c_void_p))
            
            model.LogToTensorboard(summary, iter + 1)

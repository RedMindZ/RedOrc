import tensorflow as tf
import numpy as np
import keyboard
import os, shutil
from time import clock, sleep
from DetectionModel import DetectionModel
from ImageDataGenerator import ImageDataGenerator

class DetectionModelEvaluator:
    def __init__(self, layers, dataGen, batchSize, prefetchCount, learningRate=1e-5, inputShape=[None, None, 3], labelShape=[None, None, 3]):
        print("Setting up directories...")

        for d in os.listdir("ProgressReports\\"):
            shutil.rmtree("ProgressReports\\" + d)

        for d in os.listdir("Filters\\"):
            shutil.rmtree("Filters\\" + d)

        for f in os.listdir("TensorboardLogs"):
            os.remove("TensorboardLogs\\" + f)

        self._model = DetectionModel(layers, dataGen, batchSize, prefetchCount, learningRate, inputShape, labelShape)

    def EvaluateInteractively(self, progressReporter):
        
        availableFonts = ImageDataGenerator.GetFontList()
        
        for font in availableFonts:
            os.mkdir("ProgressReports\\" + font + "\\")
            os.mkdir("ProgressReports\\" + font + "\\Activations")

        keepRunning = True
        def pauseCallback():
            nonlocal keepRunning
            keepRunning = False
        hkr = keyboard.add_hotkey("ctrl+alt+p", pauseCallback)

        with tf.Session() as sess:
            self._model.InitVariables(sess)
            iter = 0

            while True:
                cmd = input("Action: ")

                if cmd.lower() == "t":
                    maxIter = iter + int(input("Iterations count: "))
                    keepRunning = True
                    while iter < maxIter and keepRunning:
                        startTime = clock()
                        modelOutput = self._model.TrainStep(sess)
                        endTime = clock()

                        progressReporter.Report(iter, endTime-startTime, maxIter, self._model, sess, modelOutput)
                        iter += 1

                elif cmd.lower() == "a":
                    fontName = input("Font: ")
                    fontFound = False
                    for (fontIndex, font) in enumerate(availableFonts):
                        if font.lower() == fontName.lower():
                            fontFound = True
                            progressReporter.SaveActivations(fontIndex, iter, self._model, sess)
                            break
                    if not fontFound:
                        print("The font specified is not available")
                
                elif cmd.lower() == "f":
                    progressReporter.SaveFilters(iter, self._model, sess)

                elif cmd.lower() == "s":
                    modelName = input("Model name: ")
                    self._model.Save(modelName, sess)
                    print("Model saved.")

                elif cmd.lower() == "l":
                    modelName = input("Model name: ")
                    try:
                        self._model.Load(modelName, sess)
                    except:
                        print("Could not load model \"" + modelName + "\".")
                    else:
                        print("Model loaded.")

                elif cmd.lower() == "e":
                    modelName = input("Model name: ")
                    self._model.ExportLite(modelName, sess)
                    print("Model exported.")

                elif cmd.lower() == "q":
                    shouldSave = input("Save model? [y/n]: ")
                    if shouldSave.lower() == "y":
                        modelName = input("Model name: ")
                        self._model.Save(modelName, sess)
                        print("Model saved.")

                    self._model.Close()

                    break

                print()
        
        keyboard.remove_hotkey(hkr)

    @staticmethod
    def postIter(iter, iterTime, maxIter, model, session, modelOutput):
        inputImages = modelOutput[0]
        prediction = modelOutput[1]
        predictionIndices = modelOutput[2]
        loss = modelOutput[3]
        summary = modelOutput[4]
        label = modelOutput[5]
        lossWeights = modelOutput[6]

        print("Iteration:", iter + 1, "|", "Loss:", loss, end="            \r")

        if (iter + 1) % 100 == 0:
            rects = [[]] * inputImages.shape[0]
            for index in predictionIndices:
                batchIndex = index[0]
                pixelIndex = tuple(index[1:])
                rects[batchIndex].append(D2D1_RECT_F(pixelIndex[1], pixelIndex[0], pixelIndex[1] + prediction[batchIndex][pixelIndex][2], pixelIndex[0] + prediction[batchIndex][pixelIndex][1]))

            for j in range(inputImages.shape[0]):
                TextRenderer.RenderRectangles(rects[j], inputImages[j].ctypes.data_as(ctypes.c_void_p))
                TextRenderer.SaveImageAsPng("ProgressReports\\Test\\Step" + str(iter + 1) + "Index" + str(j) + ".png", inputImages[j].ctypes.data_as(ctypes.c_void_p))
            
            model.LogToTensorboard(summary, iter + 1)
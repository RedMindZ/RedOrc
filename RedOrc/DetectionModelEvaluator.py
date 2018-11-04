import tensorflow as tf
import numpy as np
from DetectionModel import DetectionModel
from TextRenderer import *
import keyboard

class DetectionModelEvaluator:
    def __init__(self, layers, dataGen, batchSize, prefetchCount, learningRate=1e-4, inputShape=[None, None, 3], labelShape=[None, None, 3]):
        self._model = DetectionModel(layers, dataGen, batchSize, prefetchCount, learningRate, inputShape, labelShape)

    def EvaluateInteractively(self, postIterationAction):
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
                    trainingStepsCount = iter + int(input("Iterations count: "))
                    keepRunning = True
                    while iter < trainingStepsCount and keepRunning:
                        modelOutput = self._model.TrainStep(sess)
                        postIterationAction(iter, self._model, sess, modelOutput)
                        iter += 1
                
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

                elif cmd.lower() == "q":
                    shouldSave = input("Save model? [y/n]: ")
                    if shouldSave.lower() == "y":
                        modelName = input("Model name: ")
                        self._model.Save(modelName, sess)
                        print("Model saved.")

                    break

                print()
        
        keyboard.remove_hotkey(hkr)

    @staticmethod
    def postIter(iter, model, session, modelOutput):
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
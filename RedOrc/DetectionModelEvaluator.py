import tensorflow as tf
import numpy as np
from DetectionModel import DetectionModel
from TextRenderer import *

class DetectionModelEvaluator:
    def __init__(self, layers, dataGen, batchSize, prefetchCount, learningRate=1e-4, inputShape=[None, None, 3], labelShape=[None, None, 3]):
        self._model = DetectionModel(layers, dataGen, batchSize, prefetchCount, learningRate, inputShape, labelShape)

        total_parameters = 0
        for variable in tf.trainable_variables():
            shape = variable.get_shape()
            variable_parameters = 1
            for dim in shape:
                variable_parameters *= dim.value
            total_parameters += variable_parameters
        print("Total parameters:", total_parameters)

    def Benchmark(self, trainingStepsCount, progressReportIntervals):        
        with tf.Session() as sess:
            self._model.InitVariables(sess)

            for i in range(trainingStepsCount):
                modelOutput = self._model.TrainStep(sess)
                inputImages = modelOutput[0]
                prediction = modelOutput[1]
                predictionIndices = modelOutput[2]
                loss = modelOutput[3]
                summary = modelOutput[4]
                label = modelOutput[5]
                lossWeights = modelOutput[6]

                print("Iteration:", i, "|", "Loss:", loss, end="            \r")

                if (i + 1) % progressReportIntervals == 0:
                    rects = [[]] * inputImages.shape[0]
                    for index in predictionIndices:
                        batchIndex = index[0]
                        pixelIndex = tuple(index[1:])
                        rects[batchIndex].append(D2D1_RECT_F(pixelIndex[1], pixelIndex[0], pixelIndex[1] + prediction[batchIndex][pixelIndex][2], pixelIndex[0] + prediction[batchIndex][pixelIndex][1]))

                    for j in range(inputImages.shape[0]):
                        TextRenderer.RenderRectangles(rects[j], inputImages[j].ctypes.data_as(ctypes.c_void_p))
                        TextRenderer.SaveImageAsPng("ProgressReports\\Step" + str(i + 1) + "Index" + str(j) + ".png", inputImages[j].ctypes.data_as(ctypes.c_void_p))
                    
                    self._model.LogToTensorboard(summary, i + 1)

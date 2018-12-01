import tensorflow as tf
import numpy as np
from tensorflow.keras.layers import Conv2D, MaxPool2D, Conv2DTranspose, Concatenate
from MultiConv import MultiConv
from DetectionModel import DetectionModel
from DetectionModelEvaluator import DetectionModelEvaluator
import os
import shutil

class UNetModel(DetectionModel):
    def __init__(self, dataGen, batchSize, prefetchCount, learningRate=1e-5, inputShape=[None, None, 3], labelShape=[None, None, 3]):
        
        # Main model
        self._input_label_pipeline = tf.data.Dataset.from_generator(dataGen, (tf.float32, tf.float32, tf.float32), (inputShape, labelShape, labelShape))
        self._input_label_pipeline = self._input_label_pipeline.batch(batchSize)
        self._input_label_pipeline = self._input_label_pipeline.prefetch(prefetchCount)
        self._input_label_pipeline = self._input_label_pipeline.make_one_shot_iterator().get_next()

        self._input = tf.placeholder_with_default(self._input_label_pipeline[0], shape=([None, *inputShape]))
        self._activations = [self._input]
        self._conv_weights = []


        def DefaultConv2D(filters, kernel_size):
            init = tf.keras.initializers.glorot_normal()
            return Conv2D(filters, kernel_size, padding="same", activation=tf.nn.relu, kernel_initializer=init)

        def ApplyDefaultConv2D(inputs, filters, kernel_size):
            conv = DefaultConv2D(filters, kernel_size)
            output = conv.apply(inputs)
            self._conv_weights.append(conv.trainable_weights[0])
            self._activations.append(output)
            return output

        def DefaultConv2DTranspose(filters, kernel_size, strides):
            init = tf.keras.initializers.glorot_normal()
            return Conv2DTranspose(filters, kernel_size, strides, padding="same", activation=tf.nn.relu, kernel_initializer=init)

        def ApplyDefaultConv2DTranspose(inputs, filters, kernel_size, strides):
            conv = DefaultConv2DTranspose(filters, kernel_size, strides)
            applied = conv.apply(inputs)
            self._conv_weights.append(conv.trainable_weights[0])
            self._activations.append(applied)
            return applied

        def ApplyMaxPool2D(inputs, pool_size, strides):
            pool = MaxPool2D((2, 2), (2, 2), "same").apply(inputs)
            self._activations.append(pool)
            return pool

        def ApplyConcatenate(inputs, axis=-1):
            cat = Concatenate(axis).apply(inputs)
            self._activations.append(cat)
            return cat

        ## RedUNetV2
        ## Down
        #conv00 = MultiConv([Conv2D(16, (21, 3), padding="same", activation=tf.nn.relu), Conv2D(16, (3, 21), padding="same", activation=tf.nn.relu), Conv2D(32, (7, 7), padding="same", activation=tf.nn.relu)]).apply(self._input)
        #conv01 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(conv00)
        #conv02 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(conv01)
        #conv03 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(conv02)
        #conv04 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(conv03)
        #maxpool00 = MaxPooling2D((2, 2), (2, 2), "same").apply(conv04)
        #
        #conv10 = MultiConv([Conv2D(32, (14, 3), padding="same", activation=tf.nn.relu), Conv2D(32, (3, 14), padding="same", activation=tf.nn.relu), Conv2D(64, (7, 7), padding="same", activation=tf.nn.relu)]).apply(maxpool00)
        #conv11 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(conv10)
        #conv12 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(conv11)
        #conv13 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(conv12)
        #conv14 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(conv13)
        #maxpool10 = MaxPooling2D((2, 2), (2, 2), "same").apply(conv14)
        #
        ## Mid
        #conv20 = Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu).apply(maxpool10)
        #conv21 = Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu).apply(conv20)
        #conv22 = Conv2D(256, (3, 3), padding="same", activation=tf.nn.relu).apply(conv21)
        #
        ## Up
        #convT30 = Conv2DTranspose(256, (4, 4), (2, 2), padding="same", activation=tf.nn.relu).apply(conv22)
        #cat30 = Concatenate().apply([convT30, conv14])
        #conv30 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(cat30)
        #conv31 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(conv30)
        #conv32 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(conv31)
        #conv33 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(conv32)
        #conv34 = Conv2D(128, (3, 3), padding="same", activation=tf.nn.relu).apply(conv33)
        #
        #convT40 = Conv2DTranspose(128, (4, 4), (2, 2), padding="same", activation=tf.nn.relu).apply(conv34)
        #cat40 = Concatenate().apply([convT40, conv04])
        #conv40 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(cat40)
        #conv41 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(conv40)
        #conv42 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(conv41)
        #conv43 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(conv42)
        #conv44 = Conv2D(64, (3, 3), padding="same", activation=tf.nn.relu).apply(conv43)

        ## RedUNetV3
        ## Down
        #conv00 = MultiConv([DefaultConv2D(16, (21, 3)), DefaultConv2D(16, (3, 21)), DefaultConv2D(32, (7, 7))]).apply(self._input)
        #conv01 = ApplyDefaultConv2D(conv00, 64, (3, 3))
        #conv02 = ApplyDefaultConv2D(conv01, 64, (3, 3))
        #conv03 = ApplyDefaultConv2D(conv02, 64, (3, 3))
        #maxpool00 = ApplyMaxPool2D(conv03, (2, 2), (2, 2))
        #
        #conv10 = MultiConv([DefaultConv2D(32, (11, 3)), DefaultConv2D(32, (3, 11)), DefaultConv2D(64, (7, 7))]).apply(maxpool00)
        #conv11 = ApplyDefaultConv2D(conv10, 128, (3, 3))
        #conv12 = ApplyDefaultConv2D(conv11, 128, (3, 3))
        #conv13 = ApplyDefaultConv2D(conv12, 128, (3, 3))
        #conv14 = ApplyDefaultConv2D(conv13, 128, (3, 3))
        #conv15 = ApplyDefaultConv2D(conv14, 128, (3, 3))
        #maxpool10 = ApplyMaxPool2D(conv15, (2, 2), (2, 2))
        #
        ## Mid
        #conv20 = ApplyDefaultConv2D(maxpool10, 256, (3, 3))
        #conv21 = ApplyDefaultConv2D(conv20, 256, (3, 3))
        #conv22 = ApplyDefaultConv2D(conv21, 256, (3, 3))
        #conv23 = ApplyDefaultConv2D(conv22, 256, (3, 3))
        #conv24 = ApplyDefaultConv2D(conv23, 256, (3, 3))
        #conv25 = ApplyDefaultConv2D(conv24, 256, (3, 3))
        #conv26 = ApplyDefaultConv2D(conv25, 256, (3, 3))
        #
        ## Up
        #convT30 = ApplyDefaultConv2DTranspose(conv26, 128, (4, 4), (2, 2))
        #cat30 = ApplyConcatenate([convT30, conv15])
        #conv30 = ApplyDefaultConv2D(cat30, 256, (3, 3))
        #conv31 = ApplyDefaultConv2D(conv30, 128, (3, 3))
        #conv32 = ApplyDefaultConv2D(conv31, 128, (3, 3))
        #conv33 = ApplyDefaultConv2D(conv32, 128, (3, 3))
        #conv34 = ApplyDefaultConv2D(conv33, 128, (3, 3))
        #
        #convT40 = ApplyDefaultConv2DTranspose(conv34, 64, (4, 4), (2, 2))
        #cat40 = ApplyConcatenate([convT40, conv03])
        #conv40 = ApplyDefaultConv2D(cat40, 128, (3, 3))
        #conv41 = ApplyDefaultConv2D(conv40, 64, (3, 3))
        #conv42 = ApplyDefaultConv2D(conv41, 64, (3, 3))
        #conv43 = ApplyDefaultConv2D(conv42, 64, (3, 3))
        #conv44 = ApplyDefaultConv2D(conv43, 64, (3, 3))
        #conv45 = ApplyDefaultConv2D(conv44, 64, (3, 3))
        #conv46 = ApplyDefaultConv2D(conv45, 64, (3, 3))

        ## RedUNetV4
        ## Down
        #conv00 = MultiConv([DefaultConv2D(16, (21, 3)), DefaultConv2D(16, (3, 21)), DefaultConv2D(32, (7, 7))]).apply(self._input)
        #conv01 = ApplyDefaultConv2D(conv00, 64, (3, 3))
        #conv02 = ApplyDefaultConv2D(conv01, 64, (3, 3))
        #conv03 = ApplyDefaultConv2D(conv02, 64, (3, 3))
        #maxpool00 = ApplyMaxPool2D(conv03, (2, 2), (2, 2))
        #
        #conv10 = MultiConv([DefaultConv2D(32, (11, 3)), DefaultConv2D(32, (3, 11)), DefaultConv2D(64, (7, 7))]).apply(maxpool00)
        #conv11 = ApplyDefaultConv2D(conv10, 128, (3, 3))
        #conv12 = ApplyDefaultConv2D(conv11, 128, (3, 3))
        #conv13 = ApplyDefaultConv2D(conv12, 128, (3, 3))
        #maxpool10 = ApplyMaxPool2D(conv13, (2, 2), (2, 2))
        #
        #conv20 = ApplyDefaultConv2D(maxpool10, 256, (3, 3))
        #conv21 = ApplyDefaultConv2D(conv20, 256, (3, 3))
        #conv22 = ApplyDefaultConv2D(conv21, 256, (3, 3))
        #maxpool20 = ApplyMaxPool2D(conv22, (2, 2), (2, 2))
        #
        ## Mid
        #conv30 = ApplyDefaultConv2D(maxpool20, 512, (3, 3))
        #conv31 = ApplyDefaultConv2D(conv30, 512, (3, 3))
        #conv32 = ApplyDefaultConv2D(conv31, 512, (3, 3))
        #
        ## Up
        #convT40 = ApplyDefaultConv2DTranspose(conv32, 512, (4, 4), (2, 2))
        #cat40 = ApplyConcatenate([convT40, conv22])
        #conv40 = ApplyDefaultConv2D(cat40, 256, (3, 3))
        #conv41 = ApplyDefaultConv2D(conv40, 256, (3, 3))
        #conv42 = ApplyDefaultConv2D(conv41, 256, (3, 3))
        #
        #convT50 = ApplyDefaultConv2DTranspose(conv42, 256, (4, 4), (2, 2))
        #cat50 = ApplyConcatenate([convT50, conv13])
        #conv50 = ApplyDefaultConv2D(cat50, 128, (3, 3))
        #conv51 = ApplyDefaultConv2D(conv50, 128, (3, 3))
        #conv52 = ApplyDefaultConv2D(conv51, 128, (3, 3))
        #
        #convT60 = ApplyDefaultConv2DTranspose(conv52, 128, (4, 4), (2, 2))
        #cat60 = ApplyConcatenate([convT60, conv03])
        #conv60 = ApplyDefaultConv2D(cat60, 64, (3, 3))
        #conv61 = ApplyDefaultConv2D(conv60, 64, (3, 3))
        #conv62 = ApplyDefaultConv2D(conv61, 64, (3, 3))

        # RedUNetV5
        # Down
        conv00 = MultiConv([DefaultConv2D(16, (21, 3)), DefaultConv2D(16, (3, 21)), DefaultConv2D(32, (7, 7))]).apply(self._input)
        conv01 = ApplyDefaultConv2D(conv00, 64, (3, 3))
        conv02 = ApplyDefaultConv2D(conv01, 64, (3, 3))
        conv03 = ApplyDefaultConv2D(conv02, 64, (3, 3))
        maxpool00 = ApplyMaxPool2D(conv03, (2, 2), (2, 2))
        
        conv10 = MultiConv([DefaultConv2D(32, (11, 3)), DefaultConv2D(32, (3, 11)), DefaultConv2D(64, (5, 5))]).apply(maxpool00)
        conv11 = ApplyDefaultConv2D(conv10, 128, (3, 3))
        conv12 = ApplyDefaultConv2D(conv11, 128, (3, 3))
        conv13 = ApplyDefaultConv2D(conv12, 128, (3, 3))
        maxpool10 = ApplyMaxPool2D(conv13, (2, 2), (2, 2))
        
        conv20 = MultiConv([DefaultConv2D(64, (11, 3)), DefaultConv2D(64, (3, 11)), DefaultConv2D(128, (3, 3))]).apply(maxpool10)
        conv21 = ApplyDefaultConv2D(conv20, 256, (3, 3))
        conv22 = ApplyDefaultConv2D(conv21, 256, (3, 3))
        maxpool20 = ApplyMaxPool2D(conv22, (2, 2), (2, 2))
        
        # Mid
        conv30 = ApplyDefaultConv2D(maxpool20, 512, (3, 3))
        conv31 = ApplyDefaultConv2D(conv30, 512, (3, 3))
        conv32 = ApplyDefaultConv2D(conv31, 512, (3, 3))
        
        # Up
        convT40 = ApplyDefaultConv2DTranspose(conv32, 512, (4, 4), (2, 2))
        cat40 = ApplyConcatenate([convT40, conv22])
        conv40 = MultiConv([DefaultConv2D(64, (11, 3)), DefaultConv2D(64, (3, 11)), DefaultConv2D(128, (3, 3))]).apply(cat40)
        conv41 = ApplyDefaultConv2D(conv40, 256, (3, 3))
        conv42 = ApplyDefaultConv2D(conv41, 256, (3, 3))
        
        convT50 = ApplyDefaultConv2DTranspose(conv42, 256, (4, 4), (2, 2))
        cat50 = ApplyConcatenate([convT50, conv13])
        conv50 = MultiConv([DefaultConv2D(32, (11, 3)), DefaultConv2D(32, (3, 11)), DefaultConv2D(64, (5, 5))]).apply(cat50)
        conv51 = ApplyDefaultConv2D(conv50, 128, (3, 3))
        conv52 = ApplyDefaultConv2D(conv51, 128, (3, 3))
        
        convT60 = ApplyDefaultConv2DTranspose(conv52, 128, (4, 4), (2, 2))
        cat60 = ApplyConcatenate([convT60, conv03])
        conv60 = MultiConv([DefaultConv2D(16, (21, 3)), DefaultConv2D(16, (3, 21)), DefaultConv2D(32, (7, 7))]).apply(cat60)
        conv61 = ApplyDefaultConv2D(conv60, 64, (3, 3))
        conv62 = ApplyDefaultConv2D(conv61, 64, (3, 3))



        self._output = ApplyDefaultConv2D(conv62, 3, (3, 3))
        self._output_indices = tf.where(tf.greater(self._output[0:, 0:, 0:, 0], 0.5))
        
        # Training
        self._label = self._input_label_pipeline[1]
        self._loss_weights = self._input_label_pipeline[2]
        self._loss = tf.losses.mean_squared_error(self._label, self._output, self._loss_weights)
        self._optimizer = tf.train.AdamOptimizer(learningRate)
        self._mop = self._optimizer.minimize(self._loss)

        # Saver
        self._saver = tf.train.Saver()

        # Tensorboard
        tf.summary.scalar("Loss", self._loss)
        self._summary = tf.summary.merge_all()
        self._file_writer = tf.summary.FileWriter("TensorboardLogs", tf.get_default_graph())

class UNetModelEvaluator(DetectionModelEvaluator):
    def __init__(self, dataGen, batchSize, prefetchCount, learningRate = 1e-5, inputShape = [...], labelShape = [...]):
        print("Setting up directories...")

        for d in os.listdir("ProgressReports\\"):
            shutil.rmtree("ProgressReports\\" + d)

        for d in os.listdir("Filters\\"):
            shutil.rmtree("Filters\\" + d)

        for f in os.listdir("TensorboardLogs"):
            os.remove("TensorboardLogs\\" + f)

        self._model = UNetModel(dataGen, batchSize, prefetchCount, learningRate, inputShape, labelShape)

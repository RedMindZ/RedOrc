import tensorflow as tf
from tensorflow.keras.layers import Layer, Concatenate

class MultiConv(Layer):
    def __init__(self, convs, channelsAxis=-1, trainable = True, name = None, dtype = None):
        super().__init__(trainable, name, dtype)

        self.convs = convs
        self.concat = Concatenate(channelsAxis)

    def build(self, input_shape):
        for conv in self.convs:
            conv.build(input_shape)
        self.concat.build([conv.compute_output_shape(input_shape) for conv in self.convs])

        super().build(input_shape)

    def call(self, inputs, **kwargs):
        appliedConvs = []
        for conv in self.convs:
            appliedConvs.append(conv.call(inputs))

        return self.concat.call(appliedConvs)
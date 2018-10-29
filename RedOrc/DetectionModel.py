import tensorflow as tf

class ConvProps:
    def __init__(self, filtersCount, kernelSize, strides=(1, 1), activation=tf.nn.relu):
        self.filtersCount = filtersCount
        self.kernelSize = kernelSize
        self.strides = strides
        self.activation = activation

class PoolProps:
    def __init__(self, size, strides):
        self.size = size
        self.strides = strides

class DetectionModel:
    def __init__(self, convProps, poolProps, transConvProps, dataGen, batchSize, prefetchCount):
        #layerCount = len(filterCounts)
        #if layerCount < 1:
        #    raise ValueError("A model must have at leaset one layer.")
        #
        #if len(kernelSizes) != layerCount or len(poolingStrides) != layerCount or len(poolingSizes) != layerCount:
        #    raise ValueError("All model arguments must be of the exact same length.")

        layerCount = len(convProps)
        if len(poolProps) != layerCount or len(transConvProps) != layerCount:
            raise ValueError("All model arguments must be of the exact same length.")
        
        # Main model
        self._input_label_pipeline = tf.data.Dataset.from_generator(dataGen, (tf.float32, tf.float32), ([None, None, 3], [None, None, 3]))
        self._input_label_pipeline = self._input_label_pipeline.batch(batchSize)
        self._input_label_pipeline = self._input_label_pipeline.prefetch(prefetchCount)
        self._input_label_pipeline = self._input_label_pipeline.make_one_shot_iterator().get_next()

        self._input = tf.placeholder_with_default(self._input_label_pipeline[0], shape=[None, None, None, 3])
        
        self._convolutions = []
        self._pools = []
        self._transposed_convolutions = []

        convStride = (1, 1)
        
        #self._convolutions.append(tf.layers.conv2d(self._input, filterCounts[0], kernelSizes[0], convStride, "same", activation=tf.nn.relu))
        #self._pools.append(tf.layers.max_pooling2d(self._convolutions[-1], poolingSizes[0], poolingStrides[0], "same"))
        #self._transposed_convolutions.append(tf.layers.conv2d_transpose(self._pools[-1], filterCounts[0], kernelSizes[0], poolingStrides[0], "same", activation=tf.nn.relu))
        #
        #for i in range(1, layerCount):
        #    self._convolutions.append(tf.layers.conv2d(self._transposed_convolutions[-1], filterCounts[i], kernelSizes[i], convStride, "same", activation=tf.nn.relu))
        #    self._pools.append(tf.layers.max_pooling2d(self._convolutions[-1], poolingSizes[i], poolingStrides[i], "same"))
        #    self._transposed_convolutions.append(tf.layers.conv2d_transpose(self._pools[-1], filterCounts[i], kernelSizes[i], poolingStrides[i], "same", activation=tf.nn.relu))

        lastLayer = self._input

        for i in range(layerCount):
            if convProps[i] != None:
                lastLayer = tf.layers.conv2d(lastLayer, convProps[i].filtersCount, convProps[i].kernelSize, convProps[i].strides, "same", activation=convProps[i].activation)
            
            if poolProps[i] != None:
                lastLayer = tf.layers.max_pooling2d(lastLayer, poolProps[i].size, poolProps[i].strides, "same")
            
            if transConvProps[i] != None:
                lastLayer = tf.layers.conv2d_transpose(lastLayer, transConvProps[i].filtersCount, transConvProps[i].kernelSize, transConvProps[i].strides, "same", activation=transConvProps[i].activation)

        #self._output = self._transposed_convolutions[-1]
        self._output = lastLayer
        self._output_indices = tf.where(tf.greater(self._output[0:, 0:, 0:, 0], 0.5))
        
        # Training
        self._label = self._input_label_pipeline[1]
        self._loss = tf.losses.mean_squared_error(self._label, self._output)
        #self._loss = tf.reduce_max(tf.square(self._label - self._output))
        self._optimizer = tf.train.AdamOptimizer(1e-5)
        self._mop = self._optimizer.minimize(self._loss)

        # Tensorboard
        tf.summary.scalar("Loss", self._loss)
        self._summary = tf.summary.merge_all()
        self._file_writer = tf.summary.FileWriter("TensorboardLogs", tf.get_default_graph())

    def InitVariables(self, session):
        session.run(tf.global_variables_initializer())

    def Predict(self, inputImages, session):
        return session.run([self._output, self._output_indices], { self._input : inputImages })

    def TrainStep(self, session):
        return session.run([self._input, self._output, self._output_indices, self._loss, self._summary, self._label, self._mop])[0:-1]

    def LogToTensorboard(self, summary, step):
        self._file_writer.add_summary(summary, step)
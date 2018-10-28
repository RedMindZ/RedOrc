import tensorflow as tf

class DetectionModel:
    def __init__(self, filterCounts, kernelSizes, poolingStrides, poolingSizes, dataGen, batchSize, prefetchCount):
        layerCount = len(filterCounts)
        if layerCount < 1:
            raise ValueError("A model must have at leaset one layer.")

        if len(kernelSizes) != layerCount or len(poolingStrides) != layerCount or len(poolingSizes) != layerCount:
            raise ValueError("All model arguments must be of the exact same length.")
        
        # Main model
        self._input_label_pipeline = tf.data.Dataset.from_generator(dataGen, (tf.float32, tf.float32), ([None, None, 3], [None, None, filterCounts[-1]]))
        self._input_label_pipeline = self._input_label_pipeline.batch(batchSize)
        self._input_label_pipeline = self._input_label_pipeline.prefetch(prefetchCount)
        self._input_label_pipeline = self._input_label_pipeline.make_one_shot_iterator().get_next()

        self._input = tf.placeholder_with_default(self._input_label_pipeline[0], shape=[None, None, None, 3])
        
        self._convolutions = []
        self._pools = []
        self._transposed_convolutions = []

        convStride = (1, 1)
        self._convolutions.append(tf.layers.conv2d(self._input, filterCounts[0], kernelSizes[0], convStride, "same", activation=tf.nn.relu))
        self._pools.append(tf.layers.max_pooling2d(self._convolutions[-1], poolingSizes[0], poolingStrides[0], "same"))
        self._transposed_convolutions.append(tf.layers.conv2d_transpose(self._pools[-1], filterCounts[0], kernelSizes[0], poolingStrides[0], "same", activation=tf.nn.relu))

        for i in range(1, layerCount):
            self._convolutions.append(tf.layers.conv2d(self._transposed_convolutions[-1], filterCounts[i], kernelSizes[i], convStride, "same", activation=tf.nn.relu))
            self._pools.append(tf.layers.max_pooling2d(self._convolutions[-1], poolingSizes[i], poolingStrides[i], "same"))
            self._transposed_convolutions.append(tf.layers.conv2d_transpose(self._pools[-1], filterCounts[i], kernelSizes[i], poolingStrides[i], "same", activation=tf.nn.relu))

        self._output = self._transposed_convolutions[-1]
        self._output_indices = tf.where(tf.greater(self._output[0:, 0:, 0:, 0], 0.5))
        
        # Training
        self._label = self._input_label_pipeline[1]
        self._loss = tf.losses.mean_squared_error(self._label, self._output)
        #self._loss = tf.reduce_max(tf.square(self._label - self._output))
        self._optimizer = tf.train.AdamOptimizer(5e-5)
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
        return session.run([self._input, self._output, self._output_indices, self._loss, self._summary, self._mop])[0:-1]

    def LogToTensorboard(self, summary, step):
        self._file_writer.add_summary(summary, step)
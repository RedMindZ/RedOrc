import tensorflow as tf

class DetectionModel:
    def __init__(self, layers, dataGen, batchSize, prefetchCount, learningRate=1e-4, inputShape=[None, None, 3], labelShape=[None, None, 3]):
        
        # Main model
        self._input_label_pipeline = tf.data.Dataset.from_generator(dataGen, (tf.float32, tf.float32, tf.float32), (inputShape, labelShape, labelShape))
        self._input_label_pipeline = self._input_label_pipeline.batch(batchSize)
        self._input_label_pipeline = self._input_label_pipeline.prefetch(prefetchCount)
        self._input_label_pipeline = self._input_label_pipeline.make_one_shot_iterator().get_next()

        self._input = tf.placeholder_with_default(self._input_label_pipeline[0], shape=([None, *inputShape]))
        
        lastLayer = self._input
        for layer in layers:
            lastLayer = layer.apply(lastLayer)

        self._output = lastLayer
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

    def InitVariables(self, session):
        session.run(tf.global_variables_initializer())

    def Save(self, name, session):
        self._saver.save(session, "Models\\" + name + ".ckpt")

    def Load(self, name, session):
        self._saver.restore(session, "Models\\" + name + ".ckpt")

    def Predict(self, inputImages, session):
        return session.run([self._output, self._output_indices], { self._input : inputImages })

    def TrainStep(self, session):
        return session.run([self._input, self._output, self._output_indices, self._loss, self._summary, self._label, self._loss_weights, self._mop])[0:-1]

    def LogToTensorboard(self, summary, step):
        self._file_writer.add_summary(summary, step)
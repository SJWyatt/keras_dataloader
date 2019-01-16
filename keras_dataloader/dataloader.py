from concurrent.futures import ThreadPoolExecutor

import keras
import numpy as np

from keras_dataloader.dataset import Dataset


class DataGenerator(keras.utils.Sequence):

    def __init__(self,
                 dataset: Dataset,
                 batch_size=32,
                 shuffle=True,
                 num_workers=0,
                 replacement: bool = False
                 ):
        """

        :param dataset (Dataset): Data set to load
        :param batch_size (int): how many samples in one batch
        :param shuffle (bool, optional): set to ``True`` to have the data reshuffled
            at every epoch (default: ``True``).
        :param num_workers (int, optional): how many threads to use for data
            loading in one batch. 0 means that the data will be loaded in the main process.
            (default: ``0``)
        :param replacement (bool): samples are drawn with replacement if ``True``, default=False
        """
        self.dataset = dataset
        self.shuffle = shuffle
        self.batch_size = batch_size
        self.num_workers = num_workers
        self.replacement = replacement
        self.indices = []
        self.on_epoch_end()

    def __getitem__(self, index):
        indices = self.indices[index * self.batch_size: (index + 1) * self.batch_size]

        X, Y = [], []
        if self.num_workers == 0:
            for i in indices:
                data = self.dataset[i]
                X.append(data[0])
                Y.append(data[1])
        else:
            with ThreadPoolExecutor(max_workers=self.num_workers) as executor:
                for x, y in executor.map(lambda i: self.dataset[i], indices):
                    X.append(x)
                    Y.append(y)
        X, Y = np.array(X), np.array(Y)
        return X, Y

    def on_epoch_end(self):
        n = len(self.dataset)
        seq = np.arange(0, n)
        if self.shuffle:
            if self.replacement:
                self.indices = np.random.randint(low=0, high=n, size=(n,),
                                                 dtype=np.int64).tolist()
            else:
                np.random.shuffle(seq)
                self.indices = seq
        else:
            self.indices = seq

    def __len__(self):
        return int(np.floor(len(self.dataset) / self.batch_size))

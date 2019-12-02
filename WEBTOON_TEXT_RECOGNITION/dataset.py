import pandas as pd
import numpy as np
import imgproc
import torch
import file_utils
import random
import config
from scipy.ndimage.interpolation import map_coordinates
from scipy.ndimage.filters import gaussian_filter
from PIL import Image, ImageFilter

class Hangul_Dataset(object):

    def __init__(self, csv_path=None, label_path=None, image_size=None, train=None):
        self.data = pd.read_csv(csv_path)
        self.size = image_size
        self.images = self.data.iloc[:, 0]
        self.labels = np.asarray(self.data.iloc[:, 1])
        self.labels_num = np.asarray(self.data.iloc[:, 2])
        self.allLabels = file_utils.loadText(label_path)
        self.labelOneHotVector = torch.zeros([len(self.allLabels)], dtype=torch.long)
        self.FLAG = train

    def __getitem__(self, index):
        if self.FLAG: return self.train_data_transform(index)
        else: return self.test_data_transform(index)

    def __len__(self):
        return len(self.data.index)

    def test_data_transform(self, index):
        image = imgproc.loadImage(self.images[index])
        image = imgproc.cvtColorGray(image)
        image = imgproc.tranformToTensor(img=image, size=self.size)

        label = self.labels[index]
        label_num = self.labels_num[index]

        return image, label_num

    def train_data_transform(self, index):
        image = imgproc.loadImage(self.images[index])
        image = imgproc.cvtColorGray(image)

        #Data Augmentation Method - elastic distotion, image blur

        #if random.randint(0, 1):
        #    image = self.distortImage(image)
        #if random.randint(0, 1):
        #     blur_extent = 1
        #    image = self.blurImage(image, blur_extent)

        image = imgproc.tranformToTensor(img=image, size=self.size)

        label = self.labels[index]
        label_num = self.labels_num[index]

        return image, label_num

    def distortImage(self, img):

        alpha = random.randint(config.ALPHA_MIN, config.ALPHA_MAX)
        sigma = random.randint(config.SIGMA_MIN, config.SIGMA_MAX)

        random_state = np.random.RandomState(None)
        shape = img.shape

        dx = gaussian_filter(
            (random_state.rand(*shape) * 2 - 1),
            sigma, mode="constant"
        ) * alpha
        dy = gaussian_filter(
            (random_state.rand(*shape) * 2 - 1),
            sigma, mode="constant"
        ) * alpha

        x, y = np.meshgrid(np.arange(shape[0]), np.arange(shape[1]))
        indices = np.reshape(y + dy, (-1, 1)), np.reshape(x + dx, (-1, 1))
        distorted_arr = map_coordinates(img, indices, order=1).reshape(shape)
        #image = Image.fromarray(distorted_arr)
        return distorted_arr

    def blurImage(self, img, extent):
        img = Image.fromarray(img)
        img = img.filter(ImageFilter.GaussianBlur(radius=extent))
        return np.array(img)

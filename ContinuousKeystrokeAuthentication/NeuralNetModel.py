from sklearn.model_selection import validation_curve
from sklearn.utils import shuffle

import tensorflow as tf
from tensorflow import keras

from keras import layers
from keras.callbacks import LearningRateScheduler

import numpy as np
import math

import h5py

# import matplotlib.pyplot as plt

print("Num GPUs Available: ", len(tf.config.list_physical_devices('GPU')))

sess = tf.compat.v1.Session(config=tf.compat.v1.ConfigProto(log_device_placement=True))
from tensorflow.python.client import device_lib
print(device_lib.list_local_devices())

class NeuralNetModel:
    
    def __init__(self):
        pass
    



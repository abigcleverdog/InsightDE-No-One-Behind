import pika

import os, sys, time, random
import threading
from threading import Thread, Event
import cv2

import json
import numpy as np
from collections import deque

import mysql.connector as db_con


CASC_FILE = "haarcascade_frontalface_default.xml"
SERVERS=[""" <List of RabbitMQ server ip's """]
QUEUE_VID = 'vid00'
QUEUE_DATA = 'vid01'
FRAME_EX_RATE = 10
VID_THROUGHPUT_SIZE = (300,200)
VID_ROLLING = True # False #

def rb_connect(servers):
    credentials = pika.credentials.PlainCredentials('<user name>', '<password>', erase_on_connect=False)
    connection = None
    random.shuffle(servers)
    for server in servers:
        try:
            parameters = pika.ConnectionParameters(server,
                                       5672,
                                       'myvid',
                                       credentials)
            connection = pika.BlockingConnection(parameters)
            break
        except:
            pass
            
    return connection
    

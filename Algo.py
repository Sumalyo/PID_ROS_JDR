#!/usr/bin/python
#-*- coding: utf-8 -*-
import threading
import time
from datetime import datetime

import math
import cv2
import numpy as np

time_cycle = 80

class MyAlgorithm(threading.Thread):

    def __init__(self, camera, motors):
        self.camera = camera
        self.motors = motors
        self.threshold_image = np.zeros((640,360,3), np.uint8)
        self.color_image = np.zeros((640,360,3), np.uint8)
        self.stop_event = threading.Event()
        self.kill_event = threading.Event()
        self.lock = threading.Lock()
        self.threshold_image_lock = threading.Lock()
        self.color_image_lock = threading.Lock()
        threading.Thread.__init__(self, args=self.stop_event)
    
    def getImage(self):
        self.lock.acquire()
        img = self.camera.getImage().data
        self.lock.release()
        return img

    def set_color_image (self, image):
        img  = np.copy(image)
        if len(img.shape) == 2:
          img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        self.color_image_lock.acquire()
        self.color_image = img
        self.color_image_lock.release()
        
    def get_color_image (self):
        self.color_image_lock.acquire()
        img = np.copy(self.color_image)
        self.color_image_lock.release()
        return img
        
    def set_threshold_image (self, image):
        img = np.copy(image)
        if len(img.shape) == 2:
          img = cv2.cvtColor(img, cv2.COLOR_GRAY2RGB)
        self.threshold_image_lock.acquire()
        self.threshold_image = img
        self.threshold_image_lock.release()
        
    def get_threshold_image (self):
        self.threshold_image_lock.acquire()
        img  = np.copy(self.threshold_image)
        self.threshold_image_lock.release()
        return img

    def run (self):

        while (not self.kill_event.is_set()):
            start_time = datetime.now()
            if not self.stop_event.is_set():
                self.algorithm()
            finish_Time = datetime.now()
            dt = finish_Time - start_time
            ms = (dt.days * 24 * 60 * 60 + dt.seconds) * 1000 + dt.microseconds / 1000.0
            #print (ms)
            if (ms < time_cycle):
                time.sleep((time_cycle - ms) / 1000.0)

    def stop (self):
        self.stop_event.set()

    def play (self):
        if self.is_alive():
            self.stop_event.clear()
        else:
            self.start()

    def kill (self):
        self.kill_event.set()

    def algorithm(self):
        #GETTING THE IMAGES
        image = self.getImage()
	
	
        # Add your code here
        print "Runing Tse 9"

        #EXAMPLE OF HOW TO SEND INFORMATION TO THE ROBOT ACTUATORS
        #self.motors.sendV(10)
	#self.motors.sendW(2)
        #self.motors.sendW(5)
	trn = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
	lower = np.array([10,10,10], dtype = "uint8")
	upper = np.array([255,255,255], dtype = "uint8")
	mask=cv2.inRange(trn,lower,upper)
	h, w, d = image.shape
    	search_top = 3*h/4
    	search_bot = 3*h/4 + 20
    	mask[0:search_top, 0:w] = 0
    	mask[search_bot:h, 0:w] = 0
	M = cv2.moments(mask)
    	if M['m00'] > 0:
		cx = int(M['m10']/M['m00'])
		cy = int(M['m01']/M['m00'])
      		#cv2.circle(image, (cx, cy), 20, (0,0,255), -1# BEGIN CONTROL
		err = cx - w/2
		self.motors.sendV(2)
		self.motors.sendW(-float(err) / 100)
		#print err
	res = cv2.bitwise_and(image,image,mask = mask)
	#SHOW THE FILTERED IMAGE ON THE GUI
        self.set_threshold_image(res)

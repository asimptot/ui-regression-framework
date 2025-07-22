import glob, re, math
import os, uuid, random, logging, traceback
from collections import Counter
import numpy as np
from skimage.metrics import structural_similarity as ssim
import cv2, warnings, ctypes
from PIL import Image
from datetime import datetime
from time import sleep
import undetected_chromedriver as uc
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class Setup:
    def __init__(self):
        ctypes.windll.kernel32.SetThreadExecutionState(
            ctypes.c_uint(0x80000002)
        )

        options = uc.ChromeOptions()
        options.add_argument('--headless=new')
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        self.browser = uc.Chrome(options=options, version_main=138)
        self.set_device_metrics(3816, 2049, 0.75, mobile=False)
        self.actions = webdriver.ActionChains(self.browser)
        self.current_results_dir = 'logs'
        warnings.filterwarnings("ignore")

    def set_device_metrics(self, width, height, device_scale_factor, mobile=False):
        self.browser.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
            "width": width,
            "height": height,
            "deviceScaleFactor": device_scale_factor,
            "mobile": mobile,
        })

    def login(self):
        WebDriverWait(self.browser, 20).until(
            EC.presence_of_element_located((By.ID, "YOUR ELEMENT ID"))
        ).send_keys('YOUR USERNAME')

        self.actions.send_keys(Keys.RETURN).perform()
        WebDriverWait(self.browser, 10).until(
            EC.presence_of_element_located((By.ID, "YOUR ELEMENT ID"))
        ).send_keys('YOUR PASSWORD')

        sleep(5)
        self.actions.send_keys(Keys.RETURN).perform()
        sleep(5)
        self.actions.send_keys(Keys.RETURN).perform()
        sleep(1)

    def close_browser(self):
        if self.browser:
            try:
                self.browser.quit()
            except Exception as e:
                print(f"An error occurred while closing the browser: {e}")
            finally:
                self.browser = None

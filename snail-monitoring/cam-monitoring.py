# Camera monitoring

# Loading libraries
from pypylon import pylon
from PIL import Image
import numpy as np
import time
from datetime import datetime
import os

IMGS_FOLDER = "data"

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())
camera.Open()

# able auto exposure if set
camera.ExposureAuto.Value = 'Continuous'

# demonstrate some feature access
new_width = camera.Width.Value - camera.Width.Inc
if new_width >= camera.Width.Min:
    camera.Width.Value = new_width

numberOfImagesToGrab = 100
camera.StartGrabbingMax(numberOfImagesToGrab)

while camera.IsGrabbing():
    grabResult = camera.RetrieveResult(5000, pylon.TimeoutHandling_ThrowException)

    if grabResult.GrabSucceeded():
        # Access the image data.
        img = grabResult.Array

         # Convert the image to PIL format and save as JPG
        img_pil = Image.fromarray(img)
        
        # Create a filename based on the current timestamp
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S-%f')
        filename = f"{IMGS_FOLDER}/image_{timestamp}.jpg"
        
        # Save the image
        img_pil.save(filename)
        print(f"Saved {filename}")

        # Wait for 0.5 seconds before capturing the next image
        # time.sleep(0.5)

    grabResult.Release()
camera.Close()
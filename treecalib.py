#!/usr/bin/env python3

import numpy as np
import cv2
import sys
from ledcontroller import LEDController
from ledfinder import LEDFinder

def calibrate(numleds, videodevnumber=0, minpixels=20):
    # Cretate dict with mapping id -> pixelpos
    mapping_dict = {}

    # create video capture
    cap = cv2.VideoCapture(videodevnumber)

    ledc = LEDController(numleds)
    ledf = LEDFinder(minpixels)

    for i in range(numleds):
        # turn led on
        ledc.set_single_led(i)

        # grab image
        _, img = cap.read()

        # find ledposition
        coords = ledf.fing_led_coords(img)
        
        # add ledpos to dict if it was found
        if(coords):
            mapping_dict[i] = coords

    cap.release()
    cv2.destroyAllWindows()

def export_mapping(path, mapping):
    np.savetxt(path, np.array([[i,x,y] for (i,(x,y)) in mapping.items()], dtype=int))

if __name__ == '__main__':
    numleds = None
    export_path = None
    if len(sys.argv) != 3:
        print('Wrong number of arguments!')
        print('Usage: python treecalib.py <# LEDs> <export_path>')
        sys.exit(-1)
    else:
        numleds = int(sys.argv[1])
        export_path = sys.argv[2]
        
    mapping_dict = calibrate(numleds, 2)
    export_mapping(export_path, mapping_dict)
    

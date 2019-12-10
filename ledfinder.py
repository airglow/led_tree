#!/usr/bin/env python3

import cv2
import numpy as np
import sys

class LEDFinder:
    def __init__(self, minpixels):
        self.minpixels = minpixels

    def find_led_coords(self, img, margin=0.95, vis=False):

        # convert image to grey level image
        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        regions = self._getBrightRegions(grey_img, margin, vis)

        # select regions based on their aspect ratios
        led_region = self._filter_regions_ar(regions)

        if(vis):
            if(led_region):
                pt1 = (led_region[0], led_region[1])
                pt2 = (led_region[0]+led_region[2], led_region[1]+led_region[3])
                cv2.rectangle(img, pt1, pt2, (0,0,255), 2)
            cv2.imshow('bboxs', img)
            cv2.waitKey(0)

        if(led_region):
            (x,y,w,h) = led_region
            return (x + w//2, y + h//2)
        else:
            return None

    def _filter_regions_ar(self, regions):
        aspect_ratios = []
        for (_,_,w,h) in regions:
            if(w < h):
                aspect_ratios.append(w/h)
            else:
                aspect_ratios.append(h/w)

        # return region which is nearest to aspect_ratio 1:1 (square)
        return regions[np.argmax(aspect_ratios)]

    def  _getBrightRegions(self, grey_img, margin=0.95, vis=False):

        # Search for brightest pixels
        _, maxVal, _, maxLoc = cv2.minMaxLoc(grey_img)

        thresh = int(maxVal*margin)
        _, thresh_img = cv2.threshold(grey_img, thresh, 255, cv2.THRESH_BINARY)
        if(vis):
            cv2.imshow('thresh', thresh_img)
            cv2.waitKey(0)

        contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        regions = []

        for contour in contours:
            if len(contour) > self.minpixels:
                contour = np.squeeze(contour)
                # find coordinates of bounding box
                x, y = min(contour[:,0]), min(contour[:,1])
                w, h = max(contour[:,0]) - x, max(contour[:,1]) - y
                regions.append((x, y, w, h))
                
        return regions


if __name__ == '__main__':
    imgpath = None
    if len(sys.argv) != 2:
        print('Wrong number of arguments!')
        print('Usage: python ledfinder.py <imagepath>')
        sys.exit(-1)
    else:
        imgpath = sys.argv[1]

    ledf = LEDFinder(30)
    img = cv2.imread(imgpath)
    coords = ledf.find_led_coords(img)
    print(coords)


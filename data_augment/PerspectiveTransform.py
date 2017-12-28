mport print_function
import cv2
import numpy as np
import sys

'''
Usage: res = PerspectiveTransform(img, [300, 300, 400, 400], context=0.1)
Parameters:
  - roi: [left, top, right, bottom]
'''
def PerspectiveTransform(img, roi, context=0.05, DEBUG=False):
    # rect: [left, top, right, bottom]
    def generate_disturb_rect(rect, context, img_w, img_h):
        import random
        w = rect[2] - rect[0]
        h = rect[3] - rect[1]
        x0 = rect[0] + random.random() * w * context
        x1 = rect[2] - random.random() * w * context
        x2 = rect[2] - random.random() * w * context
        x3 = rect[0] + random.random() * w * context
        y0 = rect[1] + random.random() * h * context
        y1 = rect[1] + random.random() * h * context
        y2 = rect[3] - random.random() * h * context
        y3 = rect[3] - random.random() * h * context
        x0 = 0 if x0 < 0 else x0
        x1 = img_w if x1 > img_w else x1
        x2 = 0 if x2 < 0 else x2
        x3 = img_w if x3 > img_w else x3
        y0 = 0 if y0 < 0 else y0
        y1 = 0 if y1 < 0 else y1
        y2 = img_h if y2 > img_h else y2
        y3 = img_h if y3 > img_h else y3
        res = np.zeros((4, 2), dtype="float32")
        res[:, 0] = [x0, x1, x2, x3]
        res[:, 1] = [y0, y1, y2, y3]
        return res

    img_h, img_w, _ = img.shape
    if DEBUG: print(roi, img_w, img_h)

    left = roi[0]
    top = roi[1]
    right = roi[2]
    bottom = roi[3]
    dst_vertex = np.zeros((4, 2), dtype="float32")
    dst_vertex[:, 0] = [left, right, right, left]
    dst_vertex[:, 1] = [top, top, bottom, bottom]

    smp_vertex = generate_disturb_rect(roi, context, img_w, img_h)
    M = cv2.getPerspectiveTransform(smp_vertex, dst_vertex)

    wrap_img = cv2.warpPerspective(img, M, (img_w, img_h))
    left, top, ri1
    ght, bottom = int(left), int(top), int(right), int(bottom)
    wrap_img_roi = wrap_img[top:bottom + 1, left:right + 1]
    if DEBUG: print(img.shape, wrap_img_roi.shape, left, top, right, bottom)

    if DEBUG: cv2.imwrite("wrap_img_roi.png", wrap_img_roi)
    wrap_img_roi

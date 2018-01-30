#from __future__ import print_function
import cv2
import numpy as np
import sys
import os
import argparse

'''
Usage: res = PerspectiveTransform(img, [300, 300, 400, 400], context=0.1)
Parameters:
  - roi: [left, top, right, bottom]
'''
parser = argparse.ArgumentParser()
parser.add_argument('--input_path',default = '')
parser.add_argument('--output_path',default = '')
parser.add_argument('--context',default = '0.1')
args = parser.parse_args()
class DataArgu():
    def __init__(self, input_path, output_path):
        self.input_path_ = input_path
        self.output_path_ = output_path
        if not os.path.exists(os.path.join(self.output_path_)):
            os.mkdir(self.output_path_)

    @staticmethod
    def PerspectiveTransform(img, roi, context=0.05):
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
    
        left = roi[0]
        top = roi[1]
        right = roi[2]
        bottom = roi[3]
        dst_vertex = np.zeros((4, 2), dtype="float32")
        dst_vertex[:, 0] = [left, right, right, left]
        dst_vertex[:, 1] = [top, top, bottom, bottom]
    
        smp_vertex = generate_disturb_rect(roi, context, img_w, img_h)
        M = cv2.getPerspectiveTransform(smp_vertex, dst_vertex)
        print dst_vertex
        print roi
        wrap_img = cv2.warpPerspective(img, M, (img_w, img_h))
        return wrap_img
    
    def ReadAnno(self,anno_file,context):
        fin = open(anno_file, 'r').readlines()                           
        img_names = np.array(map(lambda x: x.strip().split(' ')[0], fin))
        fi = anno_file.split('/')[-1].split('.')[-2]
        new_anno = os.path.join(self.output_path_,fi + '_perspective_context_' + str(context).replace('.', '_') + '.anno')
        f_anno = open(new_anno,'w')
        print 'new_anno:',new_anno
        rects = np.array(map(lambda x: np.array(map(float, x.strip().split(' ')[1:])).reshape(-1, 5), fin))
        for idx in range(len(fin)):
            img_path = os.path.join(self.input_path_, img_names[idx])
            writeImgPath = os.path.join(fi + '_perspective_context_' + str(context).replace('.', '_'),img_names[idx].split('/')[-1])
            f_anno.write(writeImgPath)
            print 'writeImgPath:',writeImgPath
            print 'img_path:',img_path
            if not os.path.exists(os.path.join(img_path)):
                print(img_path)
                continue
            img_name = img_names[idx].split('/')[-1]
            img_save_dir = os.path.join(self.output_path_, img_names[idx].split('/')[0] + '_perspective_context_'+ str(context).replace('.', '_'))
            print 'img_save_dir:',img_save_dir
            if not os.path.exists(os.path.join(img_save_dir)):
                os.mkdir(os.path.join(img_save_dir))
            img = cv2.imread(img_path)                                    
            img_h, img_w, _ = img.shape
            for rect in rects[idx]:                                       
                x1, y1, x2, y2, cls = map(int, rect)
                f_anno.write(' ' + str(x1) + ' ' + str(y1) + ' ' + str(x2) + ' ' + str(y2) + ' ' + str(cls))
                roi = [x1, y1, x2, y2]
                if (cls <= 1):
                    h_size = (y2 - y1) * context
                    w_size = (x2 - x1) * context
                    if h_size <= 0.0 or w_size <= 0.0:
                        continue
                    #add context
                #    if x1 - w_size < 0.0 or y1 - h_size < 0.0 or x2 + w_size > img_w or y2 + w_size > img_h:
                #        continue 
                    crop_img_x1 = x1 - w_size if x1 - w_size >= 0.0 else 0.0
                    crop_img_y1 = y1 - h_size if y1 - h_size >= 0.0 else 0.0 
                    crop_img_x2 = x2 + w_size if x2 + w_size <= img_w else img_w
                    crop_img_y2 = y2 + h_size if y2 + h_size <= img_h else img_h  
                    cropped_img = img[int(crop_img_y1):int(crop_img_y2), int(crop_img_x1):int(crop_img_x2)]
                    roi[2] = roi[2] - roi[0] + w_size 
                    roi[3] = roi[3] - roi[1] + h_size 
                    roi[0] = w_size
                    roi[1] = h_size
                    temp_img = self.PerspectiveTransform(cropped_img, roi, context=context)                                                        
                    img[int(crop_img_y1):int(crop_img_y2), int(crop_img_x1):int(crop_img_x2)] = temp_img
            img_name = img_path.strip().split('/')[-1] 
            print img_name
            f_anno.write('\n')
            cv2.imwrite(os.path.join(img_save_dir, img_name), img)
    
    def ReadAllAnnos(self,context): 
        my_path = self.input_path_
        anno_file_list = []
        for root,dir,files in os.walk(my_path):
            for file in files:
                if '.anno' in file:
                    anno_file_list.append(os.path.join(root,file))
                else:
                    pass
        print 'anno_file_list:',anno_file_list

        for anno_file in anno_file_list:
            self.ReadAnno(anno_file,context)
if __name__ == '__main__':
    context = args.context.split(',')
    context_list = [float(x) for x in context]
    db = DataArgu(args.input_path,args.output_path)
    for context in context_list:
        db.ReadAllAnnos(context)

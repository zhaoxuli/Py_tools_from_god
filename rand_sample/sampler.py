import numpy as np
import os
import cv2
import argparse

class RandomCropper():
    def __init__(self, min_contain_overlap, min_w, max_w, min_h, max_h,   
                 label_width, input_path, save_path):
        self.min_contain_overlap_ = float(min_contain_overlap)
        self.min_w_ = float(min_w)
        self.max_w_ = float(max_w)
        self.min_h_ = float(min_h)
        self.max_h_ = float(max_h)
        self.label_width_ = label_width 
        self.img_path_ = input_path
        self.input_path_ = input_path
        self.save_path_ = save_path

    def GenLabel(self, cropped_img_coord, boxes, box_length=5):
        """
        boxes dimension (n, box_length)
        """
        line = ''
        for box in boxes:
            percent = self.ContainPercent(cropped_img_coord, box)
            if percent >= self.min_contain_overlap_:
                new_box = self.NewCoord(box, cropped_img_coord)
                line += ' '
                line += ' '.join(map(str, new_box))
            elif percent > 0.3 and percent < self.min_contain_overlap_:
                box[4] = 1 
                new_box = self.NewCoord(box, cropped_img_coord)
                line += ' '
                line += ' '.join(map(str, new_box))
            elif percent > 0.0 and percent < 0.3:
                box[4] = 2 
                new_box = self.NewCoord(box, cropped_img_coord)
                line += ' '
                line += ' '.join(map(str, new_box))
        return line
                
    def ContainPercent(self, cropped_img_coord, box):
        img_x1, img_y1, img_x2, img_y2 = cropped_img_coord
        x1, y1, x2, y2 = box[0:4]
        inter_area = 0.0
        l = max(x1, img_x1)
        t = max(y1, img_y1)
        r = min(x2, img_x2)
        b = min(y2, img_y2)
        if l >= r or t >= b:
            inter_area =0.0 
        else:
            inter_area = (r - l) * (b - t)
        box_area = (x2 - x1) * (y2 - y1)
        return inter_area / box_area

    def NewCoord(self, box, cropped_img_coord):
        x1, y1, x2, y2 = box[0:4]
        img_x1, img_y1, img_x2, img_y2 = cropped_img_coord
        new_x1 = x1 - img_x1 if x1 > img_x1 else 0.0
        new_y1 = y1 - img_y1 if y1 > img_y1 else 0.0 
        new_x2 = img_x2 - img_x1 if x2 > img_x2 else x2 - img_x1
        new_y2 = img_y2 - img_y1 if y2 > img_y2 else y2 - img_y1

        box[0] = new_x1
        box[1] = new_y1
        box[2] = new_x2
        box[3] = new_y2 
        return box

    def GenCrop(self, img_h, img_w):
        width = np.random.uniform(self.min_w_, self.max_w_)
        height = np.random.uniform(self.min_h_, self.max_h_)
        x1 = np.random.uniform(0., img_w - width)
        y1 = np.random.uniform(0., img_h - height)
        return x1, y1, x1 + width, y1 + height


    def ProcessAnno(self):
        my_path = self.input_path_ 
        file_list = [os.path.join(my_path, fi) for fi in os.listdir(my_path) if os.path.isfile(os.path.join(my_path, fi))]
        for fi in file_list:
            if '.anno' in fi:
                self.GenImgAndAnnotation(os.path.join(my_path, fi))

    def GenImgAndAnnotation(self, annotation_path):
        #create dir and annotation names for cropped images and new annotation file respectively
        annotation_fname = annotation_path.strip().split('/')[-1].split('.')[0]
        save_dir_name = annotation_fname + '_random_crop'
        save_dir_path = os.path.join(self.save_path_, save_dir_name)
        save_annotation_name = annotation_fname + '_random_crop.anno'
        save_annotation_path = os.path.join(self.save_path_, save_annotation_name)
        #create dir for saving images
        if not os.path.exists(save_dir_path):
            os.mkdir(os.path.join(save_dir_path))
        #create annotation file for saving after-cropped annotation 
        fout = open(save_annotation_path, 'w')
        label = open(annotation_path, 'r').readlines()
        img_names = np.array(map(lambda x : x.strip().split()[0], label))
        print annotation_path 
        boxes = np.array(map(lambda x : np.array(map(float, x.strip().split()[1:])).reshape(-1, self.label_width_), label))
        for idx in range(img_names.shape[0]):
            if boxes[idx].shape[0] == 0:
                continue
            img = cv2.imread(os.path.join(self.img_path_, img_names[idx]))
            if img is None:
                continue
            h, w, _ = img.shape
            crop_x1, crop_y1, crop_x2, crop_y2 = self.GenCrop(img_h=h, img_w=w)
            cropped_img = img[crop_y1:crop_y2, crop_x1:crop_x2]
            line = self.GenLabel([crop_x1, crop_y1, crop_x2, crop_y2], boxes[idx])
            img_name = img_names[idx].split('/')[-1]
            #resize_cropped_img = cv2.resize(cropped_img, (w, h))
            cv2.imwrite(os.path.join(save_dir_path, img_name), cropped_img)
            line = os.path.join(save_dir_name, img_name) + line
            print >>fout, line
        fout.close() 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_path')
    parser.add_argument('--save_path')
    parser.add_argument('--min_contain_overlap')
    parser.add_argument('--min_width')
    parser.add_argument('--max_width')
    parser.add_argument('--min_height')
    parser.add_argument('--max_height')
    args = parser.parse_args()
    crop = RandomCropper(min_contain_overlap=args.min_contain_overlap, min_w=args.min_width, max_w=args.max_width,
                         min_h=args.min_height, max_h=args.max_height, label_width=5, input_path=args.input_path, save_path=args.save_path)
    crop.ProcessAnno()


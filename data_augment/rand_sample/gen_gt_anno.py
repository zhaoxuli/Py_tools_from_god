#!/usr/bin/python
# -*- coding:utf-8 -*-

# Convert json to anno file
# Author zhangyi, Colin Chu
# updated by Shiya Liu
# Date 2017.06.23

import os, sys, time
import json
import numpy as np
from ts_dict import ts_dict 

def MatchJsonAndPack(module_test_fpath, anno_fpath, output_fpath):
    anno_l = open(anno_fpath, 'r').readlines()
    module_l = open(module_test_fpath, 'r').readlines()
    module_out = open(output_fpath + '/merged_pack.anno', 'w')
    anno_out = open(output_fpath + '/merged_anno.anno', 'w')
    img_key_l = [line.strip().split(' ')[0] for line in anno_l]
    img_key_dict = {}
    for idx, element in enumerate(img_key_l):
        img_key_dict[element] = idx 
    for line in module_l:
        line = line.strip()
        temp_key = line.split(' ')[0]
        if temp_key in img_key_dict.keys():
            src_prefix = '_'.join(temp_key.split('_')[0:-1])
            module_out.write(src_prefix + '/' + line.strip() + '\n')
            anno_out.write(src_prefix + '/' + anno_l[img_key_dict[temp_key]].strip() + '\n')
    anno_out.close()
    module_out.close()


def GenAnno(gt_l, output_file, output_dir):
    anno_l = []
    for idx, gt in enumerate(gt_l):
        image_key, rects = gt
        anno_line = output_file + '/' + image_key
  #      anno_line = image_key
        for l, t, r, b, ign in rects:
            anno_line += ' {:.1f} {:.1f} {:.1f} {:.1f} {:d}'.format(
                          l, t, r, b, ign)
        anno_l.append(anno_line)
    fname = output_dir + output_file + ".anno" 
    fid = open(fname, 'wt')
    for anno in anno_l:
        print>>fid, anno
    fid.close()
 
     

def correct_rect(rect):
    x1, y1, x2, y2 = rect
    left = min(x1, x2)
    right = max(x1, x2)
    top = min(y1, y2)
    bottom = max(y1, y2)
    return [left, top, right, bottom]


def hard_rect(rect):
    hard_by_size = False
    w = (rect[2] - rect[0]) if rect[2] > rect[0] else 0
    h = (rect[3] - rect[1]) if rect[3] > rect[1] else 0
    hard_by_size = (w * h < 100)
    return hard_by_size


def generate_gt(json_fpath, obj_type):
    gt_list = [] # [image_name, rect4, ignore]
    if not os.path.exists(json_fpath):
        print "Error:", json_fpath, " not exists. Exit:."
        sys.exit(-1)
    fp = open(json_fpath)
    lines = fp.readlines()
    fp.close()
    for line in lines:
        data = json.loads(line)
        img_name = data['image_key']
        rects = []
	if not data.has_key(obj_type):
            gt_list.append((img_name, rects))
            continue
        labels = data[obj_type]
        for label in labels:
            rect = map(float, label['data'])
            rect = correct_rect(rect)
            if label['attrs'].has_key('ignore') and label['attrs']['ignore'] == 'yes':
            	rect.append(2) # rect with ign
            elif label['attrs'].has_key('occlusion') and \
                (label['attrs']['occlusion'] == 'heavily_occluded' or label['attrs']['occlusion'] == 'invisible'):
                rect.append(1)
            else:
                rect.append(0)
            #print rect
            rects.append(rect)
        # append all samples in this image
        gt_list.append((img_name, rects))

    return gt_list

def GenerateAnnoFile(json_dir, data_dir, smp_dir, obj_type):
    test_dir = smp_dir + '/'
    if not os.path.exists(test_dir):
        os.mkdir(test_dir)
    for json_fn in os.listdir(json_dir):
        json_fpath = os.path.join(json_dir, json_fn)
        if '.json' not in json_fn:
            continue
        fname, tmp = json_fn.split('.')
        img_dir = os.path.join(data_dir, fname)
        gt_list = generate_gt(json_fpath, obj_type)
        print len(gt_list)
        print json_fn
        GenAnno(gt_list, fname, test_dir)


def MergeAllFilesInDir(path, pattern, output_fpath):
    if os.path.exists(output_fpath):
        print "%s output file exists, removed" % (output_fpath)
        os.remove(output_fpath)
    fout = open(output_fpath, 'a+')
    for fn in os.listdir(path):
        if pattern not in fn:
            continue
        fpath = os.path.join(path, fn)
        lines = open(fpath, 'r').readlines()
        for line in lines:
            print >> fout, line.strip()
    fout.close()


def CopyFilesInDir(path, pattern, dst_dir):
    for fn in os.listdir(path):
        if pattern not in fn:
            continue
        print fn
        cmd = "cat %s/%s > %s/%s" % (path, fn, dst_dir, fn)
        os.popen(cmd)



import sys, os
from gen_gt_anno import *
from subprocess import Popen
import glob

#json_fpath = '/home/users/shiya.liu/sample_generator/alpha-plus-sample-generator/ts_train/'
#json_fpath = '/home/users/shiya.liu/caffe/caffe-for-horizonrobotics/examples/traffic_light/ts_cnn/out/smp/train/10555_1/'
#json_fpath = '/home/users/shiya.liu/sample_generator/alpha-plus-sample-generator/tl_test/'
#json_fpath = '/home/users/shiya.liu/download/HDS_TOOLS/ts/'
#json_fpath = './tl_test/'
#json_fpath = '/mnt/hdfs-data-1/adas/shiyaliu/ts_data/'
json_fpath = '/home/users/shiya.liu/sample_generator/alpha-plus-sample-generator/tl_test/'
obj_type = 'common_box'
out_dir = '/home/users/shiya.liu/sample_generator/alpha-plus-sample-generator/tl_test/'
#merge all files into a single file
merged_anno_fpath = out_dir + '/merged.txt'
#generate anno files for each json file
GenerateAnnoFile(json_fpath, '', out_dir, obj_type)
#merge all anno files
MergeAllFilesInDir(out_dir, '.anno', merged_anno_fpath)




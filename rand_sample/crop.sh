#!/bin/bash
img_path=/mnt/hdfs-data-1/adas/shiyaliu/tl_train_data_bak/
save_path=/mnt/hdfs-data-1/adas/shiyaliu/tl_train_data_more_data_crop/
min_contain_overlap=0.7
min_width=640
max_width=1280
min_height=360
max_height=720

python sampler.py --input_path=${img_path} --save_path=${save_path} --min_contain_overlap=${min_contain_overlap} --min_width=${min_width} --max_width=${max_width} --min_height=${min_height} --max_height=${max_height}



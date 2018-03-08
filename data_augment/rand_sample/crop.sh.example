#!/bin/bash
img_path=/mnt/hdfs-data-1/adas/shiyaliu/road_sign_halfsize/
save_path=/mnt/hdfs-data-1/adas/shiyaliu/road_sign_halfsize_crop/
min_contain_overlap=0.7
min_width=0.5
max_width=1.0
min_height=0.5
max_height=1.0

python sampler.py --input_path=${img_path} --save_path=${save_path} --min_contain_overlap=${min_contain_overlap} --min_width=${min_width} --max_width=${max_width} --min_height=${min_height} --max_height=${max_height}



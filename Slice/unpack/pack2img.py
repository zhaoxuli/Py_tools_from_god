import cv2
import os, sys
import numpy as np
import argparse
import ParsePack


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pack_path', help='Input path of your pack')

    args = parser.parse_args()
    return args

def pack2img():
    pack_path = args.pack_path
    pack_split = pack_path.split('/')
    pack_name = pack_split[len(pack_split)-1]
    pack_pic_anno = open('pack_pic_list.anno','w')
    #print pack_name
    #sys.exit(-1)
    if not os.path.exists('pack_pics'):
        os.mkdir('pack_pics')

    pack = ParsePack.Pack()
    pack.loadFile(pack_path)
    #print len(pack.protoLens)
    for i in range(len(pack.protoLens)):
        pic = pack.getImageByIdx(i)
        cv2.imwrite('./pack_pics/'+pack_name+'_'+str(i)+'.png', pic)
        pack_pic_anno.write(pack_name+'_'+str(i)+'.png'+'\n')

if __name__ == "__main__":
    args = parse_args()
    pack2img(args)

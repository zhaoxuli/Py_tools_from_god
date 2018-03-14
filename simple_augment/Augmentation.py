# -*- coding: utf-8 -*-
import time
import  cv2
import copy as cp
import numpy as np
#from skimage  import exposure

def Contrast(img,k=0.7):
    dst = cp.deepcopy(img)
    Avg = dst.mean()
    dst = (img-Avg)*k + img
    print 'finish constrat'
    return dst

def EquHist(img):
    w,h,c = img.shape
    dst = cp.deepcopy(img)
    for i in range(c):
        img[:,:,i] = cv2.equalizeHist(img[:,:,i])
    return img

def  Illuminate(img):
    gamma1 = float(np.random.randint(1,19))/10
    illu_img= exposure.adjust_gamma(img_data, gamma1)
    return  illu_img

def local_high(img,alpha,b=10,k1=0.2,k2=0.3):
    #k1,k2 is the range of img_size  defalut 0.2-0.3
   # bias = np.random.randint(0,b)
   # value = img[w,h,c]*alpha +bias
    #mask = zeros(img.shape)
    img_w,img_h,img_c = img.shape
    dst = cp.deepcopy(img)
    x_loc = np.random.randint(1,img_w)
    y_loc = np.random.randint(1,img_h)
    width = np.random.randint(img_w*k1,img_w*k2)
    height  = np.random.randint(img_h*k1,img_h*k2)
    if x_loc < int(img_w/2):
        x_loc_end = x_loc + width
    else :
        x_loc_end = x_loc
        x_loc = x_loc - width
    if y_loc < int(img_h/2):
        y_loc_end = y_loc + height
    else :
        y_loc_end = y_loc
        y_loc = y_loc - height
   # print x_loc,x_loc_end,'       ',y_loc,y_loc_end
    for w in range(x_loc,x_loc_end):
        for h in range(y_loc,y_loc_end):
            for c in range(img_c):
                bias = np.random.randint(0,b)
                value = img[w,h,c]*alpha +bias
                if value > 255:
                    value = 255
                if value < 0:
                    value = 0
                dst[w,h,c] = value
    return dst


def noise(img,type_noise,kernel_size=(5,5),sigma=0,slat_ratio=0.008,papper_radtio=0.01):
    img_w,img_h,img_c = img.shape
    if type_noise == 'gaussian':
        img = cv2.GaussianBlur(img,kernel_size,sigma)

    if type_noise == 'salt':
        count_all = img.shape[0] * img.shape[1]
        salt_num = int(count_all*slat_ratio)
        for n in range(salt_num):
            m = np.random.randint(1,img_w)
            n = np.random.randint(1,img_h)
            for c in range(img_c):
                img[m,n,c] = 255

    if type_noise == 'papper':
        count_all = img.shape[0] * img.shape[1]
        papper_num = int(count_all*papper_ratio)
        for n in range(papper_num):
            m = np.random.randint(1,img_w)
            n = np.random.randint(1,img_h)
            for c in range(img_c):
                img[m,n,c] = 0


    if type_noise == 'all':
        img = cv2.GaussianBlur(img,kernel_size,sigma)
        count_all = img.shape[0] * img.shape[1]
        salt_num = int(count_all*slat_ratio)
        for n in range(salt_num):
            m = np.random.randint(1,img_w)
            n = np.random.randint(1,img_h)
            rand_key = np.random.randint(0,2)
            if rand_key ==1:
                for c in range(img_c):
                    img[m,n,c] = 255
            else:
                for c in range(img_c):
                    img[m,n,c] = 0
    return img


def rotate(img,center,angle,scale=1):
    #rotate_format: x_new = int(x_old*np.sin(angle) + y_old*np.cos(angle))
    img_w,img_h,img_c = img.shape
    print img.shape
    if center == 'normal':
        center_points = (img_w/2,img_h/2)
    if center == 'random':
        width = img_w*0.1
        height = img_h*0.1
        x = np.random.randint(img_w/2-width , img_w/2+width)
        y = np.random.randint(img_h/2-height , img_h/2+height)
        center_points = (x,y)

    M = cv2.getRotationMatrix2D(center_points ,angle, scale)
    rotated = cv2.warpAffine(img,M,(img_h,img_w))
    #old_x = 60
    #old_y = 40
    #old_points =[old_x ,old_y]


    #new_points = get_new_points(old_points,center_points,angle,scale)
    #new_x = new_points[0] #+img_w/2
    #new_y = new_points[1] #+img_h/2


    #print rotated.shape
    #print old_points,'......',int(new_x),int(new_y)
    #print 'Rotated:  ',rotated[int(new_x),int(new_y)]
    #print 'Before:   ',img[60,120]

    #cv2.circle(img,(old_x,old_y),3,(0,0,255),-1)
    #cv2.circle(rotated,(int(new_x),int(new_y)),3,(0,0,255),-1)
    #cv2.imshow('old',img)
    #cv2.imshow('rotate',rotated)
    #c = chr(255&cv2.waitKey(0))

    return  rotated

def rotate_det(img,center,angle,scale,old_points):
    img_w,img_h,img_c = img.shape
    print img.shape
    if center == 'normal':
        center_points = (img_w/2,img_h/2)
    if center == 'random':
        width = img_w*0.1
        height = img_h*0.1
        x = np.random.randint(img_w/2-width , img_w/2+width)
        y = np.random.randint(img_h/2-height , img_h/2+height)
        center_points = (x,y)

    old_x = old_points[0]
    old_y = old_points[1]

    M = cv2.getRotationMatrix2D(center_points ,angle, scale)
    new_points = get_new_points(old_points,center_points,angle,scale)

    rotated = cv2.warpAffine(img,M,(img_h,img_w))

    return rotated,new_points

def get_new_points(old_points,center_points,angle,scale):
    angle = (angle*np.pi)/180
    old_x = old_points[0][:]
    old_y = old_points[1][:]

    center_x = center_points[0]
    center_y = center_points[1]

    loc_x = old_x - center_x
    loc_y = old_y - center_y

    new_x = int(loc_x*np.cos(angle)*scale + loc_y*np.sin(angle)*scale + center_x)
    new_y = int(-loc_x*np.sin(angle)*scale + loc_y*np.cos(angle)*scale + center_y)

    return [new_x,new_y]

if __name__ == '__main__':

    img_url = './test.png'

    src = cv2.imread(img_url)
    dst = cp.deepcopy(src)

    a_time = time.clock()
    rote_img = rotate(dst,'normal',20,0.8)
    b_time = time.clock()
    print 'Rotate_cost: ',b_time - a_time

    a_time = time.clock()
    noise_img  = noise(dst,'all')
    b_time = time.clock()
    print 'Noise_cost: ',b_time - a_time

    a_time = time.clock()
    const = Contrast(dst,0.7)
    b_time = time.clock()
    print 'Contrast_cost: ',b_time - a_time

    a_time = time.clock()
    equ = EquHist(dst)
    b_time = time.clock()
    print 'EquHist_cost: ',b_time - a_time
   #illu_img = Illuminate(src)
    a_time = time.clock()
    local_h  = local_high(src,1.2)
    b_time = time.clock()
    print 'Local_h: ',b_time - a_time

    cv2.imshow('src',src)
    cv2.imshow('rotated',rote_img)
    cv2.imshow('noise',noise_img)
    #cv2.imshow('illuminate',illu_img)
    cv2.imshow('lcl_h',local_h)
    cv2.imshow('contrast',const)
    cv2.imshow('equ',equ)
    c = chr(255&cv2.waitKey(0))
























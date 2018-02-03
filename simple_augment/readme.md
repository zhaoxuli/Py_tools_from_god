**该脚本主要提供了几种不同的数据增强方式的函数**

 主要有：对比度增强，直方图均衡，亮度提高，局部亮（暗）斑，噪声（椒盐/高斯），基于角度/缩放的放射变换

* Constrast 对比度增强
```
 函数：Contrast(img,k=0.7)
 //k为增强系数，默认为0.7
 参照公式：value = (img[w][h][c] - Avg)*k + img[w,h][c]
```
* EquHist  直方图均衡
```
opencv 默认直方图均衡函数
cv2.equalizeHist()
```
* Illuminate 亮度增强
```
需要skimage 扩展库支持
exposure.adjust_gamma(img_data, gamma1)
默认gamma 为随机数
```
* local_high 局部亮（暗）块
```
函数定义：local_high(img,alpha,b=10,k1=0.2,k2=0.3)
公式参考：value = img[w,h,c]*alpha +bias
         bias = np.random.randint(0,b)
//alpha 为增强系数   b为偏置系数，默认为10
//k1 k2 为噪声块大小系数默认0.2，0.3
    width = np.random.randint(img_w*k1,img_w*k2)
    height  = np.random.randint(img_h*k1,img_h*k2)
```
* noise 噪声(椒盐/高斯)
```
函数定义： noise(img,type_noise,kernel_size=(5,5),sigma=0,slat_ratio=0.008,papper_radtio=0.01)
//type_noise   可选为'gaussian' 'salt' 'papper'  'all'
//kernal_size,sigma 为gaussian 算子参数默认（5，5） 0
//slat_ratio  为slat 噪声数量系数，默认0.008
//             公式参考：salt_num = int(count_all*slat_ratio)
//papper_ratio 为papper 噪声数量系数，默认0.01
//              公式参考：papper_num = int(count_all*papper_ratio)
//另外如果 type_noise == all,首先会进行高斯模糊，之后会按照salt_ratio得//到的噪声点随机取papper 或者salt噪声点
```
* rotate 旋转/仿射变换（分类）
```
函数定义：rotate(img,center,angle,scale=1)
//center 有两种可选:normal/random
//       为normal 时仿射变换的旋转点位于图片中心
//       为random 时仿射变换的旋转点随机在图片中心的（-0.1*point，+0.1*point）之间
//angle  进行仿射变换的角度
//scale  缩放系数，默认为1，即不进行缩放
```
* rotate_det 旋转/仿射变换 （检测）
```
函数定义：rotate_det(img,center,angle,scale,old_points)
//其余参数参考rotate ,old_points为gt点
```

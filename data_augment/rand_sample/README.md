# Function:  
this script will crop part of image from original images and resize cropped image to original size. 
this is one of data argumentation method used in SSD, YOLO and etc.

# How to use  
open crop.sh file and there are 5 parameters users need to specify.  
- input_path: specify data directory. users need to put all images dirs and image annotations files in this directory. 
            the name of annotations file and corresponding image directory should match each other.  
            ex. annotations file name: 1000_2.anno directory name: 1000_2 
  
- save_path:  directory for output data. 
  
- min_contain_overlap: specify minimum contain overlap between single box with cropped image. ex. if this value is set to 0.5, it means that 
                     if 50% of ground truth box is in this cropped image, this box will be kept and all ignore attribute will be copied from original annotations file.   
                     if contain overlap is between 0 and 0.5, this box will be labeled as ignore.  
                     if less than 0.0, this box will be threw away.  
  
- min_width: minimum width of cropped image. all cropped images will be resized to original size.    
- max_width: maximum width of crooped image. all cropped images will be resized to original size.   
  
after filled all parameters, just type `bash crop.sh` and it will generate results in save_path which users specified.   


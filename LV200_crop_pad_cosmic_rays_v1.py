from tkinter import filedialog
from tkinter import *
import os, re, shutil, re
import numpy as np
#from matplotlib import pyplot as plt
#import scipy
#from scipy import ndimage, misc
import cv2
#from PIL import Image
from skimage import io
import skimage
import datetime  as dt
import imageio
from skimage.transform import rescale, resize, downscale_local_mean
from skimage.transform import warp_polar, rotate
from skimage import exposure
#from skimage.morphology import disk
#from skimage.filters import rank
from skimage.util import crop
from skimage.util import pad

######### Remove cosmic rays or not? ###########
cosmic_rays = True

######### Decrease size of enhanced img or not? #####
isize = 0.8

######### Last frame before treatment ##########
treatment = 71

####### CHANGE HOW MUCH pixels to CROP from each side of original image before rotation
upper = 0              #if explant moves down, crop here
lower = 0
left =  0              #if explant moves right, crop here
right = 0

####### ROTATE, CROP AFTER TREATMENT ###########################################
angle = 0               # CHANGE angle to rotate image (positive = counter clockwise), negative clockwise
newangle = 0            # after treatment


##################### Tkinter button for browse/set_dir ################################
def browse_button():    
    global folder_path                      # Allow user to select a directory and store it in global var folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    print(filename)
    sourcePath = folder_path.get()
    os.chdir(sourcePath)                    # Provide the path here
    root.destroy()                          # close window after pushing button

root = Tk()
folder_path = StringVar()
lbl1 = Label(master=root, textvariable=folder_path)
lbl1.grid(row=0, column=1)
buttonBrowse = Button(text="Browse folder", command=browse_button)
buttonBrowse.grid()
mainloop()

path = os.getcwd() + '\\' 

# DOWNLOAD LIBAV https://libav.org/download/
path_to_avconv = 'F:\\DATA\\LV200\\libav\\usr\\bin\\'  # SET CORRECT PATH TO AVCONV.EXE FILE

########## Stackhack subfolder-creation with timestamp ###########
mydir = os.path.join(os.getcwd(), dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
os.makedirs(mydir)


######### To create movies, WHEN ALL DESIRED FILES ARE RENAMED and in common folder, proceed>>>

######### Ceate LIST of image files in cwd and put their path to list
files = []
with os.scandir(path) as it:
    for entry in it:
        if entry.name.endswith(('.tif', '.png', '.gif')) and entry.is_file():
            print(entry.name)                                           #, entry.path
            files.append(entry.path)

######### READ all sorted files and concatenate into list of arrays
files.sort()
conc_list = []
for file in files:
    print(file)
    img = io.imread(file)
    conc_list += [img] 

# To display image stored as array>>> plt.imshow(conc_list[0]), then plt.show()


########### REMOVE COSMIC RAYS ############################################################
########### BETTER APPROACH - pixelwise subtraction of consecutive images, need CV2 to perform saturation, numpy.subtract creates int overflow

if cosmic_rays is True:
    counter = 0
    for i in range(len(conc_list)):
        if counter + 1 < len(conc_list):      
            subtract1 = cv2.subtract(conc_list[counter], conc_list[counter + 1])    # first subtract img1 and img2
            subtract2 = cv2.subtract(conc_list[counter], subtract1)                 # then subtract img1 and result of previous subtraction
            newname2 = files[counter].split('\\')[-1]    
            io.imsave(f'{mydir}' + '\\' + f'{newname2}', subtract2)
            print(f'{mydir}' + '\\' + f'{newname2}')
            counter += 1
        else:    
            break

    # Load files with removed cosmic rays
    image_folder = mydir
    #filenames = []
    files = []
    for file in os.listdir(image_folder):
        filename = os.fsdecode(file)
        if filename.endswith(('.jpeg', '.png', '.tif')):
            #filenames.append(f'{mydir}\\{filename}')
            files.append(f'{mydir}\\{filename}')
            
    #filenames.sort()
    files.sort()
    print('Cosmic rays succesfully removed!')
    
else:
    print('Cosmic rays not removed.')    

# Make new directory for processed images
#os.makedirs(f'{mydir}' + '\\' )
os.makedirs(f'{mydir}' + '\\' + 'mod2\\')


######### CROP, PAD and ROTATE images #####################
images = []
count = 1
for file in files:              # for file in filenames:  #with cosmic rays removal
    imgT = io.imread(file)
    
    if count > treatment:       
            
        imgC = crop(imgT, ((upper, lower), (left, right)), copy=False)
        imgD = pad(imgC, ((lower, upper), (right, left)), 'minimum')
        rescaled = rescale(imgD, isize, anti_aliasing=False)                       # CHANGE how much to decrease the size, 0.6 is cca. 10MB
        rotated = rotate(rescaled, newangle)    
        imgT8 = skimage.img_as_ubyte(rotated)                                   # to convert to 8 bit
        io.imsave(f'{mydir}' + '\\'  + f'{os.path.basename(file)}', imgT8)
        images += [imgT8]

    else:        
        rescaled = rescale(imgT, isize, anti_aliasing=False)                       # CHANGE how much to decrease the size, 0.6 is cca. 10MB
        rotated = rotate(rescaled, angle)    
        imgT8 = skimage.img_as_ubyte(rotated)                                   # to convert to 8 bit
        io.imsave(f'{mydir}' + '\\'  + f'{os.path.basename(file)}', imgT8)
        images += [imgT8]

    count += 1

#imageio.mimsave(f'{mydir}' + '\\' + f'_gif_mod.gif', images, duration = 0.0667)   # duration=1/fps >>> modify duration as needed, 0.04 for 25fps
#os.system(f'cmd /c "{path_to_avconv}avconv -f image2 -r 30 -i {mydir}\\mod\\img%4d.tif -vcodec qtrle -pix_fmt rgb24 -t 15 {mydir}\\_movie_lossless_mod.mov"')



####### ENHANCE CONTRAST #############################################################
####### FILTER - Change list to array of arrays and apply filter to all images at once
images_array = np.asarray(images)
p1, p2 = np.percentile(images_array, (0.1, 99.9))                           # parameters for contrast stretch, SCN (2, 98), cells (0.1, 99.9)
imgEQ = exposure.rescale_intensity(images_array, in_range=(p1, p2))         # Contrast stretching

######## SAVE FILTERED  images as separate files using skimmage io ###########
counter = 0
for i_mod in imgEQ:
    #newname3 = os.path.basename(filenames[counter])
    newname3 = os.path.basename(files[counter]) 
    io.imsave(f'{mydir}' + '\\mod2\\' + f'{newname3}', i_mod)
    print(f'{mydir}' + '\\mod2\\' + f'{newname3}')
    counter += 1

# If no further enhancement needed, uncomment this to create gif.
#imgEQ = np.asarray(images)

imageio.mimsave(f'{mydir}' + '\\' + f'_gif_mod2.gif', imgEQ, duration = 0.0667)   # duration=1/fps >>> modify duration as needed, 0.04 for 25fps, 0.0667 OK for longer movies, 0.1 for 3h/frame

# To create movies, files need to be renamed first to imgXXX, use Rename_move script, also use DOS paths to avoid potential problems.
#os.system(f'cmd /c "{path_to_avconv}avconv -f image2 -r 10 -i {mydir}\\mod2\\img%4d.tif -vcodec qtrle -pix_fmt rgb24 -t 15 {mydir}\\_movie_lossless_mod2.mov"')         # to specify nonstand framerate set parameter -r 25 to another number, now is 10 fps
#os.system(f'cmd /k "{path_to_avconv}avconv -f image2 -r 10 -i {mydir}\\mod2\\img%4d.tif -mbd rd -flags +mv4+aic -trellis 2 -cmp 2 -subcmp 2 -g 300 {mydir}\\_movie_small_mod2.mp4"') # PROBLEM-white space path, nonstandard chars



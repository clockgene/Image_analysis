from tkinter import filedialog
from tkinter import *
import os, re, shutil
import numpy as np
#from matplotlib import pyplot as plt
#import scipy
from scipy import ndimage, misc
# import cv2  # problem with installation, use scipy and numpy trick
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
#from skimage.util import pad  # deprecated in skimage, use numpy

####### set True, if all explants are similar without movement, or for quick and dirty analysis ##############
####### if True, go only to main folder with explant folders
####### if False, go to individual explant subfolder
all_at_one = False

######### Remove cosmic rays by 'subtraction', 'median_filter' or False (not at all)? ###########
cosmic_rays = 'subtraction'        # subtracts pixels between consecutive images, no blurring, but lose 1 image
#cosmic_rays = 'median_filter'       # blurs image  -- NOT WORKING WITH .astype(np.int32) - add IFs
#cosmic_rays = False

######### Decrease size of contrast-enhanced img or not? Full sized images may cause memory errors on some PCs. #####
isize = 0.6   # 0.6 default, 0.3 for web and small imgs in presentations


######### Last frame before treatment ##########
treatment = 0

####### CHANGE HOW MUCH pixels to CROP from each side of original image before rotation
upper = 0              #if explant moves down, crop here
lower = 0
left =  0              #if explant moves right, crop here
right = 0

####### ROTATE, CROP AFTER TREATMENT ###########################################
angle = 0         # CHANGE angle to rotate image (positive = counter clockwise), negative clockwise
newangle = 0         # after treatment


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

if all_at_one is False:

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
        if cosmic_rays == 'subtraction':            
            img = io.imread(file).astype(np.int32)
        else:
            img = io.imread(file)
        conc_list += [img] 

    # To display image stored as array>>> plt.imshow(conc_list[0]), then plt.show()


    ########### REMOVE COSMIC RAYS ############################################################
    ########### BETTER APPROACH - pixelwise subtraction of consecutive images, need CV2 to perform saturation, numpy.subtract creates int overflow, or use np.clip

    if cosmic_rays == 'subtraction':
        counter = 0
        for i in range(len(conc_list)):
            if counter + 1 < len(conc_list):      
                #subtract1 = cv2.subtract(conc_list[counter], conc_list[counter + 1])    # first subtract img1 and img2
                #subtract2 = cv2.subtract(conc_list[counter], subtract1)                 # then subtract img1 and result of previous subtraction
                # alternative without cv2
                subtract1 = np.clip(conc_list[counter] - conc_list[counter + 1],0,65535).astype(np.uint16)
                subtract2 = np.clip(conc_list[counter] - subtract1,0,65535).astype(np.uint16)
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
        print('Cosmic rays succesfully removed by pixelwise subtraction!')


    ######### MEDIAN FILTER - Change list to array of arrays and apply filter to all images at once
    if cosmic_rays == 'median_filter':    
        # dst = cv2.medianBlur(np.asarray(conc_list), 3)                # OpenCV2 medianBlur, adjust between 3, 5, 7...
        dst = ndimage.median_filter(np.asarray(conc_list), size=3)     # Scipy median_filter, adjust between 2,3,4,5,6,7,...
        counter = 0
        for i in dst:
            newname2 = files[counter].split('\\')[-1]    
            io.imsave(f'{mydir}' + '\\' + f'{newname2}', i)
            print(f'{mydir}' + '\\' + f'{newname2}')
            counter += 1

        # Load files with removed cosmic rays
        image_folder = mydir
        #filenames = []
        files = []
        for file in os.listdir(image_folder):
            filename = os.fsdecode(file)
            if filename.endswith(('.jpeg', '.png', '.tif')):
                #filenames.append(f'{mydir}\\{filename}')
                files.append(f'{mydir}\\{filename}')

        files.sort()
        print('Cosmic rays succesfully removed by median filter!')

    if cosmic_rays == False:
        print('Cosmic rays not removed.')


    conc_list = 0
    dst = 0

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
            #imgD = pad(imgC, ((lower, upper), (right, left)), 'minimum')
            imgD = np.pad(imgC, ((lower, upper), (right, left)), 'minimum') 
            rotated = rotate(imgD, newangle)    
            imgT8 = skimage.img_as_ubyte(rotated)                                   # to convert to 8 bit
            io.imsave(f'{mydir}' + '\\'  + f'{os.path.basename(file)}', imgT8)
            images += [imgT8]

        else:                
            rotated = rotate(imgT, angle)    
            imgT8 = skimage.img_as_ubyte(rotated)                                   # to convert to 8 bit
            io.imsave(f'{mydir}' + '\\'  + f'{os.path.basename(file)}', imgT8)
            images += [imgT8]

        count += 1

    #imageio.mimsave(f'{mydir}' + '\\' + f'_gif_mod.gif', images, duration = 0.0667)   # duration=1/fps >>> modify duration as needed, 0.04 for 25fps
    #os.system(f'cmd /c "{path_to_avconv}avconv -f image2 -r 30 -i {mydir}\\mod\\img%4d.tif -vcodec qtrle -pix_fmt rgb24 -t 15 {mydir}\\_movie_lossless_mod.mov"')


    # rescale before contrast stretching and gif
    images2 = []
    for img in images:
        rescaled = rescale(img, isize, anti_aliasing=False)  # CHANGE how much to decrease the size, 0.6 is cca. 10MB
        img = skimage.img_as_ubyte(rescaled)
        images2 += [img]
        

    ####### ENHANCE CONTRAST #############################################################
    ####### FILTER - Change list to array of arrays and apply filter to all images at once
    images_array = np.asarray(images2)
    p1, p2 = np.percentile(images_array, (0.2, 99.8))                           # parameters for contrast stretch, 0.1 - low, 1 - high stretch
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

    imageio.mimsave(f'{mydir}' + '\\' + 'mod2\\' + f'_gif_{mydir[-23:-20]}.gif', imgEQ, duration = 0.0667)   # duration=1/fps >>> modify duration as needed, 0.04 for 25fps, 0.0667 OK for longer movies, 0.1 for 3h/frame

    # To create movies, files need to be renamed first to imgXXX, use Rename_move script, also use DOS paths to avoid potential problems.
    #os.system(f'cmd /c "{path_to_avconv}avconv -f image2 -r 10 -i {mydir}\\mod2\\img%4d.tif -vcodec qtrle -pix_fmt rgb24 -t 15 {mydir}\\_movie_lossless_mod2.mov"')         # to specify nonstand framerate set parameter -r 25 to another number, now is 10 fps
    #os.system(f'cmd /k "{path_to_avconv}avconv -f image2 -r 10 -i {mydir}\\mod2\\img%4d.tif -mbd rd -flags +mv4+aic -trellis 2 -cmp 2 -subcmp 2 -g 300 {mydir}\\_movie_small_mod2.mp4"') # PROBLEM-white space path, nonstandard chars


if all_at_one is True:

    print('Running all at once! Are you sure?')
    
    folds = []
    with os.scandir(path) as it:
        for fold in it:
            #print(f'{path}{fold.name}')
            folds.append(fold.name)

    for f in folds:


        pth = f'{path}{f}\\'

        ########## Stackhack subfolder-creation with timestamp ###########
        mydir = os.path.join(pth, dt.datetime.now().strftime('%Y-%m-%d_%H-%M-%S'))
        os.makedirs(mydir)


        ######### To create movies, WHEN ALL DESIRED FILES ARE RENAMED and in common folder, proceed>>>

        ######### Ceate LIST of image files in cwd and put their path to list
        files = []
        with os.scandir(pth) as it:
            for entry in it:
                if entry.name.endswith(('.tif', '.png', '.gif')) and entry.is_file():
                    print(entry.name)                                           #, entry.path
                    files.append(entry.path)

        ######### READ all sorted files and concatenate into list of arrays
        files.sort()
        conc_list = []
        for file in files:
            print(file)
            if cosmic_rays == 'subtraction':            
                img = io.imread(file).astype(np.int32)
            else:
                img = io.imread(file)            
            conc_list += [img] 

        # To display image stored as array>>> plt.imshow(conc_list[0]), then plt.show()


        ########### REMOVE COSMIC RAYS ############################################################
        ########### BETTER APPROACH - pixelwise subtraction of consecutive images, need CV2 to perform saturation, numpy.subtract creates int overflow, or use np.clip

        if cosmic_rays == 'subtraction':
            counter = 0
            for i in range(len(conc_list)):
                if counter + 1 < len(conc_list):      
                    # subtract1 = cv2.subtract(conc_list[counter], conc_list[counter + 1])    # first subtract img1 and img2
                    # subtract2 = cv2.subtract(conc_list[counter], subtract1)                 # then subtract img1 and result of previous subtraction
                    subtract1 = np.clip(conc_list[counter] - conc_list[counter + 1],0,65535).astype(np.uint16)
                    subtract2 = np.clip(conc_list[counter] - subtract1,0,65535).astype(np.uint16)                    
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
            print('Cosmic rays succesfully removed by pixelwise subtraction!')


        ######### MEDIAN FILTER - Change list to array of arrays and apply filter to all images at once
        if cosmic_rays == 'median_filter':    
            # dst = cv2.medianBlur(np.asarray(conc_list), 3)                # OpenCV2 medianBlur, adjust between 3, 5, 7...
            dst = ndimage.median_filter(np.asarray(conc_list), size=3)     # Scipy median_filter, adjust between 2,3,4,5,6,7,...
            counter = 0
            for i in dst:
                newname2 = files[counter].split('\\')[-1]    
                io.imsave(f'{mydir}' + '\\' + f'{newname2}', i)
                print(f'{mydir}' + '\\' + f'{newname2}')
                counter += 1

            # Load files with removed cosmic rays
            image_folder = mydir
            #filenames = []
            files = []
            for file in os.listdir(image_folder):
                filename = os.fsdecode(file)
                if filename.endswith(('.jpeg', '.png', '.tif')):
                    #filenames.append(f'{mydir}\\{filename}')
                    files.append(f'{mydir}\\{filename}')

            files.sort()
            print('Cosmic rays succesfully removed by median filter!')

        if cosmic_rays == False:
            print('Cosmic rays not removed.')


        conc_list = 0
        dst = 0

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
                #imgD = pad(imgC, ((lower, upper), (right, left)), 'minimum')
                imgD = np.pad(imgC, ((lower, upper), (right, left)), 'minimum')
                rotated = rotate(imgD, newangle)    
                imgT8 = skimage.img_as_ubyte(rotated)                                   # to convert to 8 bit
                io.imsave(f'{mydir}' + '\\'  + f'{os.path.basename(file)}', imgT8)
                images += [imgT8]

            else:                
                rotated = rotate(imgT, angle)    
                imgT8 = skimage.img_as_ubyte(rotated)                                   # to convert to 8 bit
                io.imsave(f'{mydir}' + '\\'  + f'{os.path.basename(file)}', imgT8)
                images += [imgT8]

            count += 1

        #imageio.mimsave(f'{mydir}' + '\\' + f'_gif_mod.gif', images, duration = 0.0667)   # duration=1/fps >>> modify duration as needed, 0.04 for 25fps
        #os.system(f'cmd /c "{path_to_avconv}avconv -f image2 -r 30 -i {mydir}\\mod\\img%4d.tif -vcodec qtrle -pix_fmt rgb24 -t 15 {mydir}\\_movie_lossless_mod.mov"')


        # rescale before contrast stretching and gif
        images2 = []
        for img in images:
            rescaled = rescale(img, isize, anti_aliasing=False)  # CHANGE how much to decrease the size, 0.6 is cca. 10MB
            img = skimage.img_as_ubyte(rescaled)
            images2 += [img]
            

        ####### ENHANCE CONTRAST #############################################################
        ####### FILTER - Change list to array of arrays and apply filter to all images at once
        images_array = np.asarray(images2)
        p1, p2 = np.percentile(images_array, (0.2, 99.8))                           # parameters for contrast stretch, 0.1 - low, 1 - high stretch
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

        imageio.mimsave(f'{mydir}' + '\\' + 'mod2\\' + f'_gif_{mydir[-23:-20]}.gif', imgEQ, duration = 0.0667)   # duration=1/fps >>> modify duration as needed, 0.04 for 25fps, 0.0667 OK for longer movies, 0.1 for 3h/frame



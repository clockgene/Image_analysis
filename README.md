# Image_analysis, instructions for Laboratory og Biological Rhythms, IPHYS CAS

Optional:
For mp4 movies, need libav, latest releases are here https://libav.org/download/
or just use unzip libav-x86_64-w64-mingw32-20180108.7z from Z:\_install\Python scripts Martin\Image_analysis to your drive and remember the path, 
it needs to be edited in LV200_crop_pad_cosmic_rays_v2.py script

Necessary:
If you do not have it already, install miniconda3 from here: 

https://docs.conda.io/en/latest/miniconda.html
Choose Python 3.8 or newer Windows 64bit installer of Miniconda3, download, run the file, select admin, for all, select add to PATH, do not make default (unless you have no previous Python environment)

More information on Anaconda and its environments:
https://towardsdatascience.com/a-guide-to-conda-environments-bc6180fc533
https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html


Create image environment and install necessary packages:

click in Windows on Start menu, run Anaconda PowerShell prompt (as admin if possible), type and enter each row and wait for installation:
conda create -n image
conda activate image
conda env list   		
conda install numpy
conda install scikit-image 
conda install opencv-contrib-python                                

# If you have trouble installing from default channel (i.e. you get some error message), type this instead: 
conda install --channel conda-forge NAME-OF-THE-PACKAGE

# to run in IDLE, type this in conda prompt
conda activate image
idle


To use batch file that autoactivates image env and starts idle/spyder, right click on desktop, create New text document (not Word, notepad txt),
rename it to conda_image.bat, open it in notepad and copy paste this:

@echo on
call C:\ProgramData\Miniconda3\Scripts\activate.bat
call activate image
call python -m idlelib

# C:\ProgramData\... need to be modified to your actual path to miniconda, which depends on admin/user install!

AFTER it is installed, copy/download these scripts

LV200_rename_move_v4_automatic.py

LV200_crop_pad_cosmic_rays_v5.py

Open them in idle and follow instructions in them. LV200_rename_move is for renaming files from different folders (needed for treatment experiments only), 
LV200_crop_pad_cosmic_rays enhances the images and creates animated GIF or MP4 movies.

To analyze images in ImageJ https://imagej.net/software/fiji/index and get data from macro ROIs/cell-sized grid ROIs and then analyze them in per2py, follow _manual_per2py_lumicycle.txt. To use cell tracking in ImageJ TrackMate and analyze in per2py, follow manual_ImageJ and Trackmate v1.txt and _manual_per2py_trackmate.txt

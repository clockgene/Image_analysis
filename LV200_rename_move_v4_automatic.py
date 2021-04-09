import glob, os, shutil
from tkinter import filedialog
from tkinter import *
import re


##################### Tkinter button for browse/set_dir ################################
def browse_button():    
    global folder_path                      # Allow user to select a directory and store it in global var folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)
    print(filename)
    sourcePath = folder_path.get()
    os.chdir(sourcePath)                    # Provide the path here
    root.destroy()                          # close window after pushing button


#Regex to search for numbers in filename, that will be used for sequence
regex1 = re.compile(r'\d{1,}')

#### Select a folder with LV200 default named (xxx_T0001.tif) output tif files
#### Move files created before and after treatment to separate folders
#### Script renames all files in all subfolders to img0001... or to img[last_file+1]
#### then moves them all to a common folder in after folder


########################################################################
########################################################################
######## AUTORENAME and COPY/MOVE RENAMED FILES TO NEW FOLDERs #########
########################################################################
########################################################################

folderid = '_SCN'           #specific name string, e.g. '_SCN', must NOT be same as original folders
fileid = 'img'              #string attached at the start of the renamed files just before the sequence id


# Specify FOLDER BEFORE TREATMENT
root = Tk()
folder_path = StringVar()
lbl1 = Label(master=root, textvariable=folder_path)
lbl1.grid(row=0, column=1)
buttonBrowse = Button(text="Browse to folder Before Treatment", command=browse_button)
buttonBrowse.grid()
mainloop()
path = os.getcwd() + '\\'

paths = [path]

# COUNT the number of files in BEFORE TREATMENT folders
filescount = []
for root, dirs, files in os.walk(".", topdown=False):
    files = [x for x in files if x != 'Thumbs.db']   #sometimes Windows creates hidden Thumbs file, this is to avoid cointing that
    filescount.append(len(files))

# This creates new folders named e.g. name1 name2 etc for each subfolder
counter = 1          # counter, e.g. for SCN1, SCN2,...
newfolders = []
oldfolders = []
for root, dirs, files in os.walk(".", topdown=False):
    for directories in dirs:
        mydir_no = os.path.join(os.getcwd(), f'{folderid}{counter}')
        os.makedirs(mydir_no)        
        newfolders.append(os.path.join(os.getcwd(), f'{folderid}{counter}'))
        oldfolders.append(os.path.join(os.getcwd(), f'{directories}'))
        counter += 1

# This copies files from subfolders to newly named folders
counter2 = 0                          
for oldfolder in oldfolders:
    for root, dirs, files in os.walk(oldfolder):
        for name in files:
            print(os.path.join(root, name))
            if name != 'Thumbs.db':                
                partname = name.split('_T')[-1]                                                         
                new_file_start_string = str(int(partname.split('.')[0]))                        #must have _T, e.g. ExperimentSOMENUMBER_T0001.tif
                #new_file_start_string = str(int(regex1.search(name).group()))                  #for any name with sequence, but it must be the first number 
                new_file_start_string = new_file_start_string.zfill(4)
                filetype = partname.split('.')[-1]
                newname = f'{fileid}{new_file_start_string}.{filetype}'      
                os.rename(os.path.join(root, name), newfolders[counter2] + f'\\{newname}')              #this moves renamed files to new folder
                #shutil.copy(os.path.join(root, name), newfolders[counter2] + f'\\{newname}')           #this copies instead of moves the files
        shutil.rmtree(oldfolder)                                                                         #if copying, remove this
        counter2 += 1


# Specify 1st FOLDER AFTER TREATMENT
root = Tk()
folder_path = StringVar()
lbl1 = Label(master=root, textvariable=folder_path)
lbl1.grid(row=0, column=1)
buttonBrowse = Button(text="Browse to folder After treatment", command=browse_button)
buttonBrowse.grid()
mainloop()
path2 = os.getcwd() + '\\'

paths.append(path2)

# This creates new folders named e.g. name1 name2 etc for each subfolder
counter = 1          # counter, e.g. for SCN1, SCN2,...
newfolders = []
oldfolders = []
for root, dirs, files in os.walk(".", topdown=False):
    for directories in dirs:
        mydir_no = os.path.join(os.getcwd(), f'{folderid}{counter}')
        os.makedirs(mydir_no)        
        newfolders.append(os.path.join(os.getcwd(), f'{folderid}{counter}'))
        oldfolders.append(os.path.join(os.getcwd(), f'{directories}'))
        counter += 1

# rename files in AFTER TREATMENT with number of files in corresponding BEFORE TREATMENT folder
last_file = filescount[0:-1]     #last value is number of files in root, which should be 0

# This copies files from subfolders to newly named folders and renames them sequentially starting from last_files
counter2 = 0                          
for oldfolder in oldfolders:
    for root, dirs, files in os.walk(oldfolder):
        for name in files:
            print(os.path.join(root, name))
            if name != 'Thumbs.db':
                partname = name.split('_T')[-1]                                                         
                new_file_start_string = str(int(partname.split('.')[0]) + last_file[counter2])              #must have _T, e.g. ExperimentSOMENUMBER_T0001.tif
                #new_file_start_string = str(int(regex1.search(name).group()) + last_file[counter2])        #for any name with sequence, but it must be the first number 
                new_file_start_string = new_file_start_string.zfill(4)
                filetype = partname.split('.')[-1]
                newname = f'{fileid}{new_file_start_string}.{filetype}'      
                os.rename(os.path.join(root, name), newfolders[counter2] + f'\\{newname}')              #this moves renamed files to new folder
                #shutil.copy(os.path.join(root, name), newfolders[counter2] + f'\\{newname}')           #this copies instead of moves the files
        shutil.rmtree(oldfolder)                                                                         #if copying, remove this
        counter2 += 1


"""
# THIRD folder

# number of files in AFTER2 folder
filescount2 = []
for root, dirs, files in os.walk(path2, topdown=False):
    files = [x for x in files if x != 'Thumbs.db']
    filescount2.append(len(files))

root = Tk()
folder_path = StringVar()
lbl1 = Label(master=root, textvariable=folder_path)
lbl1.grid(row=0, column=1)
buttonBrowse = Button(text="Browse to 2nd After folder", command=browse_button)
buttonBrowse.grid()
mainloop()
path3 = os.getcwd() + '\\'

paths.append(path3)

# This creates new folders named e.g. name1 name2 etc for each subfolder
counter = 1          # counter, e.g. for SCN1, SCN2,...
newfolders = []
oldfolders = []
for root, dirs, files in os.walk(".", topdown=False):
    for directories in dirs:
        mydir_no = os.path.join(os.getcwd(), f'{folderid}{counter}')
        os.makedirs(mydir_no)        
        newfolders.append(os.path.join(os.getcwd(), f'{folderid}{counter}'))
        oldfolders.append(os.path.join(os.getcwd(), f'{directories}'))
        counter += 1

# rename files in AFTER2 TREATMENT with number of files in corresponding BEFORE+AFTER TREATMENT folder
last_file2 = [filescount[i] + filescount2[i] for i in range(len(filescount))][0:-1]     #adds values in list1 and 2 

# This copies files from subfolders to newly named folders and renames them sequentially starting from last_files
counter2 = 0                          
for oldfolder in oldfolders:
    for root, dirs, files in os.walk(oldfolder):
        for name in files:
            print(os.path.join(root, name))
            if name != 'Thumbs.db':
                partname = name.split('_T')[-1]                                                         
                new_file_start_string = str(int(partname.split('.')[0]) + last_file2[counter2])              #must have _T, e.g. ExperimentSOMENUMBER_T0001.tif
                #new_file_start_string = str(int(regex1.search(name).group()) + last_file2[counter2])        #for any name with sequence, but it must be the first number 
                new_file_start_string = new_file_start_string.zfill(4)
                filetype = partname.split('.')[-1]
                newname = f'{fileid}{new_file_start_string}.{filetype}'      
                os.rename(os.path.join(root, name), newfolders[counter2] + f'\\{newname}')              #this moves renamed files to new folder
                #shutil.copy(os.path.join(root, name), newfolders[counter2] + f'\\{newname}')           #this copies instead of moves the files
        os.rmdir(oldfolder)                                                                         #if copying, remove this
        counter2 += 1

"""

"""
# FOURTH folder

filescount3 = []
for root, dirs, files in os.walk(path3, topdown=False):
    files = [x for x in files if x != 'Thumbs.db']
    filescount3.append(len(files))

root = Tk()
folder_path = StringVar()
lbl1 = Label(master=root, textvariable=folder_path)
lbl1.grid(row=0, column=1)
buttonBrowse = Button(text="Browse to 3rd After folder", command=browse_button)
buttonBrowse.grid()
mainloop()
path4 = os.getcwd() + '\\'

paths.append(path4)

counter = 1          # counter, e.g. for SCN1, SCN2,...
newfolders = []
oldfolders = []
for root, dirs, files in os.walk(".", topdown=False):
    for directories in dirs:
        mydir_no = os.path.join(os.getcwd(), f'{folderid}{counter}')
        os.makedirs(mydir_no)        
        newfolders.append(os.path.join(os.getcwd(), f'{folderid}{counter}'))
        oldfolders.append(os.path.join(os.getcwd(), f'{directories}'))
        counter += 1

last_file3 = [filescount[i] + filescount2[i] + filescount3[i] for i in range(len(filescount))][0:-1]   #adds values in list1 and 2 
counter2 = 0                          
for oldfolder in oldfolders:
    for root, dirs, files in os.walk(oldfolder):
        for name in files:
            print(os.path.join(root, name))
            if name != 'Thumbs.db':
                partname = name.split('_T')[-1]                                                         
                new_file_start_string = str(int(partname.split('.')[0]) + last_file3[counter2])              #must have _T, e.g. ExperimentSOMENUMBER_T0001.tif
                #new_file_start_string = str(int(regex1.search(name).group()) + last_file3[counter2])        #for any name with sequence, but it must be the first number 
                new_file_start_string = new_file_start_string.zfill(4)
                filetype = partname.split('.')[-1]
                newname = f'{fileid}{new_file_start_string}.{filetype}'      
                os.rename(os.path.join(root, name), newfolders[counter2] + f'\\{newname}')              #this moves renamed files to new folder
                #shutil.copy(os.path.join(root, name), newfolders[counter2] + f'\\{newname}')           #this copies instead of moves the files
        os.rmdir(oldfolder)                                                                         #if copying, remove this
        counter2 += 1

# MORE FOLDERS - if even more are needed, just copy FOURTH folder segment and change variable names: filescount3 to 4, path4 to 5, last_file3 to 4 and add filescount4[i]

"""

########################################################################
########################################################################
######### MOVING RENAMED FILES TO LAST AFTER TREATMENT FOLDER ##########
########################################################################
########################################################################

oldfolders = []
                
for y in range(len(paths)):
    for root, dirs, files in os.walk(paths[y], topdown=False):
        oldsubfolders = []
        for directories in dirs:
            oldsubfolders.append(os.path.join(paths[y], f'{directories}'))
    oldfolders.append(oldsubfolders)

oldfolders2 = oldfolders[0:-1]
nextfolders = oldfolders[-1]

for cntr in range(len(oldfolders2)):
    counter3 = 0
    for oldfolder in oldfolders2[cntr]:                      
        for root, dirs, files in os.walk(oldfolder):
            for name in files:            
               #shutil.copy(oldfolder + f'\\{name}', nextfolders[cntr][counter3] + f'\\{name}')     #this copies instead of moves the files
               os.rename(oldfolder + f'\\{name}', nextfolders[counter3] + f'\\{name}')               #this moves files to folder
            counter3 += 1
            os.rmdir(oldfolder)                                                                     #if copying, remove this

[os.rmdir(i) for i in paths[0:-1]]     #if copying, remove this


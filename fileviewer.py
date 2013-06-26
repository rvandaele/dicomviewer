import dicom
import numpy as np
import scipy.ndimage
from volumeviewer import *
from sys import *

def loadVolume(filename):
    f = open(filename,'r')
    lines = f.readlines()
    n = len(lines)
    
    fname = lines[0].rstrip()
    image = dicom.read_file(fname)
    height = len(image.PixelArray)
    width = len(image.PixelArray[0])
    
    real_max = np.max(image.PixelArray)
    real_min = np.min(image.PixelArray)
    
    taille = np.max([height,width,n])
    
    taille = pow(2,np.ceil(np.log2(taille)))
    if(taille<256):
        taille=256
    VOL = np.zeros((taille,taille,taille))
    
    for i in range(n):
        fname = lines[i].rstrip()
        image = dicom.read_file(fname)
        tab = image.pixel_array
        VOL[i-1][0:height][0:width] = tab
        
    maximum = np.max(VOL)
    minimum = np.min(VOL)
    maxmin = maximum-minimum
    VOL = (VOL-minimum)/maxmin
    VOL = scipy.ndimage.zoom(VOL,256./taille)
    omage = Volume()
    omage.data = VOL
    omage.sizeX = 256
    omage.sizeY = 256
    omage.sizeZ = 256
    return omage

if __name__=="__main__":
    if(len(argv)==2): 
        vol = loadVolume(argv[1])    
        cv = Canvas(vol)
        win = GLWindow(640,480,cv)
        cv.initGL(640,480)
        win.run()
    else:
        print "You did not use fileiewer.py correctly. Please read the readme"

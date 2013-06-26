# -*- coding: utf-8 -*- 
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import dicom
import numpy as np
import scipy.ndimage
import nifti
from volumeviewer import *
from sys import *

def normalize_volume(v):
    maximum = np.max(v)
    minimum = np.min(v)
    maximini = maximum-minimum
    v = (v-minimum)/maximini
    return v
    
def loadNiftiVolume(f_filename):
    try:
        volume_f = nifti.NiftiImage(f_filename)
    except:
        print f_filename + " does not seem to be a valid nifti file."
        exit()
            
    volume_f.load()
    data_f = volume_f.getDataArray()
    height_f = len(data_f)
    width_f = len(data_f[0])
    depth_f = len(data_f[0][0])
    msize = np.power(2,int(np.ceil(np.log2(np.max((height_f,width_f,depth_f))))))
    
    if msize<256:
        msize=256
    
    finaldata_f = np.zeros((msize,msize,msize),dtype=float)
    finaldata_f[0:height_f,0:width_f,0:depth_f] = data_f
    finaldata_f = scipy.ndimage.zoom(finaldata_f,256./msize,order=1)
    fimage = Volume()
    if(abs(np.max(finaldata_f)-1)<0.01 or abs(np.min(finaldata_f))<0.01):
        fimage.data = normalize_volume(finaldata_f)
    else:
        fimage.data = normalize_volume(finaldata_f)
    fimage.sizeX = 256
    fimage.sizeY = 256
    fimage.sizeZ = 256
    return fimage
    
if __name__=="__main__":
    if(len(argv)==2): 
        vol = loadNiftiVolume(argv[1])    
        cv = Canvas(vol)
        win = GLWindow(640,480,cv)
        cv.initGL(640,480)
        win.run()
    else:
        print "You did not use fileiewer.py correctly. Please read the readme"

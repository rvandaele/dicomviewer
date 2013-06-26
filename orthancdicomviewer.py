# -*- coding: utf-8 -*- 
import pycurl as curl
import simplejson as json
import nifti
import Image
from sys import *
import StringIO
import os
import numpy as np
import scipy
import scipy.ndimage
from volumeviewer import *
"""
Usage : 
    python orthancdicomviewer.py [host,default=localhost] [port,default=8042] \
    serie
Example:
    python orthancdicomviewer.py localhost 8042 \
    17cc7e52-4f1a3e4d-9182f727-56e9cc71-c037892f
"""

"""
Floating point data normalization : all the data is converted in the range [0-1]    
"""
def normalize_volume(v):
    maximum = np.max(v)
    minimum = np.min(v)
    maximini = maximum-minimum
    v = (v-minimum)/maximini
    return v
    
#Load the Orthanc volume of the Orthanc serie specified
def load_orthanc_volume(orthanc_url,serie):
    c = curl.Curl()
    c.setopt(curl.URL, orthanc_url + "/series/" +serie)
    c.setopt(curl.HTTPHEADER, ["Accept:"])
    b = StringIO.StringIO()
    c.setopt(curl.WRITEFUNCTION, b.write)
    c.setopt(curl.FOLLOWLOCATION, 1)
    c.setopt(curl.MAXREDIRS, 5)
    c.perform()
    jason = json.loads(b.getvalue())
    instances = jason['Instances']

    """
        For each instance, raw data is saved in a temporary dicom file.
        The image is then loaded with pydicom, and saved in a numpy array.
    """
    zpos = np.zeros(len(instances))
    
    for i in range(len(instances)):
        instance = instances[i]
        
        #Request instance metadata
        cp = curl.Curl()
        cp.setopt(curl.URL,orthanc_url + "/instances/" + instance + \
"/simplified-tags")
        c.setopt(curl.HTTPHEADER, ["Accept:"])
        b = StringIO.StringIO()
        cp.setopt(curl.WRITEFUNCTION, b.write)
        cp.setopt(curl.FOLLOWLOCATION, 1)
        cp.setopt(curl.MAXREDIRS, 5)
        cp.perform()
        jason = json.loads(b.getvalue())
        zpos[i] = float(jason['SliceLocation'])-1
        if(i==0):
            height = int(jason['Rows'])
            width = int(jason['Columns'])
            depth = len(instances)
            taille = np.max([height,width,depth])
            taille = pow(2,np.ceil(np.log2(taille)))
            A = np.zeros((taille,taille,taille))
        #Request instance data
        c = curl.Curl()
        c.setopt(curl.URL,orthanc_url + "/instances/" + instance + \
"/image-uint16" )
        c.setopt(curl.HTTPHEADER, ["Accept:"])
        b = StringIO.StringIO()
        c.setopt(curl.WRITEFUNCTION, b.write)
        c.setopt(curl.FOLLOWLOCATION, 1)
        c.setopt(curl.MAXREDIRS, 5)
        c.perform()
        
        f = open('/tmp/tmp.png','w')
        f.write(b.getvalue())
        f.close()
        pilimage = Image.open('/tmp/tmp.png')
        arraydata = np.array(pilimage.getdata()).reshape(height,width)

        A[i][0:height][0:width] = arraydata
    
    w = range(len(instances))
    w.sort(key=lambda x:zpos[x])
    B = np.zeros((depth,height,width))
    for i in range(len(instances)):
        B[i] = A[w[i]]
    A = scipy.ndimage.zoom(A,256./taille)
    V = Volume()
    V.data = normalize_volume(A)
    V.sizeX = 256
    V.sizeY = 256
    V.sizeZ = 256
    return V
        
if __name__=="__main__":
    argc = len(argv)
    if(argc==2):
        HOST = 'localhost'
        PORT = '8042'
        SERIE = argv[1]
    elif(argc==4):
        HOST = argv[1]
        PORT = argv[2]
        SERIE = argv[3]
    else:
        print "You did not use orthancdicomviewer.py correctly. Please read the\
 readme"
    URL = 'http://'+HOST+':'+PORT
    vol = load_orthanc_volume(URL,SERIE)    
    cv = Canvas(vol)
    win = GLWindow(640,480,cv)
    cv.initGL(640,480)
    win.run()

# -*- coding: utf-8 -*- 
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from sys import *
import numpy as np

ESCAPE = 27
E_CHAR = 101
LEFTXY = 100
RIGHXY = 102
UPARYZ = 101
DOARYZ = 103
LEARXZ = 106
RIARXZ = 107
Q_CHAR = 113
D_CHAR = 100
Z_CHAR = 122
S_CHAR = 115
UPMOUS = 3
DOMOUS = 4
KEY_MI = 45
KEY_PL = 43

"""
An image is defined by its two dimensional data, and the size of these dimensions
Dimension are not really necessary here, as len(data) and len(data[0]) could do
it, but I think it is nicer :-)
"""
class Volume:
    def __init__(self):
        self.data = None
        self.sizeX = 0
        self.sizeY = 0
        self.sizeZ = 0
             
"""
Load the GL texture from the filename: 
basically, I load it using loadImage, and then create 3 textures with the image
I obtained.
If you do not want to use dicom, just change the function above (stay in grey values)

Principle:
Generate texture identifiers
Bind an identifier
define what to do when you upscale (MAG_FILTER) and downscale (MIN_FILTER)
then link the texture
2D texture, 0, number of channels, width, height, 0, type of data to store, type of data, data

Small change with python NeHe mipmapping : mipmap can be called from parameters
"""
def LoadGLTextures(image1):
    # Load Texture
    #image1 = loadVolume(fname)
    # Create Textures
    texture = glGenTextures(1)
    
    # Linear interpolation
    glBindTexture(GL_TEXTURE_3D, texture)
    glTexEnvf( GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_MODULATE )
    glTexParameterf( GL_TEXTURE_3D, GL_TEXTURE_MAG_FILTER, GL_LINEAR )
    glTexParameterf( GL_TEXTURE_3D, GL_TEXTURE_MIN_FILTER, GL_LINEAR )
    glTexImage3D(GL_TEXTURE_3D,0,GL_INTENSITY,image1.sizeX,image1.sizeY,image1.sizeZ,0, GL_LUMINANCE,GL_FLOAT,image1.data)
    return texture

"""
Canvas class : 
does all the interactions with GL and GLU. Arbitrary division, still convenient.
stores the state of the canvas (texturing, blending,...)
""" 
class Canvas:
    
    """
        Initialisation of gl parameters must be done AFTER the calls to GLUT,
        that defines some parameters to use
        So, to be sure, we just initalize the state of the canvas here
    """
    def __init__(self,vol):
        self.textures = None 
        self.vol = vol
        self.xyrotation = 0
        self.yzrotation = 0
        self.xzrotation = 0
        self.xtranslation = 0
        self.ytranslation = 0
        self.zoom = 4.
        self.width = 0
        self.height = 0
        self.slice = 600.
        
    """
        Function to be called when the canvas is resized.
        Basically, I resize the canvas and the view
    """
    def ReSizeGLScene(self,Width, Height):
        
        self.width = Width
        self.height = Height
        # 0 in width would mess up my further calculations, and you couldn't
        # see anything
        if Width == 0:
	        Width = 1

        # Resize the canvas to the size of the resized window
        glViewport(0, 0, Width, Height)
        
        #Define the projection
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity() # Reinitalisation
        aspect = float(Height)/float(Width)
        #My cube coordinates are -1.,1,-1,1,-1,1. I define the projection
        #with 5 in order to be able to see the cube and its possible rotations
        #You can change it if you want. aspect to keep the window ratio
        glOrtho(-self.zoom,self.zoom,-self.zoom*aspect,self.zoom*aspect,-10,10)
        glMatrixMode(GL_MODELVIEW)
    
    def initGL(self,Width,Height):
        # Loads the textures and enables 2D texturing (I only draw 2D images on
        # the cube faces)
        self.textures = LoadGLTextures(self.vol)
        glEnable(GL_TEXTURE_3D)
        
        #Window is set to black
        glClearColor(0.0, 0.0, 0.0, 0.0)
        
        #Depth buffer to handle pixels being at (x,y) position. The one with
        #smallest z is printed. Initialized but disabled: obviously, it messes
        #up with GL_MAX blending
        glClearDepth(1.0)		
        glDepthFunc(GL_LESS)				
        glDisable(GL_DEPTH_TEST)
        
        #Enable the blending with MIP projection. You can change GL_MAX to 
        #other stuff if you want to.
        glBlendEquation(GL_MAX)		
        glEnable(GL_BLEND)
        
        #Defines shading (probably not very important here)
        glShadeModel(GL_SMOOTH)
	
	    #Size the window (often done automatically, but one time more does not 
	    #kill anyone)
        self.ReSizeGLScene(Width, Height)
                   
    def DrawGLScene(self):
        #With resize, we already are in MODELVIEW mode
        
        #Clear the buffers we will write into
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        #Reinitialize all the transformations (previous are cancelled)
        glLoadIdentity()
        
        #Defines which one of the textures we are going to use
        glBindTexture(GL_TEXTURE_3D, self.textures) 

        #My object is defined by the coordinates [-1,1;-1,1;-1,1]
        #Zero is the center, and I am in orhographic projection, so no in depth
        #translation needed
        glTranslatef(self.xtranslation,self.ytranslation,0.0)
        
        #Rotate the volume
        glRotatef(self.yzrotation,1.0,0.0,0.0)
        glRotatef(self.xzrotation,0.0,1.0,0.0)
        glRotatef(self.xyrotation,0.0,0.0,1.0)
        		
                
        
        #My "cube" is defined by 6 independent faces, that I assemble like a
        #cube. Basically though, I just draw the texture on each face.
        
        glBegin(GL_QUADS)
        
        for d in np.arange(-1.,1.,1./self.slice):
            td = (d+1.)/2.
            glNormal3f(d,0.0,0.0)
            
            glTexCoord3f(td,1.,1.)
            glVertex3f(1.,1.,d)
            
            glTexCoord3f(td,0.,1.)
            glVertex3f(-1.,1.,d)
            
            glTexCoord3f(td,0.,0.)
            glVertex3f(-1.,-1.,d)
            
            glTexCoord3f(td,1.,0.)
            glVertex3f(1.,-1.,d)
        glEnd()

    def increasexyrotation(self):
        self.xyrotation = self.xyrotation+1
        
    def decreasexyrotation(self):
        self.xyrotation = self.xyrotation-1
        
    def increaseyzrotation(self):
        self.yzrotation = self.yzrotation+1
        
    def decreaseyzrotation(self):
        self.yzrotation = self.yzrotation-1

    def increasexzrotation(self):
        self.xzrotation = self.xzrotation+1
        
    def decreasexzrotation(self):
        self.xzrotation = self.xzrotation-1	    
        
    def increasextranslation(self):
        self.xtranslation = self.xtranslation+0.05
        
    def decreasextranslation(self):
        self.xtranslation = self.xtranslation-0.05
        
    def increaseytranslation(self):
        self.ytranslation = self.ytranslation+0.05
        
    def decreaseytranslation(self):
        self.ytranslation = self.ytranslation-0.05
    
    def increasezoom(self):
        self.zoom = self.zoom - 0.125
        self.ReSizeGLScene(self.width,self.height)
        
    def decreasezoom(self):
        self.zoom = self.zoom + 0.125
        self.ReSizeGLScene(self.width,self.height)
        
    def decreasethickness(self):
        self.slice = self.slice-1.
        
    def increasethickness(self):
        self.slice = self.slice+1.
        
class GLWindow:
    def __init__(self,Width,Height,canvas):
        glutInit("")
            
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_ALPHA | GLUT_DEPTH)
        glutInitWindowSize(Width,Height)
        glutInitWindowPosition(0, 0)
        self.canvas = canvas
        self.window = glutCreateWindow("dicomviewer")
        glutDisplayFunc(self.DrawGLScene)
        glutIdleFunc(self.DrawGLScene)
        glutReshapeFunc(self.ReSizeGLScene)
        glutKeyboardFunc(self.keyPressed)
        glutSpecialFunc(self.specialkeypressed)
        glutMouseFunc(self.mouseFunc)
        self.bool = False
        #glutFullScreen()
    
    def DrawGLScene(self):
        self.canvas.DrawGLScene()	    
        #  Echanger les buffers pour afficher celui dans lequel on a ecrit 
        glutSwapBuffers()
        
    def ReSizeGLScene(self,x,y):
        self.canvas.ReSizeGLScene(x,y)
        
    def keyPressed(self,key,x,y):
        key = ord(key)
        if key == ESCAPE:
            glutDestroyWindow(self.window)
            sys.exit()
        elif key== E_CHAR:
            self.bool = not self.bool
            if(self.bool):
                glutFullScreen()
            else:
                glutReshapeWindow(640, 480)
                glutPositionWindow(0,0);
        elif key == D_CHAR:
            self.canvas.increasextranslation()
        elif key == Q_CHAR:
            self.canvas.decreasextranslation()
        elif key == Z_CHAR:
            self.canvas.increaseytranslation()
        elif key == S_CHAR:
            self.canvas.decreaseytranslation()
        elif key == KEY_PL:
            self.canvas.increasethickness()
        elif key == KEY_MI:
            self.canvas.decreasethickness()
            
    def specialkeypressed(self,key,x,y):
        if key == LEFTXY:
            self.canvas.decreasexyrotation()
        elif key == RIGHXY:
            self.canvas.increasexyrotation()
        elif key == DOARYZ:
            self.canvas.decreaseyzrotation()
        elif key == UPARYZ:
            self.canvas.increaseyzrotation()
        elif key == LEARXZ:
            self.canvas.decreasexzrotation()
        elif key == RIARXZ:
            self.canvas.increasexzrotation()
            
    def mouseFunc(self,key,state,x,y):
        if key==UPMOUS:
            self.canvas.increasezoom()
        elif key==DOMOUS:
            self.canvas.decreasezoom()
            
    def run(self):
        glutMainLoop()

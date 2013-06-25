dicomviewer
===========

A simple volume dicom viewer

Code inspired from the OpenGL NeHe tutorials (http://nehe.gamedev.net/)

Viewing 3D dicom volumes is inefficient. Converting from dicom slices to
nifti volumes is more interesting. Please consider doing it.

I think the code is a good introduction to 3D texture rendering in Python using
OpenGL (if you want to use MIP).

Tester under Ubuntu 12.04 and Debian Wheezy. The application is known to fail
with some dicom images: due to the huge amount of dicom files possibilities,
python dicom is not able to read each of them.

If you have ANY question or suggestion do not hesitate to contact me at:
remy.vandaele@gmail.com

1. Requirements : 

Python Opengl (http://pyopengl.sourceforge.net/), python-opengl under Ubuntu
and Debian.

Python Dicom  (http://code.google.com/p/pydicom/), python-dicom under Ubuntu and
Debian.

numpy (http://www.numpy.org/), python-numpy under Ubuntu and Debian

scipy (http://www.scipy.org/), python-scipy under Ubuntu and Debian

2. Utilisation :

$python dicomviewer file.txt

where file.txt is organized as follows:
/path/to/slice1.dcm
/path/to/slice2.dcm
...
/path/to/slicen.dcm

The slice must be of the same size.


Use mouse wheel to zoom and unzoom
Q to translate left
D to translate right
Z to translate up
S to translate down

LEFT to rotate - along the axis xy
RIGHT to rotate + along the axis xy
DOWN to rotate - along the axis yz
UP to rotate + along the axis yz
HOME to rotate - along the axis xz
END to rotate + along the axis xz

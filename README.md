# pointsrouges

pointsrouges is a simple user interface (UI), written in python3 with PyQt5, to count objects in an image. It has been designed to count people (e.g., in a crowd). It is very elemental and needs some improvements, in particular in its user interface.

The idea is to use this UI to adjust the results of an algorithm that automatically detects people in a crowd (typically a machine learning algorithm). 

contact: olivier.chapuis@lisn.upsaclay.fr

## How To

Run:

	python3 pointsrouges.py path/image.jpg

If opencv for python3 is installed, the first time you open an image with *pointsrouges*, it runs a face detection algorithm and adds a red dot on the image where it detected a face (the result is limited on a crowd, unfortunately, but see the section on P2PNet below). 

In any case, the first time you open an image with *pointsrouges*, it creates a file
   
	path/image.count   # image is the base name of the image

that contains the coordinates of all the red dots that you will add (and maybe added by the face recognizer). You never need to save this file, it is automatically updated and loaded the next time you open the image.

Then you can pan-and-zoom in the image as with google (drag-and-wheel to pan-and-zoom) and have fun by adding red dots on the faces of the people by clicking on them. The number of red dots is displayed at the bottom of the window. 

You can also:

- Change the size of the red dots with the bottom right drop-down menu

- Remove the latest added dots by using the undo button (undo is very limited for now and maybe forever).

- Add a series of dots by drawing a rectangle by either using Shift-Drag or the "Add Dots" button (and then drag on the window). After you finish drawing the rectangle, a dialogue will ask you how many lines and columns of dots you want to add.

- Remove a set of dots by drawing a rectangle using Ctrl-Drag or the "Remove Dots" button. You can also remove a single dot with a Ctrl-click or a right-click on it.

- Ctrl-P: print in a jpg file the image with the dots in a file named image-print-xxxx.jpg in the same image directory, where xxx is the value of the counter and image is the base name of the image.

- Open another image with the Open Image button.


## P2PNet 

In an academic context, I suggest using P2PNet to create an initial set of red dots:

https://github.com/tencentyouturesearch/crowdcounting-p2pnet

more on this later
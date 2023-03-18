# pointsrouges

*pointsrouges* is a simple user interface (UI), written in python3 with PyQt5, to count objects in an image. It has been designed to count people (e.g., in a crowd). It is very elemental and needs some improvements, in particular in its user interface.

The idea is to use this UI to adjust the results of an algorithm that automatically detects people in a crowd (typically a machine learning algorithm). 

contact: olivier.chapuis@lisn.upsaclay.fr

## How To

Run:

	python3 pointsrouges.py path/image.jpg

If opencv for python3 is installed, the first time you open an image with *pointsrouges*, it runs a face detection algorithm and adds a red dot on the image where it detected a face (the result is limited on a crowd, unfortunately, but see the section on P2PNet below). 

In any case, the first time you open an image with *pointsrouges*, it creates a file
   
	path/image.count   # image is the base name of the image

that contains the coordinates of all the red dots that you will add (and maybe added by the face recognizer). You never need to save this file, it is automatically updated and loaded the next time you open the image.

Then you can pan-and-zoom in the image as with google map (drag-and-wheel to pan-and-zoom) and have fun by adding red dots on the faces of the people by clicking on them. The number of red dots is displayed at the bottom of the window. 

You can also:

- Change the size of the red dots with the bottom right drop-down menu

- Remove the latest added dots by using the undo button (undo is very limited for now and maybe forever).

- Add a series of dots by drawing a rectangle by either using Shift-Drag or the "Add Dots" button (and then drag on the window). After you finish drawing the rectangle, a dialogue will ask you how many lines and columns of dots you want to add.

- Remove a set of dots by drawing a rectangle using Ctrl-Drag or the "Remove Dots" button. You can also remove a single dot with a Ctrl-click or a right-click on it.

- Ctrl-P: print in a jpg file the image with the dots in a file named image-print-xxxx.jpg in the same image directory, where xxx is the value of the counter and image is the base name of the image.

- Open another image with the Open Image button.


## P2PNet 

There is lot of research on counting people in a crowd:

https://paperswithcode.com/task/crowd-counting

I tested P2PNet to create an initial set of red dots for *pointsrouges*:

https://github.com/tencentyouturesearch/crowdcounting-p2pnet

Note that the use of *P2PNet* is restricted to academic use (if I well understand)

### P2PNet howto

Follow the following step:

* Install:

You need a computer that support CUDA (NVIDIA GPU) and several python3 library with cuda support (pytorch, pytorchvision, etc.) or not (TODO): see the P2PNet Readme (I use the latest stable version of torch, torchvision, etc.).

In the *pointsrouges* directory:

	git clone https://github.com/TencentYoutuResearch/CrowdCounting-P2PNet.git

Apply the p2pnet.patch patch:
	
	cd CrowdCounting-P2PNet
	git apply ../patches/p2pnet.patch
	mkdir logs/

* Use:

To detect people in an image path/image.jpg:

	 __NV_PRIME_RENDER_OFFLOAD=1 CUDA_VISIBLE_DEVICES=0 python3 run_test.py --weight_path ./weights/SHTechA.pth --output_dir ./logs/  --image path/image.jpg --scale 0.35

if everything work well *P2PNet* build a file:

	path/image.dlcount

with the coordinates of the points where it detected a person. It also output images pred-[orig,scaled]-XXX.jpg in logs/ where XXX is the number of people detected in the image. If you have a "CUDA out of memory" error you should reduce the number of the --scale option (you can start with --scale 1.0 and reduce the scale until you do not get the memory error).

Then you can use *pointsrouges* (after moving or removing path/image.count if any):

	python3 pointsrouges.py path/image.jpg

it will automatically load the ".dlcount" file, and then you can edit the red dots (the ".count" file is used to save you work, and used at the next loading).

### Help for installing and running *P2PNet*

TODO. For now, ask me by email.

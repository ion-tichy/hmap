Hmap
====

Fork of Hmap, an image histogram remapping script written in Python 2.7 by [Anthony Kesich](http://akesich.com) and [Ross Goodwin](http://rossgoodwin.com). Changes source image so that source image's histogram matches target image's histogram. Requires PIL/Pillow:

    $ sudo pip install Pillow

To run Hmap, cd into the directory where hmap.py  is located. Ensure source and target images have the same height and width dimensions (in pixels), and place them in the directory. Run the script with 2 additional arguments (source and target image files) as shown in the following example.
This version will detect if your source image is grayscale or color.
The resulting image will be stored in the same directory as output.jpg

Example:

    $ python hmap.py source_image.jpg target_image.jpg


hmap.py (Grayscale Mode)
=======

Source Image:

![Source Image](http://imgur.com/MGCUWZo.jpg "Source Image")


Target Image:

![Target Image](http://imgur.com/vuGrjAY.jpg "Target Image")


Result:

![Result](http://imgur.com/KavoDjf.jpg "Result")

*Photographs by Ansel Adams*


hmap.py (Color Mode)
=========

Color Source Image:

![Color Source Image](http://imgur.com/2KzkN8p.jpg "Color Source Image")

Color Target Image:

![Target Image](http://imgur.com/VyaVBkQ.jpg "Target Image")

Result:

![Result](http://imgur.com/kiNBR57.jpg "Result")

*Photographs by Steve McCurry*

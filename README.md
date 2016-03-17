## wm-ocr
Water meter optical character recognition (WM-OCR for short) is a collection 
of scripts for automatic collection of water usage data from analogue water
usage meters. The scripts mainly provide utilities for filtering, OCR using 
Tesseract CLI, and data insertion in InfluxDB. 

This project was originally developed for the course KTH AG1815 Sustainable 
Development, ICT and Innovation.

***Project members:***
kalleg,
fcurringa,
bandit738,
Arouzen,
skogsfaktor


### filtering.py
This script provides a interface for converting colored images with shadows 
and other artifacts to pure black and white image. 
This filter is actually a combination of filters:
* Blur filter to spread the digits' black pixels and avoid "holes" in the digits
* Threshold filter to keep only the digits as black pixels (and unfortunately some noise)
* Sharpening filter to make the digits fancier
* Custom grid filter to isolate and delete the remaining noise

**1. Import from filtering.py**

```python
 import filtering as filt
```

**2. Call filter**

```python
 filt.imfilter(imname, sourcefolder, outputfolder)
```

Parameter              | Comment
---------------------- | ------------------------------------------------------
[String] image name    | The name of the image (ex: "50752.jpg")
[String] source folder | The folder where the image is located (ex: "unfiltered/")
[String] output folder | The folder here the image will be saved (ex: "filtered/")

```python
 imfilter(imname, sourcefolder, outputfolder, dbfilename="filterdb", debug=False, forcethr=0)
```

Optional Parameter     | Comment
---------------------- | ------------------------------------------------------
[String] dbfilename    | The path to the filter database file (default: "filterdb")
[Bool]   debug         | Enters debug mode to output more information (default: False)
[Float]  forcethr      | Forces the threshold filter to use this level value if >0 (default: 0)

Example:

```python
 filt.imfilter("50751.jpg", "unfiltered/", "filtered/")
 filt.imfilter("unfiltered/50751.jpg", "", "filtered/")
```

*These two lines are equivalent and both save the image to "filtered/50751.jpg".*

**3. Understanding the filterdb file**

The purpose of this filter is to be as autonomous as possible, and allow the user not to worry about its internal process. However, the threshold value for the threshold filter is an important parameter and the output is very sensitive on this parameter.
Empirical observations showd that the threshold value and the image contrast were highly correlated, and that to one contrast value corresponded only one threshold value. So our idea is to estimate the function threshold = f(contrast), and enable the filter to compute the threshold value according to the image contrast it can easily evaluate.
However, this fuction is hard to compute theoritically, so we chose to approximate it with polynomial fitting. To do so, we need points to map our polynomial and allow it to have a higher order.
There are currently only 2 points so the polynomial is an affine function, but data can be inserted to the file by the user. This is detailed in the next section.

** 4. Enhancing the filter database**

Data can be inserted to the filterdb file by following the provided syntax. When an image is input to the filter, it computes its contrast and it uses the database file to fit a polynomial to the provided points. If the contrast is near from a known point, then the output should be good but otherwise the model may be inaccurate. This tipically happens when a new camera is setup and its contrast is far from the other cameras' one.
Here is a suggested workflow for inserting data to the filterdb file:
* Take one image out of this new camera (an image that represent well the camera's image quality) ;
* Apply the filter in debug mode (it will output the contrast value and the computed threshold) ;
* Checks the output image and identify the issue (too white or too black ?) ;
* If it is too black, the threshold should be lowered and otherwise, it should be raised ;
* Adjust the threshold using the manual mode (forcethr) until the output is good for Tesseract ;
* Add to the filterdb file a line with the image contrast and the estimated threshold.
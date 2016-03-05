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

**1. Import from filtering.py**

```python
 import filtering as filt
```

**2. Call filter/3**

```python
 filt.filter(imname, sourcefolder, outputfolder)
```

Parameter              | Comment
---------------------- | ------------------------------------------------------
[String] image name    | The name of the image (ex: "50752.jpg")
[String] source folder | The folder where the image is located (ex: "unfiltered/")
[String] output folder | The folder here the image will be saved (ex: "filtered/")

Example:

```python
 filt.filter("50751.jpg", "unfiltered/", "filtered/")
 filt.filter("unfiltered/50751.jpg", "", "filtered/")
```

*These two lines are equivalent and both save the image to "filtered/50751.jpg".*

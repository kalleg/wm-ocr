import numpy
import cv2
import csv
import warnings


def filternoise(img, horizontal_thr, authorized):
    """
    Filters out the black pixels that are not part of the digits and are near from the image borders

    :type img: numpy.array
    :type horizontal_thr: int
    :type authorized: int

    :param img: the image to be filtered
    :param horizontal_thr: the threshold on the min number of black pixels per line to allow a line not to be deleted
    :param authorized: the maximum distance from the bottom and the top of the image a line can be erased
    :return: filtered image
    """
    for i in range(0, len(img)):
        line = [255-x for x in img[i, :]]
        buff = float(numpy.sum(line))/255
        if(buff < horizontal_thr) and ((i < authorized) or (i > len(img)-authorized)):
            img[i, :] = [255 for x in line]
    return img


def safeblur(img, avg_size, thr):
    """
    Blurs the image and then apply a threshold filter

    :type img: numpy.array
    :type avg_size: int
    :type thr: float

    :param img: the image to be filtered
    :param avg_size: the size of the blur kernel
    :param thr: the threshold value for the threshold filter
    :return: filtered image
    """
    blur = cv2.GaussianBlur(img, (avg_size, avg_size), 0)
    blur = rescalevalues(blur)
    img_thres2 = thresholder(blur, thr)
    return img_thres2


def safesharp(img):
    """
    Sharpens the image

    :type img: numpy.array

    :param img: the image to be filtered
    :return: filtered image
    """
    img_sharp = cv2.addWeighted(img, 15, 0, -0.5, 0)
    img_sharp = rescalevalues(img_sharp)
    return img_sharp


def rescalevalues(img):
    """
    Ensures that all the pixel values are between 0 and 255

    :type img: numpy.array

    :param img: the image to be filtered
    :return: filtered image
    """
    for i in range(0, len(img)):
        for j in range(0, len(img[0])):
            if img[i, j] < 0:
                img[i, j] = 0
            if img[i, j] > 255:
                img[i, j] = 255
    return img


def computethreshold(img, filestr, debug=0, forcethr=0):
    """
    Uses the database and polynom fitting to compute the threshold
    value for threshold filter according to the image contrast

    :type img: numpy.array
    :type filestr: str
    :type debug: bool
    :type forcethr: float

    :param img: the image to be filtered
    :param filestr: the path to the filter database
    :param debug: enters debug mode
    :param forcethr: (optional) bypasses the computation and force the function to output forcethr
    :return: threshold value for the threshold filter
    """
    m = numpy.std(img)
    if not forcethr:
        warnings.simplefilter("ignore", numpy.RankWarning)
        dbfile = open(filestr, 'r')
        reader = csv.reader(filter(lambda row: row[0] != '#', dbfile))
        allrows = [map(float, row) for row in reader]
        x = [e[0] for e in allrows]
        y = [e[1] for e in allrows]
        z = numpy.polyfit(x, y, len(x))
        pol = numpy.poly1d(z)
        out = pol(m)
    else:
        out = forcethr
    if debug:
        print("Contrast value : "+str(m))
        print("Threshold value: "+str(out)+"\n")
    return out


def concatpatches(imout, buff):
    """
    Safely concatenates image in a vertical way, used for dissociate()

    :type imout: numpy.array
    :type buff: numpy.array

    :param imout: the first part of the image to be concatenated
    :param buff: the second part of the image to be concatenated
    :return: concatenated image
    """
    if len(imout) == 0:
        return buff
    else:
        out = numpy.concatenate((imout, buff), 1)
        return out


def setbrightness(im, lv):
    """
    Increases (or lower) the image's brightness

    :type im: numpy.array
    :type lv: int

    :param im: the raw image
    :param lv: the level to increase the image brightness
    :return: filtered image
    """
    for i in range(0, len(im)):
        line = im[i, :]
        line += lv
        hv = line > 255
        line[hv] = 255
        im[i, :] = line
    return im


def thresholder(blur, lv):
    """
    Applies the threshold filter (if the pixel value is under lv it is black, else white)

    :type blur: numpy.array
    :type lv: float

    :param blur: the image to be threshold-filtered
    :param lv: the threshold level (if <lv it becomes black, else white)
    :return: filtered image
    """
    _img = numpy.zeros((len(blur), len(blur[0])))
    for i in range(0, len(blur)):
        for j in range(0, len(blur[0])):
            if blur[i, j] < lv:
                _img[i, j] = 0
            else:
                _img[i, j] = 255
    return _img


def dissociate(img):
    """
    Filters out all black pixels that are not part of the digits

    :type img: numpy.array

    :param img: the image to be filtered
    :return: filtered image
    """
    # ranges: to detect digits positions on x axis in the image
    img = rescalevalues(img)
    s = 255*len(img) - numpy.sum(img, 0)
    s = (s > 0)
    s = numpy.diff(s)
    ranges = numpy.where(s != 0)
    ranges = ranges[0]
    imout = []
    for i in range(0, len(ranges)-1):
        # buff: nb_lines*delta(range)
        # we will sum on columns
        buff = img[0:len(img), ranges[i]:ranges[i+1]]
        d = 255*len(buff[0]) - numpy.sum(buff, 1)
        d = (d > 0)
        d = numpy.diff(d)
        rg = numpy.where(d != 0)
        rg = rg[0]
        rg = [e for e in rg]
        if (len(rg) > 2) or (len(rg) == 2 and numpy.sum(buff[0]) > 0):
            # rg: nb_lines*1
            buff = extractroi(buff)
        if len(buff[0]) < 10:
            buff = 255*numpy.ones((len(buff), len(buff[0])))
        imout = concatpatches(imout, buff)
    if len(ranges) == 0:
        # if the image is plain white or black
        imout = img
    return imout


def extractroi(img):
    """
    Detects the black patches whose vertical extension is low and filters them out

    :type img: numpy.array

    :param img: the image to be filtered
    :return: filtered image
    """
    try:
        # We try to filter out the patch, sometimes concatenations with badly defined tables occur and it raises
        # runtime errors. The solution now is to catch them and forsake the filtering of this patch.
        d = 255*len(img[0]) - numpy.sum(img, 1)
        d = (d > 0)
        d = numpy.diff(d)
        ranges = numpy.where(d != 0)  # We isolate line blocks where there is at least one black pixel
        ranges = ranges[0]
        ranges = [e for e in ranges]
        ranges = [0] + ranges + [len(img)]
        score = []
        for i in range(0, len(ranges)-1):
            buff = img[ranges[i]:ranges[i+1], 0:len(img[0])]
            buff = 255*len(buff[0])*len(buff) - numpy.sum(buff)
            score = score + [numpy.sum(buff)]
        maxsc = numpy.argmax(score)
        if ranges[maxsc + 1] - ranges[maxsc] < len(img)/3:
            # This threshold could be tuned: we want to filter out the blocks of black pixels that are too
            # small to actually be digits
            mid = 255*numpy.ones((ranges[maxsc + 1] - ranges[maxsc], len(img[0])))
        else:
            mid = img[ranges[maxsc]:ranges[maxsc+1]]
        if ranges[maxsc] > 0:
            beg = 255*numpy.ones((ranges[maxsc]-1, len(img[0])))
        else:
            beg = 255*numpy.ones((0, len(img[0])))
        # We merge all treated patches, it would be useful to check if the
        # final size is the same as the input image one
        end = 255*numpy.ones((len(img)-ranges[maxsc+1]+1, len(img[0])))
        imout = numpy.concatenate((beg, mid))
        imout = numpy.concatenate((imout, end))
        if ranges[maxsc] == 0:
            imout = imout[1:len(imout), 0:len(imout[0])]
        if len(imout) < len(img):
            raise Exception
    except:
        imout = img
    return imout


def uncrop(img):
    """
    Adds 20 pixels at each border of the image to ease Tesseract's work

    :type img: numpy.array

    :param img: the image to be uncropped
    :return: filtered image
    """
    i = 0
    _img = 255*numpy.ones((len(img)+20, len(img[0])+20))
    for line in img:
        line = numpy.concatenate((255*numpy.ones(10), line, 255*numpy.ones(10)))
        _img[i] = line
        i += 1
    _img = numpy.concatenate((255*numpy.ones((10, len(_img[0]))), _img, 255*numpy.ones((10, len(_img[0])))))
    return _img


def imfilter(imname, sourcefolder, outputfolder, dbfilename="filterdb", debug=False, forcethr=0):
    """
    The main function, applies all the filters to the raw image

    :type imname: str
    :type sourcefolder: str
    :type outputfolder: str
    :type dbfilename: str
    :type debug: bool
    :type forcethr: float

    :param imname: the name of the image to be filtered
    :param sourcefolder: the folder it is located (ex: unfiltered/)
    :param outputfolder: the folder where the output will be written (ex: filtered/)
    :param dbfilename: the name of the database file (if not specified: "filterdb")
    :param debug: (optional) enters debug mode
    :param forcethr: (optional) forces the threshold filter to use this level value
    :return: void
    """
    # Blur parameter: the higher the more the digits are "spread"
    # Modification is not encouraged
    avg_size = 5

    # Read raw image and increase brightness
    img = cv2.imread(sourcefolder+imname, 0)
    if debug: print(sourcefolder+imname)
    img = setbrightness(img, 40)

    # Compute the threshold according to DB
    thr = computethreshold(img, dbfilename, debug, forcethr)

    # Crop to avoid black borders
    img = img[20:len(img)-20, 20:len(img[0])-20]

    # Threshold and blur
    img_thres = safeblur(img, avg_size, thr)

    # Sharpening (parameters to be tuned)
    img_sharp = safesharp(img_thres)

    # Delete remaining noise with custom grid algorithm
    img_final = dissociate(img_sharp)

    # Add some white pixels at the borders to help Tesseract
    img_final = uncrop(img_final)

    # Saves the image
    cv2.imwrite(outputfolder+imname, img_final)

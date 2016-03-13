import numpy
import cv2


def filternoise(img, horizontal_thr, authorized):
    for i in range(0, len(img)):
        line = [255-x for x in img[i, :]]
        buff = float(numpy.sum(line))/255
        if(buff < horizontal_thr) and ((i < authorized) or (i > len(img)-authorized)):
            img[i, :] = [255 for x in line]
    return img


def safeblur(img, avg_size, thr):
    blur = cv2.GaussianBlur(img, (avg_size, avg_size), 0)
    blur = rescalevalues(blur)
    img_thres2 = thresholder(blur, thr)
    return img_thres2


def safesharp(img):
    img_sharp = cv2.addWeighted(img, 15, 0, -0.5, 0)
    img_sharp = rescalevalues(img_sharp)
    return img_sharp


def rescalevalues(img):
    for i in range(0, len(img)):
        for j in range(0, len(img[0])):
            if img[i, j] < 0:
                img[i, j] = 0
            if img[i, j] > 255:
                img[i, j] = 255
    return img


def computethreshold(img):
    m = numpy.std(img)
    return -2.43*m+168.14


def concatpatches(imout, buff):
    if len(imout) == 0:
        return buff
    else:
        out = numpy.concatenate((imout, buff), 1)
        return out


def setbrightness(im, lv):
    for i in range(0, len(im)):
        line = im[i, :]
        line += lv
        hv = line > 255
        line[hv] = 255
        im[i, :] = line
    return im


def thresholder(blur, lv):
    _img = numpy.zeros((len(blur), len(blur[0])))
    for i in range(0, len(blur)):
        for j in range(0, len(blur[0])):
            if blur[i, j] < lv:
                _img[i, j] = 0
            else:
                _img[i, j] = 255
    return _img


def dissociate(img):
    # ranges: to detect digits positions on x axis in the image
    # img: nb_lines*nb_col
    s = 255*len(img) - numpy.sum(img, 0)
    s = (s > 0)
    s = numpy.diff(s)
    ranges = numpy.where(s != 0)
    ranges = ranges[0]
    imout = []
    for i in range(0, len(ranges)-1):
        # buff: nb_lines*delta(range)
        # we will sum on columns
        #buff = [numpy.asarray(x[ranges[i]:ranges[i+1]]) for x in img]
        buff = img[0:len(img), ranges[i]:ranges[i+1]]
        cv2.imwrite("buff.jpg", buff)
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
    return imout


def extractroi(img):
    d = 255*len(img[0]) - numpy.sum(img, 1)
    d = (d > 0)
    d = numpy.diff(d)
    ranges = numpy.where(d != 0)
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
        mid = 255*numpy.ones((ranges[maxsc + 1] - ranges[maxsc], len(img[0])))
    else:
        mid = img[ranges[maxsc]:ranges[maxsc+1]]
    if ranges[maxsc] > 0:
        beg = 255*numpy.ones((ranges[maxsc]-1, len(img[0])))
    else:
        beg = 255*numpy.ones((0, len(img[0])))
    end = 255*numpy.ones((len(img)-ranges[maxsc+1]+1, len(img[0])))
    imout = numpy.concatenate((beg, mid))
    imout = numpy.concatenate((imout, end))
    if ranges[maxsc] == 0:
        imout = imout[1:len(imout), 0:len(imout[0])]
    return imout


def uncrop(img):
    i = 0
    _img = 255*numpy.ones((len(img)+20, len(img[0])+20))
    for line in img:
        line = numpy.concatenate((255*numpy.ones(10), line, 255*numpy.ones(10)))
        _img[i] = line
        i += 1
    _img = numpy.concatenate((255*numpy.ones((10, len(_img[0]))), _img, 255*numpy.ones((10, len(_img[0])))))
    return _img


def filter(imname, sourcefolder, outputfolder):
    """
    :param imname: [string] the name of the image to be filtered
    :param sourcefolder: [string] the folder it is located (ex: unfiltered/)
    :param outputfolder: [string] the folder where the output will be written (ex: filtered/)
    :return: void
    """
    avg_size_1 = 5
    avg_size_2 = 3
    avg_size_3 = 5
    avg_size_4 = 5
    avg_size_5 = 3

    img = cv2.imread(sourcefolder+imname, 0)
    img = setbrightness(img, 40)
    cv2.imwrite("test.jpg", img)
    thr = computethreshold(img)

    img = img[20:len(img)-20, 20:len(img[0])-20]
    # Threshold
    blur = img
    #blur = cv2.GaussianBlur(img, (avg_size_1, avg_size_1), 0)
    #blur = numpy.multiply(blur, 2)
    #blurf = blur
    #ret3, img_thres = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    img_thres = safeblur(img, avg_size_1, thr)
    #img_thres = thresholder(blur, thr)
    cv2.imwrite("blur.jpg", blur)
    cv2.imwrite("thr.jpg", img_thres)
    # Blur image
    #img_blur = cv2.GaussianBlur(img_thres, (avg_size_2, avg_size_2), 0)
    img_blur = safeblur(img_thres, avg_size_2, thr+15)
    cv2.imwrite("blurr.jpg", img_blur)

    # Sharpening (parameters to be tuned)
    #buff = cv2.GaussianBlur(img_blur, (avg_size_3, avg_size_3), 3)
    #img_sharp = cv2.addWeighted(buff, 15, 0, -0.5, 0)
    img_sharp = safesharp(img_blur)
    cv2.imwrite("sharp.jpg", img_sharp)

    # Threshold
    #blur = cv2.GaussianBlur(img_sharp, (avg_size_4, avg_size_4), 0)
    #img_thres2=blur
    img_thres2 = safeblur(img_sharp, avg_size_4, thr+15)
    cv2.imwrite("blur2.jpg", blur)
    #img_thres2 = thresholder(img_thres2, thr)
    #ret3, img_thres2 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Filter out part of the noise created by shadows
    img_thres2 = rescalevalues(img_thres2)
    img_noisefil = filternoise(img_thres2, 55, 5)
    cv2.imwrite("noise.jpg", img_noisefil)

    # Blur image
    img_blur = cv2.GaussianBlur(img_noisefil, (avg_size_5, avg_size_5), 0)
    cv2.imwrite("blur3.jpg", img_blur)
    # Sharpening (parameters to be tuned)
    img_sharp = cv2.addWeighted(img_blur, 15, 0, -0.5, 0)

    # Threshold
    img_thres3=img_sharp
    #ret3, img_thres3 = cv2.threshold(img_sharp, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
    cv2.imwrite("sharp2.jpg", img_sharp)
    # Dissociate image to filter out irrelevant black lines
    img_thres3=rescalevalues(img_thres3)
    cv2.imwrite("prefinal.jpg", img_thres3)
    img_final = dissociate(img_thres3)
    cv2.imwrite("dissoc.jpg", img_final)
    img_final = uncrop(img_final)

    cv2.imwrite(outputfolder+imname, img_final)

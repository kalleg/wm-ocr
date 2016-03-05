import numpy
import cv2


def filternoise(img, horizontal_thr, authorized):
    for i in range(0, len(img)):
        line = [255-x for x in img[i, :]]
        buff = float(numpy.sum(line))/255
        if(buff < horizontal_thr) and ((i < authorized) or (i > len(img)-authorized)):
            img[i, :] = [255 for x in line]
    return img


def concatpatches(imout, buff):
    if len(imout) == 0:
        return buff
    else:
        out = numpy.concatenate((imout, buff), 1)
        return out


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
        buff = [numpy.asarray(x[ranges[i]:ranges[i+1]]) for x in img]
        d = 255*len(buff[0]) - numpy.sum(buff, 1)
        d = (d > 0)
        d = numpy.diff(d)
        rg = numpy.where(d != 0)
        rg = rg[0]
        if len(rg) > 2:
            # rg: nb_lines*1
            buff = extractroi(buff)
        imout = concatpatches(imout, buff)
    return imout


def extractroi(img):
    d = 255*len(img[0]) - numpy.sum(img, 1)
    d = (d > 0)
    d = numpy.diff(d)
    ranges = numpy.where(d != 0)
    ranges = ranges[0]
    score = []
    for i in range(0, len(ranges)-1):
        buff = img[ranges[i]:ranges[i+1]]
        buff = 255*len(buff[0]) - numpy.sum(buff, 1)
        score = score + [numpy.sum(buff)]
    maxsc = numpy.argmax(score)
    if ranges[maxsc + 1] - ranges[maxsc] < len(img[0])/3:
        mid = 255*numpy.ones((ranges[maxsc + 1] - ranges[maxsc], len(img[0])))
    else:
        mid = img[ranges[maxsc]:ranges[maxsc+1]]
    beg = 255*numpy.ones((ranges[maxsc]-1, len(img[0])))
    end = 255*numpy.ones((len(img)-ranges[maxsc+1]+1, len(img[0])))
    imout = numpy.concatenate((beg, mid))
    imout = numpy.concatenate((imout, end))
    return imout


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
    img = img[20:210, 20:880]
    # Threshold
    blur = cv2.GaussianBlur(img, (avg_size_1, avg_size_1), 0)
    #blur = numpy.multiply(blur, 2)
    blurf = blur
    ret3, img_thres = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Blur image
    img_blur = cv2.GaussianBlur(img_thres, (avg_size_2, avg_size_2), 0)

    # Sharpening (parameters to be tuned)
    buff = cv2.GaussianBlur(img_blur, (avg_size_3, avg_size_3), 3)
    img_sharp = cv2.addWeighted(buff, 15, 0, -0.5, 0)

    # Threshold
    blur = cv2.GaussianBlur(img_sharp, (avg_size_4, avg_size_4), 0)
    ret3, img_thres2 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Filter out part of the noise created by shadows
    img_noisefil = filternoise(img_thres2, 100, 35)

    # Blur image
    img_blur = cv2.GaussianBlur(img_noisefil, (avg_size_5, avg_size_5), 0)

    # Sharpening (parameters to be tuned)
    img_sharp = cv2.addWeighted(img_blur, 15, 0, -0.5, 0)

    # Threshold
    ret3, img_thres3 = cv2.threshold(img_sharp, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)

    # Dissociate image to filter out irrelevant black lines
    img_final = dissociate(img_thres3)

    cv2.imwrite(outputfolder+imname, img_final)

import filtering as filt
from os import listdir
from os.path import isfile, join

# This path is to be adapted
inpath = "/home/florian/Images/unfiltered/somecam12/"
outpath = "/home/florian/Images/filtered/somecam12/"

# Reads all files in directory inpath
onlyfiles = [f for f in listdir(inpath) if isfile(join(inpath, f))]

# Filter is applied to all image files
for e in onlyfiles:
    filt.imfilter(e, inpath, outpath, debug=True)

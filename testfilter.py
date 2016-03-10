import filtering as filt
from os import listdir
from os.path import isfile, join

mypath = "/home/florian/Images/unfiltered"

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

for e in onlyfiles:
    filt.filter(e, mypath+"/", "/home/florian/Images/filtered/")

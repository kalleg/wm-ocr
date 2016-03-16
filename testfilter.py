import filtering as filt
from os import listdir
from os.path import isfile, join

mypath = "/home/florian/Images/unfiltered"

onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

#for e in onlyfiles:
#e = "cam12-20160309_040001_rot_65_crop.jpg"
e = "30734.jpg"
filt.imfilter(e, mypath+"/", "/home/florian/Images/filtered/bases/", debug=True)

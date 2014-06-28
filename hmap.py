# image histogram remapping

from __future__ import print_function
from sys import argv
from PIL import Image
import collections
import random



#source and target images
srcImg = None
tgtImg = None

#load pixel maps
srcPix = None
tgtPix = None

srcHist = None
tgtHist = None

#value list
pxlsByVal = None


#the bins
equalBins = collections.deque()
excessBins = collections.deque()
deficitBins = collections.deque()


#Get histograms of the images
#only take the first 256 values for now since they're B&W
def init_histograms():
    global srcHist,tgtHist
    srcHist = srcImg.histogram()[:256]
    tgtHist = tgtImg.histogram()[:256]

def make_value_list((w,h)):
    for i in range(w):
        for j in range(h):
            value = srcPix[i, j][0]
            pxlsByVal[value].add((i, j))

def sort_bins_into_lists():
    for i, _ in enumerate(srcHist):
        src_i = srcHist[i]
        tgt_i = tgtHist[i]
        if src_i < tgt_i:
            deficitBins.append(i)
        elif src_i > tgt_i:
            excessBins.append(i)
        else:
            equalBins.append(i)
            
def print_bin():
    print("#equal bins: %s\t#excess bins: %s\t#deficit bins: %s" % tuple(
    map(len, (equalBins, excessBins, deficitBins))))


#change one pixel function
def change_n_pixels(curVal, tgtVal, nToChange):
    #find a pixel to change
    candidatePxls = pxlsByVal[curVal]
    chosenPxls = random.sample(candidatePxls, nToChange)

    #change the pixel
    for pxl in chosenPxls:
        srcPix[pxl] = (tgtVal, tgtVal, tgtVal)
        #update pixel list
        pxlsByVal[curVal].remove(pxl)
        pxlsByVal[tgtVal].add(pxl)
    update_histograms(curVal,tgtVal,nToChange)
        
def update_histograms(curVal,tgtVal,nToChange):
    #update the histograms
    srcHist[curVal] -= nToChange
    srcHist[tgtVal] += nToChange


#change one pixel function
def change_n_pixels_smooth(curVal, tgtVal, nToChange):
    Nincrements = abs(curVal - tgtVal)
    for inc in range(Nincrements):
        # This part was throwing IndexErrors, so I adjusted it
        if tgtVal > curVal:
            try:
                change_n_pixels(curVal+inc, curVal+inc+1, nToChange)
            except IndexError:
                pass
        else:
            try:
                change_n_pixels(curVal-inc, curVal-inc-1, nToChange)
            except IndexError:
                pass


#move pixels in excess bins to deficit bins
def move_pixels_excess_to_deficit():
    for curValue in excessBins:
        excess = srcHist[curValue] - tgtHist[curValue]
        if curValue % 5 == 0:
            print("On value", curValue, "with", excess, "excess pixels")
        while excess > 0:
            if deficitBins == collections.deque([]):
                break
            else:
                tgtValue = deficitBins[0]
            deficit = tgtHist[tgtValue] - srcHist[tgtValue]
            if excess > deficit:
                nToMove = excess - deficit
                deficitBins.popleft()
            else:
                nToMove = excess
                if deficit == excess:
                    deficitBins.popleft()

            change_n_pixels_smooth(curValue, tgtValue, nToMove)
            excess -= nToMove



if __name__ == "__main__":
    #cli args
    script, source_image, target_image = argv
    
    #load our source and target images
    srcImg = Image.open(source_image)
    tgtImg = Image.open(target_image)
    #load pixel maps
    srcPix = srcImg.load()
    tgtPix = tgtImg.load()
    
    init_histograms()
    #sort bins into lists
    pxlsByVal = [set() for _ in range(256)]
    make_value_list(srcImg.size)
    sort_bins_into_lists()
    print_bin()
    move_pixels_excess_to_deficit()
    
    #show images --> won't work in win7 and vista (PIL bug)
    #srcImg.show()
    #tgtImg.show()
    srcImg.save('J:\GIT\hmap\output.jpg')
    #srcImg.show()

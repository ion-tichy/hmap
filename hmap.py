# image histogram remapping

from __future__ import print_function
from sys import argv
from PIL import Image
import collections
import random

RGB_Keys = ['R','G','B']
#source and target images
srcImg = None
tgtImg = None

#pixel maps
srcPix = None
tgtPix = None

#histograms
srcHist = None
tgtHist = None

#the different bins
equalBins = {}
excessBins = {}
deficitBins = {}

pxlsByVal = {}


#Get histograms of the images
#Now taking 3 different histograms for each image; 1 for each color channel

def init_histograms():
    global srcHist,tgtHist,RGB_Keys
    if RGB_Keys == ['R','G','B']:
        print("Initializing color histogram")
        srcHist = {'R':srcImg.histogram()[:256],
                   'G':srcImg.histogram()[256:512],
                   'B':srcImg.histogram()[512:]
               }
        tgtHist = {'R':tgtImg.histogram()[:256],
                   'G':tgtImg.histogram()[256:512],
                   'B':tgtImg.histogram()[512:]
               }
    else:
        print("Initializing bw histogram")
        srcHist = {'BW':srcImg.histogram()[:256]}
        tgtHist = {'BW':tgtImg.histogram()[:256]}

def init_bins():
    for chan in RGB_Keys:
        equalBins[chan] = collections.deque()
        excessBins[chan] = collections.deque()
        deficitBins[chan] = collections.deque()

def make_value_list((w,h),ch,ind):
    print("Make value list for channel",ch)
    for i in range(w):
        for j in range(h):
            value = srcPix[i, j][ind]
            pxlsByVal[ch][value].add((i,j))



def sort_bins_into_lists(chan):
    for i, _ in enumerate(srcHist[chan]):
        src_i = srcHist[chan][i]
        tgt_i = tgtHist[chan][i]
        if src_i < tgt_i:
            deficitBins[chan].append(i)
        elif src_i > tgt_i:
            excessBins[chan].append(i)
        else:
            equalBins[chan].append(i)

def print_bin(chan):
    print("For "+str(chan)+"\n#equal bins: %s\t#excess bins: %s\t#deficit bins: %s" % tuple(
    map(len, (equalBins[chan], excessBins[chan], deficitBins[chan]))))

#change one pixel function - RGB    
def change_n_pixels(chan,curVal,tgtVal,nToChange):
    #find a pixel to change
    candidatePxls = pxlsByVal[chan][curVal]
    chosenPxls = random.sample(candidatePxls, nToChange)

    #change the pixel
    for pxl in chosenPxls:
        if chan == "R":
             srcPix[pxl] = (tgtVal, srcPix[pxl][1], srcPix[pxl][2])#R
        elif chan =="G":
             srcPix[pxl] = (srcPix[pxl][0], tgtVal, srcPix[pxl][2])#G
        elif chan == "B":
             srcPix[pxl] = (srcPix[pxl][0], srcPix[pxl][1], tgtVal)#B
        elif chan == "BW":
             srcPix[pxl] = (tgtVal,tgtVal,tgtVal) # Black and white only
        else:
            raise ValueError       
        #update pixel list
        pxlsByVal[chan][curVal].remove(pxl)
        pxlsByVal[chan][tgtVal].add(pxl)

    #update the histograms
    update_histogram(chan,curVal,tgtVal,nToChange)
    
def update_histogram(chan,curVal,tgtVal,n):
    srcHist[chan][curVal] -= n
    srcHist[chan][tgtVal] += n
    
    
def change_n_pixels_smooth(chan,curVal, tgtVal, nToChange):
    Nincrements = abs(curVal - tgtVal)
    for inc in range(Nincrements):
        # This part was throwing IndexErrors, so I adjusted it
        if tgtVal > curVal:
            try:
                change_n_pixels(chan,curVal+inc, curVal+inc+1, nToChange)
            except IndexError:
                print("IndexError"," channel: ",chan)
        else:
            try:
                change_n_pixels(chan,curVal-inc, curVal-inc-1, nToChange)
            except IndexError:
                print("IndexError"," channel: ",chan)

def move_pixels_excess_to_deficit(chan):
    for curValue in excessBins[chan]:
        excess = srcHist[chan][curValue] - tgtHist[chan][curValue]
        if curValue % 5 == 0:
            print("On "+str(chan)+" value", curValue, "with", excess, "excess pixels")
        while excess > 0:
            if deficitBins[chan] == collections.deque([]):
                break
            else:
                tgtValue = deficitBins[chan][0]
            deficit = tgtHist[chan][tgtValue] - srcHist[chan][tgtValue]
            if excess > deficit :
                nToMove = excess - deficit
                deficitBins[chan].popleft()
            else:
                nToMove = excess
                if deficit == excess:
                    deficitBins[chan].popleft()

            change_n_pixels_smooth(chan,curValue,tgtValue,nToMove)
            excess -= nToMove

def check_if_bw_image():
    tmp = srcImg.convert('RGB')
    w,h  = srcImg.size
    for i in range(w):
        for j in range(h):
            R,G,B = tmp.getpixel((i,j))
            if R!= G != B:
                return False
    else:
        return True                
    
if __name__ == "__main__":
    #cli args
    script,source_image,target_image = argv

    #load images
    srcImg = Image.open(source_image)
    tgtImg = Image.open(target_image)
    
    #load pixel maps
    srcPix = srcImg.load()
    tgtPix = tgtImg.load()
    #srcImg.show()
    #tgtImg.show()
    
    #test if image is black and white
    # if not --> same procedure as ever
    # if bw --> only operate on first channel
    if check_if_bw_image():
        RGB_Keys = ['BW'] # only one black channel
    
	#init the histograms
    init_histograms()
	    
    #sort bins into lists
    init_bins()
    
    for i,chan in enumerate(RGB_Keys):
        #make value lists
        pxlsByVal[chan] = [set() for _ in range(256)]
        make_value_list(srcImg.size,chan,i) 
        #sort bins into lists
        sort_bins_into_lists(chan)
        print_bin(chan)
        #move pixels in excess bins to deficit bins 
        move_pixels_excess_to_deficit(chan)

    #write out resulting image
    srcImg.save('output.jpg')
    
    print("--- Done ---")

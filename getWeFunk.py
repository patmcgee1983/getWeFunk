# -*- coding: utf-8 -*-
"""
Created on Mon Jan 10 19:38:07 2022

--==[[[[[ Grab WeFunk Radio Shows ]]]]]==--

@author: Pat McGee

WeFunk is the longest running and the best funk / hip hop / breaks radio ever!
They have been running for over 25 years and continue to provide the highest quality music

Since no plug in exists for KODI, I may have to make one, but for the time being I used this python script
to download the entire series!

This script will start at first show #,  and go to last show #
For each show it will download the show mp3, and the album art, write the ID3 tags and set the album art

Files will be downloaded into same location as script

All ~1000 shows require about 100GB of space




"""

import requests
import re
from bs4 import BeautifulSoup
import os
import eyed3
from eyed3.id3.frames import ImageFrame

TAG_RE = re.compile(r'<[^>]+>')

def remove_tags(text):
    return TAG_RE.sub('', text)


# Show starts at 168
# Last show at time of this was 1100
firstShow = 168
lastShow = 1101


# For each show number
for currentShow in range(firstShow, lastShow):

    print("************ Starting show # "+ str(currentShow) + " ************")
    id = str(currentShow)
    
    # the urls for the the mp3 file, the page containing all the information and the albumart
    mp3 = "http://www.wefunkradio.com/mirror/stream/"+id
    info = "http://www.wefunkradio.com/show/"+id
    albumart = "http://cache.wefunkradio.com/montages/montage-small9sq-show-"+id+".jpg"
    
    
    page = requests.get(info)
    soup = BeautifulSoup(page.content, "html.parser")
    
    showDescription = remove_tags(str(soup.find(id="showdescription")))
    artists = remove_tags(str(soup.find(id="credits")))
    
    # Extract the artists out of the credits div
    try:
        artists = artists.replace('\n','%@').split('%@')[1].replace("DJs &amp; GUESTS","")
    except:
        artists = artists

    print(artists)
    print(showDescription)
    
    
    # Get the albumart image
    print("Requesting album art")
    r = requests.get(albumart, allow_redirects=True)    
    print("Saving albumart to file")
    open("montage-small9sq-show-"+id+".jpg", 'wb').write(r.content)
    
    # Get the mp3
    print("Requesting "+mp3)
    r = requests.get(mp3, allow_redirects=True)
    print("Getting mp3 content...")
    #filename = getFilename_fromCd(r.headers.get('content-disposition'))
    open("Wefunk-Show-"+id+".mp3", 'wb').write(r.content)

    

    print("Setting albumart")
    # If there was an error loading the mp3, delete the file and move on
    # If the mp3 loads successfully, set the track #, albumart and artist tags
    try:
        audiofile = eyed3.load("Wefunk-Show-"+id+".mp3")
        if (audiofile.tag == None):
            audiofile.initTag()
            
        audiofile.tag.images.set(ImageFrame.FRONT_COVER, open("montage-small9sq-show-"+id+".jpg",'rb').read(), 'image/jpeg')
        audiofile.tag.track_num = id
        audiofile.tag.album_artist = u"www.wefunkradio.com"
        audiofile.tag.artist = artists
        audiofile.tag.save(version=eyed3.id3.ID3_V2_3)
        
    except:
        print("Bad mp3 file... removing")
        os.remove("Wefunk-Show-"+id+".mp3")
        os.remove("montage-small9sq-show-"+id+".jpg")
    
#!/usr/bin/python
import sys
import praw
import requests
import urllib
import os.path
from imgurpython import ImgurClient
import BeautifulSoup

import ConfigParser

pathFolder = "downloaded_imagesTest"
counter = 0

def getimgurlink(s):
    client = ImgurClient(client_idImgur, client_secretImgur)
    index1 = s.rfind('.')
    index2 = s.rfind('/')
    if index2 < index1:
        imgid = s[index2+1:index1]
    else:
        imgid = s[index2+1:]
    item = client.get_image(imgid)
    return item.link

def getflickrlink(s):
    print('flickr link:',s)
    if "/in/" not in s:
        opener = urllib.FancyURLopener({})
        page = opener.open(s).read()
        parsed = BeautifulSoup(page)
        div = parsed.find('div', id='allsizes-photo')
        children = div.findChildren()
        return children[0].get('src')
    else:
        return ""

def imgurSave(submission,title):
    if os.path.exists(title + ".jpg") == False:
        link = getimgurlink(submission.url)
        if link == "":
            return False
        downloadFile(title,submission.url)
        return True

def flickrSave(submission,title):
    if os.path.exists(title) == False:
        link = getflickrlink(submission.url)
        if link != "":
            f = open(title,'wb')
            f.write(urllib.urlopen(link).read())
            f.close()

def redditSave(submission,title):
    if os.path.exists(title + ".jpg") == False:
        downloadFile(title,submission.url)
        return True
    return False

def downloadFile(filename,url):
    with open(filename+'.jpg', "wb") as file:
        response = requests.get(url, stream = True)

        fsize = response.headers.get('content-length')

        downloaded = 0

        if fsize is not None:
            fsize = int(fsize)
            print( "%s. Downloading %s") % (counter, filename)
            for packet in response.iter_content(chunk_size = 2048):
                downloaded += len(packet)
                file.write(packet)
                progress = 50 * downloaded/fsize
                sys.stdout.write("\r[%s%s]" % ('=' * int(progress), ' ' * (50 - int(progress))))
                sys.stdout.flush()
        print

def main():
    config = ConfigParser.RawConfigParser()
    config.read('imgur.ini')
    client_idImgur = config.get('credentials', 'client_id')
    client_secretImgur = config.get('credentials', 'client_secret')
    reddit = praw.Reddit('bot1')
    subreddit = reddit.subreddit("EarthPorn")
    if not os.path.exists(pathFolder):
        os.mkdir(pathFolder)
    os.chdir(pathFolder)
    chars = ['!','.',' ','(',')','[',']','\\','/','?','*','|',",",':',"\""]
    first = True
    maxLimit = input('Enter amount of posts to scan:')
    global counter
    counter = 1
    for submission in subreddit.hot(limit=maxLimit):
        title = submission.title
        for char in chars:
            title = title.replace(char,'_')
        if(submission.post_hint == 'image'):
           if redditSave(submission,title) == True:
                counter += 1
        elif submission.post_hint == 'link' and submission.domain == 'imgur.com':
            if imgurSave(submission,title) == True:
                counter += 1
            #elif submission.domain == "flickr.com":
                #flickrSave(submission,title)

    print("---------------------------------\n")
    print "Result:",counter-1,"/",maxLimit

if __name__ == "__main__":
    main()
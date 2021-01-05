import time
from gi.repository import Gst
from gi.repository import GstPbutils

Gst.init()
discoverer = GstPbutils.Discoverer()
info = discoverer.discover_uri('file:///home/eric/Downloads/01.mp4')
mysublist = info.get_subtitle_streams()
print(len(mysublist))
i=0
for x in mysublist:
    print (x.get_language(), i, info.get_subtitle_streams()[i].get_language())
    i+=1
uri = 'file:///home/eric/Downloads/01.mp4'

pipeline=Gst.ElementFactory.make("playbin", "playbin")
pipeline.set_property('uri',uri)
pipeline.set_state(Gst.State.PLAYING)
time.sleep(2)
subs = pipeline.get_property('n-text')
print("there are ", subs, " Subtitles")
auds = pipeline.get_property('n-audio')
print("there are ", auds, " Audio streams")
vids = pipeline.get_property('n-video')
print("there are ", vids, " Video Streams")



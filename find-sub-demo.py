#!/usr/bin/env python
import time
from gi.repository import Gst, GstTag
Gst.init(None)
uri='file:///home/rolf/H.mkv'
pipeline=Gst.ElementFactory.make("playbin", "playbin")
pipeline.set_property('uri',uri)
try:
    prefix = uti.rindex('.')
    suburi = uri[:prefix]
    suburi = suburi+".srt"
    suburi = pipeline.set_property('suburi', suburi)
except:
    pass
pipeline.set_state(Gst.State.PLAYING)
time.sleep(0.5)
subs = pipeline.get_property('n-text')
auds = pipeline.get_property('n-audio')
vids = pipeline.get_property('n-video')
print vids, "Video Streams ", auds, "Audio Streams ", subs, "Subtitle Streams"
subc = pipeline.get_property('current-text')

dur = (pipeline.query_duration(Gst.Format.TIME)[1]) / Gst.SECOND  
hh = int(dur/3600)
mm, ss = (divmod(int(divmod(dur,3600)[1]),60))
print("Duration : %02d:%02d:%02d" % (hh,mm,ss))
for x in xrange(subs):
    tags = pipeline.emit("get-text-tags", x)
    if (tags):
        name = tags.nth_tag_name(0)
        if name == "language-code":
            current_code = tags.get_string(name)[1]
            language = GstTag.tag_get_language_name(current_code)
            print "Subtitle stream ",current_code, "Index ", x, language

    else:
        print "No subtitle tags listed"
print "Currently using Subtitle set ", subc
time.sleep(dur)   
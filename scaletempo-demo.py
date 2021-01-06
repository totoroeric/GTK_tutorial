#!/usr/bin/env python

import os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject, Gtk

class GTK_Main(object):

    def __init__(self):
        window = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        window.set_title("Audio-Player")
        window.set_default_size(300, -1)
        window.connect("destroy", Gtk.main_quit, "WM destroy")
        vbox = Gtk.VBox()
        window.add(vbox)
        self.entry = Gtk.Entry()
        vbox.pack_start(self.entry, False, True, 0)
        self.button = Gtk.Button("Start")
        self.button.connect("clicked", self.start_stop)
        vbox.add(self.button)

        self.switch_speed_button = Gtk.ToggleButton(label="PlaySpeed %")
        self.switch_speed_button.connect("toggled", self.on_speed_toggled, "1")
        vbox.add(self.switch_speed_button)

        window.show_all()

        # self.player = Gst.ElementFactory.make("playbin", "player")
        # print("original audio sink:" + str(self.player.get_property("audio-sink")))
        # self.fakesink = Gst.ElementFactory.make("scaletempo rate=0.5 ! audioconvert ! audioresample ! autoaudiosink", "fakesink")

        # source = Gst.ElementFactory.make("filesrc", "file-source")
# filesrc location="/home/eric/Downloads/S01E22.mkv" ! matroskademux ! vorbisdec ! audioconvert ! audioresample ! autoaudiosink
        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("filesrc", "file-source")

        demuxer = Gst.ElementFactory.make("decodebin", "demuxer")
        demuxer.connect("pad-added", self.demuxer_callback)

        self.queuev = Gst.ElementFactory.make("queue", "queuev")
        vconv = Gst.ElementFactory.make("videoconvert", "vconv")
        vsink = Gst.ElementFactory.make("autovideosink", "video-output")

        self.queuea = Gst.ElementFactory.make("queue", "queuea")
        aconv1 = Gst.ElementFactory.make("audioconvert", "aconv1")
        aresample1 = Gst.ElementFactory.make("audioresample", "aresample1")
        ascale = Gst.ElementFactory.make("scaletempo", "ascacle")
        aconv2 = Gst.ElementFactory.make("audioconvert", "aconv2")
        aresample2 = Gst.ElementFactory.make("audioresample", "aresample2")
        asink = Gst.ElementFactory.make("autoaudiosink", "audio-output")



        self.player.add(source) 
        self.player.add(demuxer) 

        self.player.add(self.queuev) 
        self.player.add(vconv) 
        self.player.add(vsink)

        self.player.add(self.queuea) 
        self.player.add(aconv1) 
        self.player.add(aresample1)
        self.player.add(ascale) 
        self.player.add(aconv2) 
        self.player.add(aresample2)
        self.player.add(asink) 


        source.link(demuxer)

        self.queuev.link(vconv)
        vconv.link(vsink)

        self.queuea.link(aconv1)
        aconv1.link(aresample1)
        aresample1.link(ascale)
        ascale.link(aconv2)
        aconv2.link(aresample2)
        aresample2.link(asink)

        # demuxer.link(self.queuea)
        # demuxer.link(self.queuev)




        bus = self.player.get_bus()
        bus.add_signal_watch()
        # bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        # bus.connect("sync-message::element", self.on_sync_message)

    def start_stop(self, w):
        if self.button.get_label() == "Start":
            filepath = self.entry.get_text().strip()
            if os.path.isfile(filepath):
                filepath = os.path.realpath(filepath)
                self.button.set_label("Stop")
                self.player.get_by_name("file-source").set_property("location", filepath)
                self.player.set_state(Gst.State.PLAYING)
            else:
                self.player.set_state(Gst.State.NULL)
                self.button.set_label("Start")

    def on_speed_toggled(self, widget, name):
        if widget.get_active():
            state = "on"
            self.player.seek(0.65 , Gst.Format.TIME, Gst.SeekFlags.FLUSH, Gst.SeekType.NONE, 0,Gst.SeekType.NONE, 0)

        else:
            state = "off"
            self.player.seek(1.0, Gst.Format.TIME, Gst.SeekFlags.SKIP, Gst.SeekType.NONE, 0,Gst.SeekType.NONE, 0)

    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print("Error: %s" % err, debug)
            self.button.set_label("Start")

    def demuxer_callback(self, demuxer, pad):
        # if pad.get_property("template").name_template == "video_%02d":
        #     qv_pad = self.queuev.get_pad("sink")
        #     pad.link(qv_pad)
        # elif pad.get_property("template").name_template == "audio_%02d":
        #     qa_pad = self.queuea.get_pad("sink")
        #     pad.link(qa_pad)

        string = pad.query_caps(None).to_string()
        print('Found stream: %s' % string)
        if string.startswith('video/x-raw'):
            # qv_pad = self.queuev.get_pad("sink")
            pad.link(self.queuev.get_static_pad('sink'))
        elif string.startswith('audio/x-raw'):
            # qv_pad = self.queuev.get_pad("sink")
            pad.link(self.queuea.get_static_pad('sink'))



Gst.init(None)
GTK_Main()
GObject.threads_init()
Gtk.main()
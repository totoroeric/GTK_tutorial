import gi
import sys, os, _thread, time
gi.require_version('Gst', '1.0')
gi.require_version("Gtk", "3.0")
gi.require_version('GstVideo', '1.0')
from gi.repository import Gtk, Gdk, GObject, Gst

# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='MediaMenu'>
      <menuitem action='OpenFile' />
      <separator />
      <menuitem action='Quit' />
    </menu>
    <menu action='PlaybackMenu'>
        <menuitem action='SpeedUp' />
        <menuitem action='SpeedDown' />
        <menuitem action='ResetSpeed' />
        <separator />
        <menuitem action='JumpForward' />
        <menuitem action='JumpBackward' />
        <menuitem action='JumpToSpecificTime' />
        <separator />
        <menuitem action='Play' />
        <menuitem action='Stop' />
    </menu>
    <menu action='AudioMenu'>
        <menuitem action='AudioTrackNext' />
        <separator />
        <menuitem action='IncreaseVolume' />
        <menuitem action='DecreaseVolume' />
        <menuitem action='Mute' />
    </menu>
    <menu action='VideoMenu'>
    </menu>
    <menu action='SubtitleMenu'>
      <menuitem action='AddSubtitleFile' />
      <menuitem action='SubTrackNext' />
    </menu>
    <menu action='ToolsMenu'>
    </menu>
    <menu action='ViewMenu'>
    </menu>
    <menu action='HelpMenu'>
    </menu>

  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='Play' />
    <toolitem action='Stop' />
    <toolitem action='JumpBackward' />
    <toolitem action='JumpForward' />
  </toolbar>
  <popup name='PopupMenu'>
    <menuitem action='EditCopy' />
    <menuitem action='EditPaste' />
    <menuitem action='EditSomething' />
  </popup>
</ui>
"""

# Oh, got it to work. Had to add a ToolItem into the tooblar, 
# then call toolitem.add(spinbutton).
class myVLCWindow(Gtk.ApplicationWindow):
    def __init__(self):
        Gtk.Window.__init__(self, title="My VLC")

        self.file_name = ""
        self.play_toggle = "play"
        self.stepsize = 5 # 前后跳转步长（秒）
        self.playspeed = 100 
        self.sub_uri = ""

        self.set_default_size(800, 400)
        self.connect("destroy", Gtk.main_quit, "WM destroy")

        action_group = Gtk.ActionGroup(name="my_actions")

        self.add_MediaMenu_actions(action_group)
        self.add_PlaybackMenu_actions(action_group)
        self.add_Audio_actions(action_group)
        self.add_Video_actions(action_group)
        self.add_Subtitle_actions(action_group)
        self.add_Tools_actions(action_group)
        self.add_View_actions(action_group)
        self.add_Help_actions(action_group)

        uimanager = self.create_ui_manager()
        uimanager.insert_action_group(action_group)

        menubar = uimanager.get_widget("/MenuBar")
        toolbar = uimanager.get_widget("/ToolBar")
        # speedtoolbar = uimanager.get_widget("/SpeedToolBar")

        # timeline的容器grid
        timelinegrid = Gtk.Grid() #时间和进度条放这里
        # 定义左右两个time lable
        self.time_label_left = Gtk.Label(label="00:00")
        self.time_label_right = Gtk.Label(label="00:00")
        # 定义scale
        ad = Gtk.Adjustment(0, 0, 100, 1, 10, 0)
        self.scale = Gtk.Scale(orientation=Gtk.Orientation.HORIZONTAL, adjustment=ad)
        self.scale.set_digits(0)
        self.scale.set_hexpand(True)
        self.scale.set_valign(Gtk.Align.START)
        self.scale.connect("value-changed", self.scale_moved)
        # 组装timelinegrid
        timelinegrid.set_column_homogeneous(True)
        timelinegrid.set_column_spacing(10)
        timelinegrid.attach(self.time_label_left, 0, 0, 1, 1)
        timelinegrid.attach_next_to(self.scale, self.time_label_left, Gtk.PositionType.RIGHT, 8, 1)
        timelinegrid.attach_next_to(self.time_label_right, self.scale, Gtk.PositionType.RIGHT, 1, 1)

        # 视频窗口的容器box
        eventbox = Gtk.EventBox()
        # vbox = Gtk.VBox()
        eventbox.connect("button-press-event", self.on_button_press_event)

        # 外围的总box
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)
        box.pack_start(eventbox, True, True, 0)
        # 定义播放视频的窗口区域
        self.movie_window = Gtk.DrawingArea() # 视频窗口
        eventbox.add(self.movie_window)
        box.pack_start(timelinegrid, False, False, 0)

        # 把toolbar和其他一些button放在一行的box
        hbox = Gtk.HBox(spacing=6)

        # 定义跳转脚步大小的spinbutton
        forwardstep_adjustment = Gtk.Adjustment(value=self.stepsize, lower=1, upper=15, step_increment=1, page_increment=5)
        self.forwardstep = Gtk.SpinButton()
        forwardstep_label = Gtk.Label(label="Step Size(Seconds)")
        self.forwardstep.set_adjustment(forwardstep_adjustment)
        self.forwardstep.connect("value-changed", self.on_forwardstep_changed)

        # 定义变速、常速切换开关
        self.switch_speed_button = Gtk.ToggleButton(label="PlaySpeed %")
        self.switch_speed_button.connect("toggled", self.on_speed_toggled, "1")

        # 定义播放速度的spinbutton
        speed_adjustment = Gtk.Adjustment(value=self.playspeed, lower=10, upper=200, step_increment=10, page_increment=50)
        self.speed = Gtk.SpinButton()
        # speed_label = Gtk.Label(label="Play Speed(%)")
        self.speed.set_adjustment(speed_adjustment)
        self.speed.connect("value-changed", self.on_speed_changed)

        hbox.pack_start(toolbar, False, False, 0)
        hbox.pack_start(forwardstep_label, False, False, 0)
        hbox.pack_start(self.forwardstep, False, False, 0)
        hbox.pack_start(self.switch_speed_button, False, False, 0)
        # hbox.pack_start(speedtoolbar, False, False, 0)
        # hbox.pack_start(speed_label, False, False, 0)
        hbox.pack_start(self.speed, False, False, 0)

        box.pack_start(hbox, False, False, 0)

        # label = Gtk.Label(label="Right-click to see the popup menu.")
        # eventbox.add(self.movie_window)
        # vbox.add(self.movie_window)

        # 以下定义播放器
        Gst.init(None)  
        # self.player = Gst.ElementFactory.make("playbin", "player")


        # # 定义变速后需要用到的audio调整的elements
        # self.aplayer = Gst.Pipeline.new("aplayer")
        # ascale = Gst.ElementFactory.make("scaletempo", "ascacle")
        # aconv = Gst.ElementFactory.make("audioconvert", "aconv")
        # aresample = Gst.ElementFactory.make("audioresample", "aresample")
        # asink = Gst.ElementFactory.make("autoaudiosink", "asink")

        # self.aplayer.add(ascale) 
        # self.aplayer.add(aconv) 
        # self.aplayer.add(aresample)
        # self.aplayer.add(asink)

        # ascale.link(aconv)
        # aconv.link(aresample)
        # aresample.link(asink)

        
        # pad = ascale.get_static_pad("sink")
        # ghostpad = Gst.GhostPad.new("sink", pad)
        # self.aplayer.add_pad(ghostpad)

        # self.player.set_property("audio-sink", self.aplayer)

        # 以下测试自建playerbin
        self.player = Gst.Pipeline.new("player")
        source = Gst.ElementFactory.make("filesrc", "file-source")

        demuxer = Gst.ElementFactory.make("decodebin", "demuxer")
        demuxer.connect("pad-added", self.demuxer_callback)

        self.queuev = Gst.ElementFactory.make("queue", "queuev")
 


        vconv = Gst.ElementFactory.make("videoconvert", "vconv")
        vrate = Gst.ElementFactory.make("videorate", "vrate")
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
        self.player.add(vrate)
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
        vconv.link(vrate)
        vrate.link(vsink)

        self.queuea.link(aconv1)
        aconv1.link(aresample1)
        aresample1.link(ascale)
        ascale.link(aconv2)
        aconv2.link(aresample2)
        aresample2.link(asink)






        bus = self.player.get_bus()
        bus.add_signal_watch()
        bus.enable_sync_message_emission()
        bus.connect("message", self.on_message)
        bus.connect("sync-message::element", self.on_sync_message)

        self.popup = uimanager.get_widget("/PopupMenu")

        self.add(box)
    
    def add_MediaMenu_actions(self, action_group):
        action_group.add_actions(
            [
                ("MediaMenu", None, "Media", "<alt>M", None, None),
                ("OpenFile", None, "Open File...", "<control>O", None, self.on_open_file),
                ("Quit", None, "Quit", "<control>Q", None, self.on_quit)
            ]
        )

    def add_PlaybackMenu_actions(self, action_group):
        action_group.add_actions(
            [
                ('PlaybackMenu', None, "Playback", "<alt>L", None, None),
                ('SpeedUp', Gtk.STOCK_GOTO_BOTTOM, "Speed Up", "<alt>U", None, None),
                ('SpeedDown', Gtk.STOCK_GO_DOWN, "Speed Down", "<alt>D", None, None),
                ('ResetSpeed', None, "Reset Speed", "<alt>R", None, None),
                ('JumpForward', Gtk.STOCK_MEDIA_FORWARD, "Jump Forward", "<alt>J", None, self.on_jump_forward),
                ('JumpBackward', Gtk.STOCK_MEDIA_REWIND, "Jump Backward", "<alt>K", None, self.on_jump_backword),
                ('JumpToSpecificTime', None, "Jump To Specific Time", "<control>T", None, None),
                ('Play', Gtk.STOCK_MEDIA_PLAY, "Play", "<alt>P", None, self.on_play_pause),
                ('Stop', Gtk.STOCK_MEDIA_STOP, "Stop", "<alt>S", None, self.on_stop)
            ]
        )

    def add_Audio_actions(self, action_group):
        action_group.add_actions(
            [
                ("AudioMenu", None, "Audio", "<alt>A", None, None),
                ("AudioTrackNext", None, "Audio Track", "<alt>T", None, None),
                ("IncreaseVolume", None, "Increase Volume", "<alt>I", None, None),
                ("DecreaseVolume", None, "Decrease Volume", "<alt>E", None, None),
                ("Mute", None, "Mute", "<alt>M", None, None)
            ]
        )

    def add_Video_actions(self, action_group):
        action_group.add_actions(
            [
                ("VideoMenu", None, "Video", "<alt>V", None, None)
            ]
        )


    def add_Subtitle_actions(self, action_group):
        action_group.add_actions(
            [
                ("SubtitleMenu", None, "Subtitle", "<alt>T", None, None),
                ("AddSubtitleFile", None, "Add Subtitle File...", "<alt>S", None, self.on_pick_sub_file),
                ("SubTrackNext", None, "Sub Track Next", "<alt>R", None, None)
            ]
        )
    def add_Tools_actions(self, action_group):
        action_group.add_actions(
            [
                ("ToolsMenu", None, "Tools", None, None, None)
            ]
        )
    def add_View_actions(self, action_group):
        action_group.add_actions(
            [
                ("ViewMenu", None, "View", None, None, None)
            ]
        )
    def add_Help_actions(self, action_group):
        action_group.add_actions(
            [
                ("HelpMenu", None, "Help", None, None, None)
            ]
        )

    def create_ui_manager(self):
        uimanager = Gtk.UIManager()

        # Throws exception if something went wrong
        uimanager.add_ui_from_string(UI_INFO)

        # Add the accelerator group to the toplevel window
        accelgroup = uimanager.get_accel_group()
        self.add_accel_group(accelgroup)
        return uimanager

    def on_open_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            file_name = dialog.get_filename()
            print("File selected: " + file_name)
            self.file_name = file_name
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()



    def add_filters(self, dialog):
        filter_text = Gtk.FileFilter()
        filter_text.set_name("Text files")
        filter_text.add_mime_type("text/plain")
        dialog.add_filter(filter_text)

        filter_py = Gtk.FileFilter()
        filter_py.set_name("Python files")
        filter_py.add_mime_type("text/x-python")
        dialog.add_filter(filter_py)

        filter_any = Gtk.FileFilter()
        filter_any.set_name("Any files")
        filter_any.add_pattern("*")
        dialog.add_filter(filter_any)
    
    def on_play_pause(self, widget):
        if self.play_toggle == "play":
            filepath = self.file_name.strip()
            if os.path.isfile(filepath):
                filepath = os.path.realpath(filepath)
                self.play_toggle = "pause"
                # self.player.set_property("uri", "file://" + filepath)
                self.player.get_by_name("file-source").set_property("location", filepath)

                self.player.set_state(Gst.State.PLAYING)
                widget.set_stock_id(Gtk.STOCK_MEDIA_PAUSE)
                # 打印一些媒体信息，用于调试

                self.player.set_property("flags", 0x00000613)
        elif self.play_toggle == "playing":
            self.player.set_state(Gst.State.PLAYING)
            self.play_toggle = "pause"
            widget.set_stock_id(Gtk.STOCK_MEDIA_PAUSE)
            print(str(self.player.get_property("n-text"))+"inner subtitles")
            print(self.player.get_property("current-suburi"))
            print(self.player.get_property("current-text"))
            print(self.player.get_property("text-sink"))
            print(self.player.get_property("audio-sink"))
            print(self.player.get_property("video-sink"))
        else:
            self.player.set_state(Gst.State.PAUSED)
            self.play_toggle = "playing"
            widget.set_stock_id(Gtk.STOCK_MEDIA_PLAY)
        # print(widget.get_name())

    def on_stop(self, widget):
        pass

    def on_quit(self, widget):
        Gtk.main_quit()

    def on_button_press_event(self, widget, event):
        pass
    
    def on_message(self, bus, message):
        t = message.type
        if t == Gst.MessageType.EOS:
            self.player.set_state(Gst.State.NULL)
            # self.button.set_label("Start")
        elif t == Gst.MessageType.ERROR:
            self.player.set_state(Gst.State.NULL)
            err, debug = message.parse_error()
            print( "Error: %s" % err, debug)
            # self.button.set_label("Start")

    def on_sync_message(self, bus, message):
        if message.get_structure().get_name() == 'prepare-window-handle':
            imagesink = message.src
            imagesink.set_property("force-aspect-ratio", True)
            imagesink.set_window_handle(self.movie_window.get_property('window').get_xid())

    def scale_moved(self, event):
        print("Horizontal scale is " + str(int(self.scale.get_value())))

    def on_jump_forward(self, widget):
        rc, pos_int = self.player.query_position(Gst.Format.TIME)
        seek_ns = pos_int + self.stepsize * 1000000000
        print('Forward: %d ns -> %d ns' % (pos_int, seek_ns))
        self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)


    def on_jump_backword(self, widget):
        rc, pos_int = self.player.query_position(Gst.Format.TIME)
        seek_ns = pos_int - self.stepsize * 1000000000
        if seek_ns < 0:
            seek_ns = 0
        print('Backward: %d ns -> %d ns' % (pos_int, seek_ns))
        self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)

    def on_forwardstep_changed(self, widget):
        stepsize = widget.get_value_as_int()
        print(stepsize)
        self.stepsize = stepsize

    def on_speed_changed(self, widget):
        playspeed = widget.get_value_as_int()
        print(playspeed)
        self.playspeed = playspeed

    def on_speed_toggled(self, widget, name):
        if widget.get_active():
            state = "on"
            self.player.set_state(Gst.State.PAUSED)


            self.player.seek(self.playspeed / 100, Gst.Format.TIME, Gst.SeekFlags.FLUSH, Gst.SeekType.NONE, 0,Gst.SeekType.NONE, 0)
            self.player.set_state(Gst.State.PLAYING)

        else:
            state = "off"
            # self.player.set_property("audio-sink", Null)

            # self.player.seek(1.0, Gst.Format.TIME, Gst.SeekFlags.SKIP, Gst.SeekType.NONE, 0,Gst.SeekType.NONE, 0)
            # self.player.set_state(Gst.State.PAUSED)

            rc, pos_int = self.player.query_position(Gst.Format.TIME)
            seek_ns = pos_int

            self.player.seek_simple(Gst.Format.TIME, Gst.SeekFlags.FLUSH, seek_ns)
            
            # self.player.set_state(Gst.State.PLAYING)

        print("Button", name, "was turned", state)

    def on_pick_sub_file(self, widget):
        dialog = Gtk.FileChooserDialog(
            title="Please choose a file", parent=self, action=Gtk.FileChooserAction.OPEN
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL,
            Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN,
            Gtk.ResponseType.OK,
        )

        self.add_filters(dialog)

        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            print("Open clicked")
            file_name = dialog.get_filename()
            print("File selected: " + file_name)
            self.sub_uri = file_name
        elif response == Gtk.ResponseType.CANCEL:
            print("Cancel clicked")

        dialog.destroy()
        print(self.sub_uri)
        self.player.set_property("suburi", self.sub_uri)

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

Gdk.threads_init()
window = myVLCWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
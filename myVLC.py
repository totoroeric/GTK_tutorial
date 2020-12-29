import gi
import sys, os
gi.require_version('Gst', '1.0')
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GObject

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
    <toolitem action='Mute' />
  </toolbar>
  <popup name='PopupMenu'>
    <menuitem action='EditCopy' />
    <menuitem action='EditPaste' />
    <menuitem action='EditSomething' />
  </popup>
</ui>
"""

class myVLCWindow(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="My VLC")

        self.set_default_size(600, 400)
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
        eventbox = Gtk.EventBox()
        eventbox.connect("button-press-event", self.on_button_press_event)

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.pack_start(menubar, False, False, 0)
        box.pack_start(eventbox, True, True, 0)  #这里需要插入视频窗口,这里用一个eventbox替代先
        #这里插入进度条
        box.pack_start(toolbar, False, False, 0)

        # label = Gtk.Label(label="Right-click to see the popup menu.")
        self.movie_window = Gtk.DrawingArea() # 视频窗口
        eventbox.add(self.movie_window)

        # 以下定义播放器
        self.player = Gst.ElementFactory.make("playbin", "play")
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
                ('SpeedUp', None, "Speed Up", "<alt>U", None, None),
                ('SpeedDown', None, "Speed Down", "<alt>D", None, None),
                ('ResetSpeed', None, "Reset Speed", "<alt>R", None, None),
                ('JumpForward', None, "Jump Forward", "<alt>J", None, None),
                ('JumpBackward', None, "Jump Backward", "<alt>K", None, None),
                ('JumpToSpecificTime', None, "Jump To Specific Time", "<control>T", None, None),
                ('Play', None, "Play", "<alt>P", None, None),
                ('Stop', None, "Stop", "<alt>S", None, None)
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
                ("AddSubtitleFile", None, "Add Subtitle File...", "<alt>S", None, None),
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
        pass

    def on_quit(self, widget):
        Gtk.main_quit()

    def on_button_press_event(self, widget, event):
        pass

window = myVLCWindow()
window.connect("destroy", Gtk.main_quit)
window.show_all()
Gtk.main()
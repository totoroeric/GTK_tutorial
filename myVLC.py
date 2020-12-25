import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk

UI_INFO = """
<ui>
  <menubar name='MenuBar'>
    <menu action='MediaMenu'>
      <separator />
      <menuitem action='OpenFile' />
      <menuitem action='OpenMultipleFile' />
      <menuitem action='OpenDirectory' />
      <menuitem action='OpenDisc' />
      <menuitem action='OpenNetworkStream' />
      <menuitem action='OpenCaptureDevice' />
      <menuitem action='OpenLocationFromClipboard' />
      <menu action='OpenRecentMedia'>
        <menuitem action='FileNewStandard' />
        <menuitem action='FileNewFoo' />
        <menuitem action='FileNewGoo' />
      </menu>
      <separator />
      <menuitem action='SavePlaylistToFile' />
      <menuitem action='ConvertOrSave' />
      <menuitem action='Stream' />
      <separator />
      <menuitem action='QuitAtTheEndOfPlaylist' />
      <menuitem action='Quit' />
    </menu>
    <menu action='PlaybackMenu'>
      <menu action='Title'>
      </menu>
      <menu action='Chapter'>
      </menu>
      <menu action='Program'>
      </menu>
      <menu action='CustomBookmarks'>
      </menu>
      <separator />
      <menu action='Renderer'>
        <menuitem action='Local' />
        <separator />
        <menuitem action='Scanning' />
      </menu>
      <separator />
      <menu action='Speed'>
      </menu>
      <separator />
      <menuitem action='JumpForward' />
      <menuitem action='JumpBackward' />
      <menuitem action='JumpToSpecificTime' />
      <separator />
      <menuitem action='Play' />
      <menuitem action='Stop' />
      <menuitem action='Previous' />
      <menuitem action='Next' />
      <menuitem action='Record' />
    </menu>
    <menu action='Audio'>
      <menu action='AudioTrack'>
      </menu>
      <menu action='AudioDevice'>
      </menu>
      <menu action='StereoMode'>
      </menu>
      <separator />
      <menu action='Visualizations'>
      </menu>
      <separator />
      <menuitem action='IncreaseVolume'/>
      <menuitem action='DecreaseVolume'/>
      <menuitem action='Mute'/>
    </menu>
    <menu action='Video'>
    </menu>
    <menu action='Subtitle'>
      <menuitem action='AddSubtitleFile'/>
      <menu action='SubTrack'>
      </menu>
    </menu>
    <menu action='Tools'>
    </menu>
    <menu action='View'>
    </menu>
    <menu action='Help'>
    </menu>
  </menubar>
  <toolbar name='ToolBar'>
    <toolitem action='PlayButton' />
    <toolitem action='PreviousMediaButton' />
    <toolitem action='StopButton' />
    <toolitem action='NextMediaButton' />
    <toolitem action='FullScreenToggle' />
    <toolitem action='ExtendedSettingsToggle' />
    <toolitem action='PlaylistToggle' />
    <toolitem action='LoopModeToggle' />
    <toolitem action='RandomToggle' />
    <toolitem action='MuteButton' />
    <toolitem action='VolumeController' />
  </toolbar>
</ui>
"""
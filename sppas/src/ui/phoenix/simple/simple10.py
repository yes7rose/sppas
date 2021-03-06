import wx
import logging
import os.path
from argparse import ArgumentParser

try:
    import wx.adv
    adv_import = True
except ImportError:
    adv_import = False


"""

Use global settings to fix the Look&Feel,
so no longer global variables fixed in hard in the code!

"""


def setup_logging(log_level=15, filename=None):
    """ Setup default logger to log to stderr or and possible also to a file.

    :param log_level: Sets the threshold for this logger. Logging messages
    which are less severe than this value will be ignored. When NOTSET is
    assigned, all messages are printed.
    :param filename: Specifies that a FileHandler be created, using the
    specified filename, rather than a StreamHandler.

    The numeric values of logging levels are given in the following:

        - CRITICAL 	50
        - ERROR 	40
        - WARNING 	30
        - INFO 	    20
        - DEBUG 	10
        - NOTSET 	 0

    """
    formatmsg = "%(asctime)s [%(levelname)s] %(message)s"
    if log_level is None:
        log_level = 15

    # Setup logging to file if filename is specified
    if filename is not None:
        file_handler = logging.FileHandler(filename, "a+")
        file_handler.setFormatter(logging.Formatter(formatmsg))
        file_handler.setLevel(log_level)
        logging.getLogger().addHandler(file_handler)
        logging.getLogger().setLevel(log_level)
        logging.info("Logging set up level={:d}, filename={:s}".format(log_level, filename))

    else:
        # Setup logging to stderr
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(formatmsg))
        console_handler.setLevel(log_level)
        logging.getLogger().addHandler(console_handler)
        logging.getLogger().setLevel(log_level)
        logging.info("Logging set up level={:d}".format(log_level))

# ---------------------------------------------------------------------------


class myTitleText(wx.StaticText):
    """ A class to write a title. """

    def __init__(self, parent, title_text):

        wx.StaticText.__init__(self, parent, label=title_text, style=wx.ALIGN_CENTER)

        # Fix Look&Feel
        cfg = wx.GetApp().cfg

        if 'TITLE_TEXT_FONT' in cfg:
            self.SetFont(cfg['TITLE_TEXT_FONT'])
        if 'TITLE_BG_COLOUR' in cfg:
            self.SetBackgroundColour(parent.GetBackgroundColour())
        if 'TITLE_FG_COLOUR' in cfg:
            self.SetForegroundColour(cfg['TITLE_FG_COLOUR'])

# ---------------------------------------------------------------------------


class myButton(wx.Button):
    """ Create my own button. Inherited from the wx.Button.

    """
    def __init__(self, parent, label, name):

        wx.Button.__init__(self,
                           parent,
                           wx.ID_ANY,
                           label,
                           style=wx.NO_BORDER,
                           name=name)
        # Fix Look&Feel
        cfg = wx.GetApp().cfg

        if 'BUTTON_FG_COLOUR' in cfg:
            self.SetForegroundColour(cfg['BUTTON_FG_COLOUR'])
        if 'BUTTON_BG_COLOUR' in cfg:
            self.SetBackgroundColour(cfg['BUTTON_FG_COLOUR'])
        if 'BUTTON_TEXT_FONT' in cfg:
            self.SetFont(cfg['BUTTON_TEXT_FONT'])

# ---------------------------------------------------------------------------


class myFrame(wx.Frame):
    """ Create my own frame. Inherited from the wx.Frame.

    """
    def __init__(self):

        cfg = wx.GetApp().cfg
        FRAME_STYLE = wx.DEFAULT_FRAME_STYLE
        if FRAME_STYLE in cfg:
            FRAME_STYLE = cfg['FRAME_STYLE']

        title = wx.GetApp().GetAppDisplayName()
        wx.Frame.__init__(self,
                          None,
                          title=title,
                          style=FRAME_STYLE)
        self.SetMinSize((300, 200))
        if 'FRAME_WIDTH' in cfg or 'FRAME_HEIGHT' in cfg:
            w = -1
            h = -1
            if 'FRAME_WIDTH' in cfg:
                w = cfg['FRAME_WIDTH']
            if 'FRAME_HEIGHT' in cfg:
                h = cfg['FRAME_HEIGHT']
            self.SetSize(wx.Size(w, h))

        # Store all panels in a dictionary with key=name, value=object
        self.panels = dict()

        # create a sizer to add and organize objects
        topSizer = wx.BoxSizer(wx.VERTICAL)

        # add a customized menu (instead of a traditional menu+toolbar)
        menus = myMenuPanel(self)
        topSizer.Add(menus, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # separate menu and the rest with a line
        line_top = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        topSizer.Add(line_top, 0, wx.ALL | wx.EXPAND, 0)

        # add a 1st panel for files
        self.panels["files"] = myFilePanel(self)
        topSizer.Add(self.panels["files"], 3, wx.ALL | wx.EXPAND, 0)

        # add a 2nd panel for annotations
        self.panels["annotate"] = myAnnotatePanel(self)
        topSizer.Add(self.panels["annotate"], 3, wx.ALL | wx.EXPAND, 0)

        # add a 3rd panel for analysis
        self.panels["analyze"] = myAnalyzePanel(self)
        topSizer.Add(self.panels["analyze"], 3, wx.ALL | wx.EXPAND, 0)

        # separate the rest and the action buttons with a line
        line_bottom = wx.StaticLine(self, style=wx.LI_HORIZONTAL)
        topSizer.Add(line_bottom, 0, wx.ALL | wx.EXPAND, 0)

        # add some action buttons
        actions = myActionPanel(self)
        topSizer.Add(actions, 0, wx.ALIGN_LEFT | wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Associate a handler function with the EVT_BUTTON event.
        # That means that when a button is clicked then the process
        # handler function will be called.
        self.Bind(wx.EVT_BUTTON, self.process_event)

        # Since Layout doesn't happen until there is a size event, you will
        # sometimes have to force the issue by calling Layout yourself. For
        # example, if a frame is given its size when it is created, and then
        # you add child windows to it, and then a sizer, and finally Show it,
        # then it may not receive another size event (depending on platform)
        # in order to do the initial layout. Simply calling self.Layout from
        # the end of the frame's __init__ method will usually resolve this.
        self.SetAutoLayout(True)
        self.SetSizer(topSizer)
        self.Layout()

    # -----------------------------------------------------------------------
    # Callbacks
    # -----------------------------------------------------------------------

    def process_event(self, event):
        """ Process any kind of events. """

        event_name = event.GetEventObject().GetName()
        event_id = event.GetEventObject().GetId()
        logging.debug("Received event id {:d} of {:s}".format(event_id, event_name))

        if event_name == "exit":
            self.exit()
        elif event_name == "save":
            pass
        elif event_name == "open":
            pass
        elif event_name in ["files", "annotate", "analyze"]:
            self.switch_to_panel(event_name)
        else:
            event.Skip()

    # -----------------------------------------------------------------------

    def exit(self):
        """ Close the frame, terminating the application. """

        self.Close(True)

    # -----------------------------------------------------------------------

    def switch_to_panel(self, panel_name):
        """ Switch to the expected panel. Hide the current. """

        if panel_name not in self.panels:
            logging.warning("Unknown panel name '{:s}' to switch on.".format(panel_name))
            return

        logging.debug("Switch to panel '{:s}'.".format(panel_name))
        if self.panels[panel_name].IsShown() is False:
            # hide the current
            for p in self.panels:
                if self.panels[p].IsShown() is True:
                    self.panels[p].HideWithEffect(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM, timeout=400)
            # show the expected
            self.panels[panel_name].ShowWithEffect(wx.SHOW_EFFECT_SLIDE_TO_BOTTOM, timeout=400)

        self.Layout()
        self.Refresh()

# ---------------------------------------------------------------------------


class myMenuPanel(wx.Panel):
    """ Create my own menu panel with several action buttons.
    It aims to replace the old-style menus.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)

        # Fix Look&Feel
        cfg = wx.GetApp().cfg
        if 'TITLE_BG_COLOUR' in cfg:
            self.SetBackgroundColour(cfg['TITLE_BG_COLOUR'])
        if 'TITLE_HEIGHT' in cfg:
            logging.debug('Menu height: {:d}'.format(cfg['TITLE_HEIGHT']))
            self.SetMinSize((-1, cfg['TITLE_HEIGHT']))

        menuSizer = wx.BoxSizer(wx.HORIZONTAL)
        st = myTitleText(self, "My App!")
        menuSizer.Add(st, 0, wx.ALIGN_CENTER_VERTICAL, 0)

        menuSizer.AddStretchSpacer(prop=1)

        # Will switch to the "Files" main panel
        fileBtn = myButton(self, "Files", name="files")
        menuSizer.Add(fileBtn, 1, wx.EXPAND, 0)

        # Will switch to the "Annotate" main panel
        annotBtn = myButton(self, "Annotate", name="annotate")
        menuSizer.Add(annotBtn, 1, wx.EXPAND, 0)

        # Will switch to the "Analyze" main panel
        analyseBtn = myButton(self, "Analyze", name="analyze")
        menuSizer.Add(analyseBtn, 1, wx.EXPAND, 0)

        menuSizer.AddStretchSpacer(prop=5)

        # Will open an about message dialog
        aboutBtn = myButton(self, "About", name="about")
        menuSizer.Add(aboutBtn, 0, wx.ALIGN_RIGHT | wx.EXPAND, 0)

        # Bind all buttons of this menu
        self.Bind(wx.EVT_BUTTON, self.OnAction, fileBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, annotBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, analyseBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAbout, aboutBtn)

        self.SetSizer(menuSizer)
        self.SetAutoLayout(True)

    # -----------------------------------------------------------------------

    def OnAction(self, event):
        """ A button was clicked.
        Here we just send the event to the parent.

        """
        logging.debug("A button in the menu was clicked on.")
        wx.PostEvent(self.GetTopLevelParent(), event)

    # -----------------------------------------------------------------------

    def OnAbout(self, event):
        """ Display an About Dialog. """

        # Default dialog which will have the default style... so, it won't
        # have our own colors...
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World",
                      wx.OK | wx.ICON_INFORMATION)

# ---------------------------------------------------------------------------


class myActionPanel(wx.Panel):
    """ Create my own panel with 3 action buttons: exit, open, save.

    """
    def __init__(self, parent):

        wx.Panel.__init__(self, parent)
        self.SetMinSize((-1, 32))

        cfg = wx.GetApp().cfg
        if 'TITLE_BG_COLOUR' in cfg:
            self.SetBackgroundColour('TITLE_BG_COLOUR')

        exitBtn = myButton(self, "Exit", name="exit")
        openBtn = myButton(self, "Open", name="open")
        saveBtn = myButton(self, "Save", name="save")

        actionSizer = wx.BoxSizer(wx.HORIZONTAL)
        actionSizer.Add(exitBtn, 1, wx.ALL | wx.EXPAND, 0)
        actionSizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        actionSizer.Add(openBtn, 1, wx.ALL | wx.EXPAND, 0)
        actionSizer.Add(wx.StaticLine(self, style=wx.LI_VERTICAL), 0, wx.ALL | wx.EXPAND, 0)
        actionSizer.Add(saveBtn, 1, wx.ALL | wx.EXPAND, 0)
        self.SetSizer(actionSizer)

        self.Bind(wx.EVT_BUTTON, self.OnAction, exitBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, openBtn)
        self.Bind(wx.EVT_BUTTON, self.OnAction, saveBtn)

    # -----------------------------------------------------------------------

    def OnAction(self, event):
        """ A button was clicked.
        Here we just send the event to the parent.

        """
        logging.debug("A button in the action panel was clicked on.")
        wx.PostEvent(self.GetTopLevelParent(), event)

# ---------------------------------------------------------------------------


class myContentPanel(wx.Panel):
    """ Create my own panel for the content of the frame.

    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)

        cfg = wx.GetApp().cfg
        if 'BG_COLOUR' in cfg:
            self.SetBackgroundColour(cfg['BG_COLOUR'])

# ---------------------------------------------------------------------------


class myFilePanel(myContentPanel):
    """ Create my own panel to work with files.

    """
    def __init__(self, parent):
        myContentPanel.__init__(self, parent)

        cfg = wx.GetApp().cfg

        st = wx.StaticText(self, wx.ID_ANY, label="Files panel", pos=(25, 25))
        if 'FG_COLOUR' in cfg:
            st.SetForegroundColour(cfg['FG_COLOUR'])
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(True)

# ---------------------------------------------------------------------------


class myAnnotatePanel(myContentPanel):
    """ Create my own panel to annotate files.

    """
    def __init__(self, parent):

        myContentPanel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(10, 10, 5))
        cfg = wx.GetApp().cfg

        st = wx.StaticText(self, wx.ID_ANY, label="Annotate panel", pos=(25, 25))
        if 'FG_COLOUR' in cfg:
            st.SetForegroundColour(cfg['FG_COLOUR'])
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(False)

# ---------------------------------------------------------------------------


class myAnalyzePanel(myContentPanel):
    """ Create my own panel to analyze files.

    """
    def __init__(self, parent):

        myContentPanel.__init__(self, parent)
        self.SetBackgroundColour(wx.Colour(80, 80, 75))
        cfg = wx.GetApp().cfg

        st = wx.StaticText(self, wx.ID_ANY, label="Analyze panel", pos=(25, 25))
        if 'FG_COLOUR' in cfg:
            st.SetForegroundColour(cfg['FG_COLOUR'])
        font = st.GetFont()
        font.PointSize += 10
        font = font.Bold()
        st.SetFont(font)
        self.Show(False)

# ---------------------------------------------------------------------------


class myApp(wx.App):
    """ Create my own wx application. """


    def __init__(self):

        # Create members
        self.app_dir = os.path.dirname(os.path.realpath(__file__))
        self.splash = None
        self.cfg = dict()
        self.log_file = None  # os.path.join(os.path.dirname(os.path.abspath(__file__)), "simple.log")
        self.log_level = 10
        self.init_members()

        # Initialize the wx application
        wx.App.__init__(self,
                        redirect=False,
                        filename=self.log_file,
                        useBestVisual=True,
                        clearSigInt=True)

        self.SetAppName("simple10")
        self.SetAppDisplayName("Displayed application name")

        wx.Log.EnableLogging(True)
        wx.Log.SetLogLevel(20)
        
        lang = wx.LANGUAGE_DEFAULT
        self.locale = wx.Locale(lang)

    # -----------------------------------------------------------------------

    def init_members(self):

        self.process_command_line_args()

        self.cfg['splash_delay'] = 10

        # Fix the level of messages and where to redirect them (file or std)
        try:
            setup_logging(self.log_level, self.log_file)
        except:
            setup_logging(self.log_level, None)


    # -----------------------------------------------------------------------

    def run(self):
        
        # here we could fix things like:
        #  - is first launch? No? so create config! and/or display a welcome msg!
        #  - fix config dir,
        #  - etc

        if adv_import and self.cfg['splash_delay'] > 0:
            self.show_splash_screen(self.cfg['splash_delay'])
        self.background_initialization()
        self.create_application()   
        self.MainLoop()

    # -----------------------------------------------------------------------

    def process_command_line_args(self):
        """ This is an opportunity for users to fix some args. """

        parser = ArgumentParser(usage="%s" % os.path.basename(__file__), 
                        description="... a program to do something.")
        # add arguments here
        # then parse
        args = parser.parse_args()

        # and do things with arguments

    # -----------------------------------------------------------------------

    def background_initialization(self):

        # Initialize the application
        #   here we could read some config file, load some resources, etc
        #   while we show the Splash window
        # for this example, we simply create a dictionary with the config
        # (and sleep some time to simulate we're doing something).
        a = 1.5
        for i in range(1000000):
            a *= float(i)

        title_font = wx.SystemSettings().GetFont(wx.SYS_DEFAULT_GUI_FONT)
        title_font = title_font.Bold()
        title_font = title_font.Scale(2.)

        button_font = wx.Font(12,  # point size
                              wx.FONTFAMILY_DEFAULT,  # family,
                              wx.FONTSTYLE_NORMAL,    # style,
                              wx.FONTWEIGHT_NORMAL,   # weight,
                              underline=False,
                              faceName="Calibri",
                              encoding=wx.FONTENCODING_SYSTEM)

        self.cfg['FRAME_STYLE'] = wx.DEFAULT_FRAME_STYLE | wx.CLOSE_BOX

        # Fix the size of the objects
        self.cfg['FRAME_WIDTH'] = 640
        self.cfg['FRAME_HEIGHT'] = 480
        self.cfg['TITLE_HEIGHT'] = 64

        # Fix the COLORS
        self.cfg['TITLE_BG_COLOUR'] = wx.Colour(65, 65, 60, alpha=wx.ALPHA_OPAQUE)
        self.cfg['TITLE_FG_COLOUR'] = wx.Colour(250, 250, 250, alpha=wx.ALPHA_OPAQUE)

        self.cfg['FG_COLOUR'] = wx.Colour(250, 250, 240, alpha=wx.ALPHA_OPAQUE)
        self.cfg['BG_COLOUR'] = wx.Colour(45, 45, 40, alpha=wx.ALPHA_OPAQUE)

        # Fix the font
        self.cfg['TITLE_TEXT_FONT'] = title_font
        self.cfg['BUTTON_TEXT_FONT'] = button_font
    
    # -----------------------------------------------------------------------

    def create_application(self):
        """ Create the main frame of the application and show it. """

        frm = myFrame()
        self.SetTopWindow(frm)
        if self.splash:
            self.splash.Close()
        frm.Show()

    # -----------------------------------------------------------------------

    def show_splash_screen(self, delay=10):
        """ Create and show the splash image during 10 seconds. """
        
        bitmap = wx.Bitmap('splash.png', wx.BITMAP_TYPE_PNG)

        self.splash = wx.adv.SplashScreen(bitmap,
                                          wx.adv.SPLASH_CENTRE_ON_SCREEN | wx.adv.SPLASH_TIMEOUT,
                                          delay*100,
                                          None,
                                          -1,
                                          wx.DefaultPosition,
                                          wx.DefaultSize,
                                          wx.BORDER_SIMPLE | wx.STAY_ON_TOP)
        self.Yield()

    # -----------------------------------------------------------------------

    def OnExit(self):
        """ Optional. Override the already existing method to kill the app.
        This method is invoked when the user:

            - clicks on the X button of the frame manager
            - does "ALT-F4" (Windows) or CTRL+X (Unix)

        """
        # do whatever you want here (save session, ...)
        logging.debug("OnExit method invoked.")

        # then it will exit. Nothing special to do. Return the exit status.
        return 0

# ---------------------------------------------------------------------------


if __name__ == '__main__':

    # Create and run the application
    app = myApp()
    app.run()

    # do some job after (the application is stopped)
    logging.info("Bye bye")

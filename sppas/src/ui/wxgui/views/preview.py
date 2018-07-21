#!/usr/bin/env python2
# -*- coding: UTF-8 -*-
# ---------------------------------------------------------------------------
#            ___   __    __    __    ___
#           /     |  \  |  \  |  \  /              Automatic
#           \__   |__/  |__/  |___| \__             Annotation
#              \  |     |     |   |    \             of
#           ___/  |     |     |   | ___/              Speech
#
#
#                           http://www.sppas.org/
#
# ---------------------------------------------------------------------------
#            Laboratoire Parole et Langage, Aix-en-Provence, France
#                   Copyright (C) 2011-2016  Brigitte Bigi
#
#                   This banner notice must not be removed
# ---------------------------------------------------------------------------
# Use of this software is governed by the GNU Public License, version 3.
#
# SPPAS is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SPPAS is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with SPPAS. If not, see <http://www.gnu.org/licenses/>.
#
# ---------------------------------------------------------------------------
# File: preview.py
# ---------------------------------------------------------------------------

__docformat__ = """epytext"""
__authors__   = """Brigitte Bigi"""
__copyright__ = """Copyright (C) 2011-2016  Brigitte Bigi"""

# ----------------------------------------------------------------------------
# Imports
# ----------------------------------------------------------------------------

# General libraries import
import wx
import wx.richtext

from sppas.src.ui.wxgui.dialogs.basedialog import spBaseDialog
from sppas.src.ui.wxgui.sp_icons import TIER_PREVIEW

from sppas.src.ui.wxgui.ui.CustomListCtrl import LineListCtrl

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

DARK_GRAY  = wx.Colour(35,35,35)
LIGHT_GRAY = wx.Colour(235,235,235)
LIGHT_BLUE = wx.Colour(230,230,250)
LIGHT_RED  = wx.Colour(250,230,230)

SILENCE_FG_COLOUR = wx.Colour(45,45,190)
SILENCE_BG_COLOUR = wx.Colour(230,230,250)
LAUGH_FG_COLOUR   = wx.Colour(190,45,45)
LAUGH_BG_COLOUR   = wx.Colour(250,230,230)
NOISE_FG_COLOUR   = wx.Colour(45,190,45)
NOISE_BG_COLOUR   = wx.Colour(230,250,230)

# ----------------------------------------------------------------------------
# class PreviewTierDialog
# ----------------------------------------------------------------------------

class PreviewTierDialog( spBaseDialog ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Frame allowing to show details of a tier.

    """

    def __init__(self, parent, preferences, tiers=[]):
        """
        Constructor.

        @param parent is a wx.Window or wx.Frame or wx.Dialog
        @param preferences (Preferences or Preferences_IO)
        @param tiers is a list of tiers to display

        """
        spBaseDialog.__init__(self, parent, preferences, title=" - Preview")
        wx.GetApp().SetAppName( "log" )

        self.tiers = tiers

        titlebox   = self.CreateTitle(TIER_PREVIEW,"Preview of tier(s)")
        contentbox = self._create_content()
        buttonbox  = self._create_buttons()

        self.LayoutComponents( titlebox,
                               contentbox,
                               buttonbox )

    # ------------------------------------------------------------------------
    # Create the GUI
    # ------------------------------------------------------------------------

    def _create_buttons(self):
        btn_close = self.CreateCloseButton()
        return self.CreateButtonBox( [],[btn_close] )

    def _create_content(self):
        self.notebook = wx.Notebook(self)

        page1 = TierAsListPanel(self.notebook, self.preferences)
        page2 = TierDetailsPanel(self.notebook, self.preferences)
        page3 = TierGraphicPanel(self.notebook, self.preferences)

        # add the pages to the notebook with the label to show on the tab
        self.notebook.AddPage(page1, "List view"     )
        self.notebook.AddPage(page2, "Detailed view" )
        self.notebook.AddPage(page3, "Graphic view"  )

        # TODO: view all tiers
        if len(self.tiers) > 0:
            page1.ShowTier( self.tiers[0] )
        self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.OnNotebookPageChanged)
        return self.notebook

    # ------------------------------------------------------------------------
    # Callbacks to events
    # ------------------------------------------------------------------------

    def OnNotebookPageChanged(self, event):
        oldselection = event.GetOldSelection()
        newselection = event.GetSelection()
        if oldselection != newselection:
            page = self.notebook.GetPage( newselection )
            # LIMITATION / TODO: view all tiers
            if len(self.tiers)>0:
                page.ShowTier( self.tiers[0] )

# ----------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# Base Tier Panel
# ----------------------------------------------------------------------------

class BaseTierPanel( wx.Panel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Base tier panel.

    """

    def __init__(self, parent, prefsIO):

        wx.Panel.__init__(self, parent)
        self.preferences = prefsIO

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.SetSizer(self.sizer)
        self.ShowNothing()
        self.sizer.Fit(self)

    # ------------------------------------------------------------------------

    def ShowNothing(self):
        """
        Method to show a message in the panel.

        """
        self.sizer.DeleteWindows()
        st = wx.StaticText(self, -1, "Nothing to view!")
        st.SetMinSize((320,200))
        self.sizer.Add(st, 1, flag=wx.ALL|wx.EXPAND, border=5)

    # ------------------------------------------------------------------------

    def ShowTier(self, tier):
        """
        Base method to show a tier in the panel.

        """
        self.ShowNothing()

    # ------------------------------------------------------------------------


# ----------------------------------------------------------------------------
# First tab: simple list view
# ----------------------------------------------------------------------------

class TierAsListPanel( BaseTierPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: List-view of a tier.

    """

    def __init__(self, parent, prefsIO):
        BaseTierPanel.__init__(self, parent, prefsIO)

    # ------------------------------------------------------------------------

    def ShowTier(self, tier):
        """
        Show a tier as list.

        """
        if not tier:
            self.ShowNothing()
            return

        tierctrl = LineListCtrl(self, style=wx.LC_REPORT)#|wx.LC_HRULES|wx.LC_VRULES)
        tierctrl.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        tierctrl.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        #tierctrl.SetMinSize((600, 380))

        # create columns
        isPointTier = tier.IsPoint()
        if not isPointTier:
            cols = ("Begin", "End", "Label")
        else:
            cols = ("Time", "Label")
        for i, col in enumerate(cols):
            tierctrl.InsertColumn(i, col)
            tierctrl.SetColumnWidth(i, 100)
        tierctrl.SetColumnWidth(len(cols)-1, 400)

        # fill rows
        for i, a in enumerate(tier):

            # fix location
            if not isPointTier:
                tierctrl.InsertStringItem(i, str(a.GetLocation().GetBeginMidpoint()))
                tierctrl.SetStringItem(i, 1, str(a.GetLocation().GetEndMidpoint()))
                labeli = 2
            else:
                tierctrl.InsertStringItem(i, str(a.GetLocation().GetPointMidpoint()))
                labeli = 1

            # fix label
            label = a.GetLabel()
            tierctrl.SetStringItem(i, labeli, label.GetValue())

            # customize label look
            if label.IsSilence():
                tierctrl.SetItemTextColour( i, SILENCE_FG_COLOUR )
                tierctrl.SetItemBackgroundColour( i, SILENCE_BG_COLOUR )
            if label.IsPause():
                tierctrl.SetItemTextColour( i, SILENCE_FG_COLOUR )
            if label.IsLaugh():
                tierctrl.SetItemTextColour( i, LAUGH_FG_COLOUR )
                tierctrl.SetItemBackgroundColour( i, LAUGH_BG_COLOUR )
            if label.IsNoise():
                tierctrl.SetItemTextColour( i, NOISE_FG_COLOUR )
                tierctrl.SetItemBackgroundColour( i, NOISE_BG_COLOUR )

        self.sizer.DeleteWindows()
        self.sizer.Add(tierctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.Fit(self)

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Second tab: Details of each annotation
# ----------------------------------------------------------------------------

class TierDetailsPanel( BaseTierPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Detailed-view of a tiers.

    """

    def __init__(self, parent, prefsIO):
        BaseTierPanel.__init__(self, parent, prefsIO)

    # ------------------------------------------------------------------------

    def ShowTier(self, tier):
        """
        Show a tier in a rich text control object, with detailed information.

        """
        self.text_ctrl = wx.richtext.RichTextCtrl(self, style=wx.VSCROLL|wx.HSCROLL|wx.NO_BORDER)
        self.text_ctrl.SetForegroundColour( self.preferences.GetValue('M_FG_COLOUR') )
        self.text_ctrl.SetBackgroundColour( self.preferences.GetValue('M_BG_COLOUR') )
        self.text_ctrl.SetMinSize((600, 380))
        self.text_ctrl.SetEditable(False)
        self._set_styles()
        self._create_text_content(tier)

        self.sizer.DeleteWindows()
        self.sizer.Add(self.text_ctrl, 1, flag=wx.ALL|wx.EXPAND, border=5)
        self.sizer.Fit(self)

    # ------------------------------------------------------------------------

    def _set_styles(self):
        """
        Fix a set of styles to be used in the RichTextCtrl.

        """
        fs = self.preferences.GetValue('M_FONT').GetPointSize()

        # SetFont( pointSize, family, style, weight, underline, face, encoding )
        self.labelStyle = wx.richtext.RichTextAttr()
        self.labelStyle.SetBackgroundColour( LIGHT_RED )
        self.labelStyle.SetTextColour( wx.BLACK )
        self.labelStyle.SetFont(wx.Font(fs, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New'))

        self.nlineStyle = wx.richtext.RichTextAttr()
        self.nlineStyle.SetBackgroundColour( LIGHT_GRAY )
        self.nlineStyle.SetTextColour( DARK_GRAY )
        self.nlineStyle.SetFont(wx.Font(fs+1, wx.ROMAN, wx.NORMAL, wx.BOLD, False, u'Courier New'))

        self.timeStyle = wx.richtext.RichTextAttr()
        self.timeStyle.SetBackgroundColour( LIGHT_BLUE )
        self.timeStyle.SetTextColour( wx.BLACK )
        self.timeStyle.SetFont(wx.Font(fs, wx.SWISS, wx.NORMAL, wx.NORMAL, False, u'Courier New'))

    def _create_text_content(self, tier):
        """
        Add the content of the tier in the RichTextCtrl.
        """

        if not tier:
            self.text_ctrl.WriteText( "Nothing to view!" )
            return

        isPointTier = tier.IsPoint()

        # creating a richtextctrl can work for a while...
        dialog = wx.ProgressDialog("Detailed view progress", "Please wait while creating the detailed view...", tier.GetSize(),
        style=wx.PD_ELAPSED_TIME | wx.PD_REMAINING_TIME)

        for i,ann in enumerate(tier):

            # Update progress
            if (i%20):
                dialog.Update(i)

            # Write line number
            idx = "{:6d}".format( i )
            if isPointTier is False:
                self._append_text("Interval "+idx+" ", self.nlineStyle)
            else:
                self._append_text("Point "+idx+" ", self.nlineStyle)
            self.text_ctrl.Newline()

            # Location:
            strloc = "\t- Location:\n"
            location = ann.GetLocation()
            for place in location.GetLocalizations():
                if isPointTier is False:
                    sm = "{:6.2f}".format( place.GetBegin().GetMidpoint() )
                    sr = str(place.GetBegin().GetRadius())
                    em = "{:6.2f}".format( ann.GetLocation().GetEndMidpoint() )
                    er = str(place.GetEnd().GetRadius())
                    sc = str(place.GetScore())

                    strloc = strloc+"\t\t* score="+sc+":\n"
                    strloc = strloc+"\t\t\tfrom:\t"+sm+" (radius="+sr+")\n"
                    strloc = strloc+"\t\t\tto:\t\t"+em+" (radius="+er+")\n"

                else:
                    sm = "{:6.2f}".format( ann.GetLocation().GetPointMidpoint() )
                    sr = str(place.GetPoint().GetRadius())
                    sc = str(place.GetScore())
                    strloc = strloc+"\t\t* score="+sc+": "+sm+" (radius="+sr+")\n"

            self._append_text(strloc, self.timeStyle)

            # Label
            strlabel = "\t- Label:\n"
            label = ann.GetLabel()
            for text in label.GetLabels():
                lv = text.GetValue()
                lc = str(text.GetScore())
                strlabel = strlabel+"\t\t* score="+lc+": "+lv+"\n"
            self._append_text(strlabel, self.labelStyle)

            self.text_ctrl.Newline()

        # progress finished!
        dialog.Destroy()


    def _append_text(self, text, style):
        """
        Append a text with the appropriate style.
        """
        self.text_ctrl.BeginStyle(style)
        self.text_ctrl.WriteText(text)
        self.text_ctrl.EndStyle();

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

# ----------------------------------------------------------------------------
# Third tab: Graphic view of each tier
# ----------------------------------------------------------------------------

class TierGraphicPanel( BaseTierPanel ):
    """
    @author:  Brigitte Bigi
    @contact: brigitte.bigi@gmail.com
    @license: GPL
    @summary: Graphical-view of tiers (TODO).

    """

    def __init__(self, parent, prefsIO):
        BaseTierPanel.__init__(self, parent, prefsIO)

    # ------------------------------------------------------------------------

# ----------------------------------------------------------------------------

def ShowPreviewDialog(parent, preferences, tiers):
    dialog = PreviewTierDialog(parent, preferences,tiers)
    dialog.ShowModal()
    dialog.Destroy()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = wx.PySimpleApp()
    ShowPreviewDialog(None,None,[])
    app.MainLoop()

# ---------------------------------------------------------------------------

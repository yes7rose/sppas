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
# File: dataroamerframe.py
# ----------------------------------------------------------------------------

import wx

from baseframe import ComponentFrame

from wxgui.sp_icons   import DATAROAMER_APP_ICON
from wxgui.sp_icons   import NEW_FILE
from wxgui.sp_icons   import SAVE_FILE
from wxgui.sp_icons   import SAVE_AS_FILE
from wxgui.sp_icons   import SAVE_ALL_FILE
from wxgui.sp_consts  import TB_ICONSIZE

from wxgui.cutils.imageutils        import spBitmap
from wxgui.clients.dataroamerclient import DataRoamerClient

# ----------------------------------------------------------------------------
# Constants
# ----------------------------------------------------------------------------

NEW_ID      = wx.NewId()
SAVE_AS_ID  = wx.NewId()
SAVE_ALL_ID = wx.NewId()

# ----------------------------------------------------------------------------

class DataRoamerFrame( ComponentFrame ):
    """
    @author:       Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      DataRoamer allows to manipulate annotated files.

    """
    def __init__(self, parent, idc, prefsIO):

        arguments = {}
        arguments['title'] = 'SPPAS - Data Roamer'
        arguments['icon']  = DATAROAMER_APP_ICON
        arguments['type']  = "DATAFILES"
        arguments['prefs'] = prefsIO

        ComponentFrame.__init__(self, parent, idc, arguments)

        self.toolbar.AddButton(NEW_ID,      NEW_FILE,  "New")
        self.toolbar.AddButton(wx.ID_SAVE,  SAVE_FILE, "Save")
        self.toolbar.AddButton(SAVE_AS_ID,  SAVE_AS_FILE, "Save as")
        self.toolbar.AddButton(SAVE_ALL_ID, SAVE_ALL_FILE, "Save all")
        self._LayoutFrame()

    # ------------------------------------------------------------------------

    def CreateClient(self, parent, prefsIO):
        """ Override. """

        return DataRoamerClient( parent,prefsIO )

    # ------------------------------------------------------------------------

    def DataRoamerProcessEvent(self, event):
        """
        Processes an event, searching event tables and calling zero or more
        suitable event handler function(s).  Note that the ProcessEvent
        method is called from the wxPython docview framework directly since
        wxPython does not have a virtual ProcessEvent function.
        """
        ide = event.GetId()

        if ide == NEW_ID:
            self._clientpanel.New()
            return True

        elif ide == wx.ID_SAVE:
            self._clientpanel.Save()
            return True

        elif ide == SAVE_AS_ID:
            self._clientpanel.SaveAs()
            return True

        elif ide == SAVE_ALL_ID:
            self._clientpanel.SaveAll()
            return True

        return wx.GetApp().ProcessEvent(event)

# ----------------------------------------------------------------------------

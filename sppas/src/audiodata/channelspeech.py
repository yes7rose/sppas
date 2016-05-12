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
# File: channelsil.py
# ----------------------------------------------------------------------------

from audioframes import AudioFrames
from channelvolume import ChannelVolume

# ----------------------------------------------------------------------------

class ChannelSpeech( object ):
    """
    @authors:      Nicolas Chazeau, Brigitte Bigi
    @organization: Laboratoire Parole et Langage, Aix-en-Provence, France
    @contact:      brigitte.bigi@gmail.com
    @license:      GPL, v3
    @copyright:    Copyright (C) 2011-2016  Brigitte Bigi
    @summary:      This class implements the silence finding on a channel.

    """
    def __init__(self, channel):
        """
        Constructor.

        @param channel (Channel) the input channel object
        @param m (float) is the minimum track duration (in seconds)

        """
        self.channel   = channel
        self.volstats  = ChannelVolume( channel, 0.01 )
        self.silences  = []

    # ------------------------------------------------------------------

    def get_channel(self):
        return self.channel

    def get_volstats(self):
        return self.volstats

    # ------------------------------------------------------------------
    # DEPRECATED Silence detection
    # ------------------------------------------------------------------

    def tracks(self, m):
        """
        Yield tuples (from,to) of the tracks, from the result of get_silence().
        @deprecated

        """
        from_pos = 0
        if len(self.silence)==0:
        # No silence: Only one track!
            yield 0,self.channel.get_nframes()
            return
        # At least one silence
        for to_pos, next_from in self.silence:
            if (to_pos - from_pos) >= (m * self.channel.get_framerate()):
                # Track is long enough to be considered a track.
                yield int(from_pos), int(to_pos)
            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self.channel.get_nframes()
        if (to_pos - from_pos) >= (m * self.channel.get_framerate()):
            yield int(from_pos), int(to_pos)


    def get_silence(self, p=0.250, v=150, s=0.):
        """
        Estimates silences from an audio file.
        @deprecated

        @param p (float) Minimum silence duration in seconds
        @param v (int) Expected minimum volume (rms value)
        @param s (float) Shift delta duration in seconds
        @return a set of frames corresponding to silences.

        """
        self.channel.seek(0)
        self.silence = []

        # Once silence has been found, continue searching in this interval
        nbreadframes = int(self.volstats.get_winlen() * self.channel.get_framerate())
        afterloop_frames = int(nbreadframes/2) #int((nbreadframes/2) * self.channel.get_framerate())
        initpos = i = self.channel.tell()

        # This scans the file in steps of frames whether a section's volume
        # is lower than silence_cap, if it is it is written to silence.
        while i < self.channel.get_nframes():

            curframe = self.channel.get_frames(nbreadframes)

            a = AudioFrames( curframe, self.channel.get_sampwidth(), 1)
            #volume = audioutils.get_rms(curframe, self.channel.get_sampwidth())
            volume = a.rms()
            if volume < v:

                # Continue searching in smaller steps whether the silence is
                # longer than read frames but smaller than read frames * 2.
                while volume < v and self.channel.tell() < self.channel.get_nframes():
                    curframe = self.channel.get_frames(afterloop_frames)

                    a = AudioFrames( curframe, self.channel.get_sampwidth(), 1)
                    volume = a.rms()
                    #volume   = audioutils.get_rms(curframe, self.channel.get_sampwidth())

                # If the last sequence of silence ends where the new one starts
                # it's a continuous range.
                if self.silence and self.silence[-1][1] == i:
                    self.silence[-1][1] = self.channel.tell()
                else:
                # append if silence is long enough
                    duree = self.channel.tell() - i
                    nbmin = int( (p+s) * self.channel.get_framerate())
                    if duree > nbmin:
                        # Adjust silence start-pos
                        __startpos = i + ( s * self.channel.get_framerate() )
                        # Adjust silence end-pos
                        __endpos = self.channel.tell() - ( s * self.channel.get_framerate() )
                        self.silence.append([__startpos, __endpos])

            i = self.channel.tell()

        # Return the position in the file to where it was when we got it.
        self.channel.seek(initpos)

    # ------------------------------------------------------------------
    # Utility method
    # ------------------------------------------------------------------

    def track_data(self, tracks):
        """
        Get the track data: a set of frames for each track.

        """
        nframes = self.channel.get_nframes()
        for from_pos, to_pos in tracks:
            if nframes < from_pos:
                # Accept a "DELTA" of 10 frames, in case of corrupted data.
                if nframes < from_pos-10:
                    raise ValueError("Position %d not in range(%d)" % (from_pos, nframes))
                else:
                    from_pos = nframes
            # Go to the provided position
            self.channel.seek(from_pos)
            # Keep in mind the related frames
            yield self.channel.get_frames(to_pos - from_pos)

    # ------------------------------------------------------------------
    # New silence detection
    # ------------------------------------------------------------------

    def extract_tracks(self, mintrackdur, shiftdurstart=0.010, shiftdurend=0.010):
        """
        Return a list of tuples (from,to) of the tracks.

        @param mintrackdur (float) The minimum duration for a track (in seconds)

        """
        tracks = []
        delta = int(mintrackdur * self.channel.get_framerate())

        shiftstart = int(shiftdurstart * self.channel.get_framerate())
        shiftend   = int(shiftdurend   * self.channel.get_framerate())

        from_pos = 0
        if len(self.silences)==0:
        # No silence: Only one track!
            tracks.append( (0,self.channel.get_nframes()) )
            return tracks

        # At least one silence
        for to_pos, next_from in self.silences:
            shift_from_pos = max(from_pos - shiftstart, 0)
            shift_to_pos   = min(to_pos + shiftend, self.channel.get_nframes())

            if (shift_to_pos-shift_from_pos) >= delta:
                # Track is long enough to be considered a track.
                tracks.append( (int(shift_from_pos), int(shift_to_pos)) )

            from_pos = next_from

        # Last track after the last silence
        # (if the silence does not end at the end of the channel)
        to_pos = self.channel.get_nframes()
        if (to_pos - from_pos) >= delta:
            tracks.append( (int(from_pos), int(to_pos)) )

        return tracks

    # ------------------------------------------------------------------

    def search_threshold_vol(self):
        """
        Try to fix optimally the threshold for speech/silence segmentation.

        """
        vmin  = self.volstats.min()
        vmean = self.volstats.mean()
        vcvar = 1.1 * self.volstats.coefvariation()
        alt = (vmean-vmin)/5.
        if alt > vcvar:
            vcvar=alt

        return vmin + int((vmean - vcvar))

    # ------------------------------------------------------------------

    def search_silences(self, threshold=0, mintrackdur=0.08):
        """
        Search windows with a volume lesser than a given threshold.

        @param threshold (int) Expected minimum volume (rms value)
        If threshold is set to 0, search_minvol() will assign a value.
        @param mintrackdur (float) The minimum duration for a track (in seconds)

        """
        if threshold == 0:
            threshold = self.search_threshold_vol()

        # This scans the volumes whether it is lower than silence_cap,
        # if it is it is written to silence.
        self.silences = []
        inside = False
        idxbegin = 0
        ignored = 0
        delta = int(mintrackdur / self.volstats.get_winlen())

        for i,v in enumerate(self.volstats):
            if v < threshold:
                if inside is False:
                    # It's the beginning of a block of zero volumes
                    idxbegin = i
                    inside = True
            else:
                if inside is True:
                    # It's the end of a block of non-zero volumes...
                    # or not if the track is very short!
                    if (i-idxbegin) > delta:
                        inside = False
                        idxend = i-ignored-1
                        start_pos = int(idxbegin * self.volstats.get_winlen() * self.channel.get_framerate())
                        end_pos   = int(idxend * self.volstats.get_winlen() * self.channel.get_framerate())
                        self.silences.append((start_pos,end_pos))
                        ignored = 0
                    else:
                        ignored += 1

        # Last interval
        if inside is True:
            start_pos = int(idxbegin * self.volstats.get_winlen() * self.channel.get_framerate())
            end_pos   = self.channel.get_nframes()
            self.silences.append((start_pos,end_pos))

        return threshold

    # ------------------------------------------------------------------

    def filter_silences(self, minsildur=0.250):
        """
        Return filtered silences areas.

        @param minsildur (float) Minimum silence duration in seconds
        @param shiftdurstart (float) Shift delta duration in seconds
        @param shiftdurend (float) Shift delta duration in seconds

        @return a list of tuples (start_pos,end_pos) of silences.

        """
        if len(self.silences) == 0:
            return

        filteredsil = []
        for (start_pos,end_pos) in self.silences:
            sildur = float(end_pos-start_pos) / float(self.channel.get_framerate())
            if sildur > minsildur:
                filteredsil.append( (start_pos,end_pos) )

        self.silences = filteredsil

        for (s,e) in self.silences:
            print " (",float(s)/float(self.channel.get_framerate())," ; ",float(e)/float(self.channel.get_framerate()),")"
        print "Number of silences: ",len(self.silences)

    # ------------------------------------------------------------------

    def set_silences(self, silences):
        """
        Fix manually silences!

        @param silences (list of tuples)

        """
        self.silences = silences

# ----------------------------------------------------------------------

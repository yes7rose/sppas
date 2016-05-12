#!/usr/bin/env python2
# -*- coding: utf8 -*-

import paths
import unittest
import os

import audiodata.io
from audiodata.audio import AudioPCM
from audiodata.audiodataexc import AudioDataError

from paths import SPPASSAMPLES,TEMP
sample_1 = os.path.join(SPPASSAMPLES, "samples-eng", "oriana1.wav")
sample_3 = os.path.join(SPPASSAMPLES, "samples-eng", "oriana3.wave")
sample_new = os.path.join(TEMP,"newFile.wav")
from utils.type import compare

class TestAudioPCM(unittest.TestCase):

    def setUp(self):
        pass
    def tearDown(self):
        pass

    def test_set_get(self):
        a1 = audiodata.io.open(sample_1)
        a2 = AudioPCM()
        a2.Set(a1)
        self.assertEqual(a1.get_channels(), a2.get_channels())
        self.assertEqual(a1.get_audiofp(), a2.get_audiofp())

    def test_channels(self):
        a1 = audiodata.io.open(sample_1)
        a2 = AudioPCM()
        a3 = audiodata.io.open(sample_3)

        # Test extract_channel
        with self.assertRaises(AudioDataError):
            a2.extract_channel(0)
        with self.assertRaises(AudioDataError):
            a1.extract_channel(2)

        cidx1 = a3.extract_channel()
        cidx2 = a3.extract_channel( 1 )

        c1 = a3.get_channel(cidx1)
        c2 = a3.get_channel(cidx2)

        self.assertEqual(0, a2.append_channel( c1 ) )
        self.assertEqual(1, a2.append_channel( c2 ) )
        a2.insert_channel( 0, c1 )
        self.assertTrue( a2.verify_channels())

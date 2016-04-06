#!/usr/bin/env python
#
# Copyright (c) 2015 Blizzard Entertainment
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
from importlib import import_module
from collections import defaultdict

from . import mpyq
from . import protocol29406


def as_dict(data, field):
    """Sorts a list of event messages into a dictionary by event type

    :param data: List of events
    :param field: The event field to use as a key in the new dictionary
    """
    tmp = defaultdict(list)
    for msg in data:
        tmp[msg[field]].append(msg)

    return tmp


def strip_key_prefix(data, n):
    """Strip a prefix of a given length from all dictionary keys

    :param data: Dictionary with keys that are too long
    :param n: Number of characters of common prefix to remove
    """
    tmp = {}
    for k, v in data.items():
        tmp[k[n:]] = v

    return tmp


class Replay:
    """Parses a Heroes of the Storm replay file, automatically selecting the correct protocol"""
    def __init__(self, fpath):
        """Initialize a Heroes of the Storm replay parser

        :param fpath: Path to a .StormReplay file
        """
        self._archive = mpyq.MPQArchive(fpath)

        contents = self._archive.header['user_data_header']['content']
        self.header = protocol29406.decode_replay_header(contents)

        # The header's base_build determines which protocol to use
        self.base_build = self.header['m_version']['m_baseBuild']
        try:
            self.protocol = import_module('.protocol%s' % (self.base_build,), 'heroprotocol')
        except:
            raise RuntimeError('Unsupported base build: %d' % self.base_build)

        self.details = []
        self.initdata = []
        self.game = []
        self.messages = []
        self.tracker = []
        self.attributes = []

    def load_details(self):
        """Loads data from replay.details"""
        contents = self._archive.read_file('replay.details')
        self.details = self.protocol.decode_replay_details(contents)

    def load_initdata(self):
        """Loads data from replay.initData"""
        contents = self._archive.read_file('replay.initData')
        self.initdata = self.protocol.decode_replay_initdata(contents)['m_syncLobbyState']

    def load_game(self):
        """Loads data from replay.game.events"""
        contents = self._archive.read_file('replay.game.events')
        self.game = strip_key_prefix(as_dict([e for e in self.protocol.decode_replay_game_events(contents)],
                                             '_event'), len('NNet.Game.S'))

    def load_messages(self):
        """Loads data from replay.messages.events"""
        contents = self._archive.read_file('replay.message.events')
        self.messages = strip_key_prefix(as_dict([e for e in self.protocol.decode_replay_message_events(contents)],
                                                 '_event'), len('NNet.Game.S'))

    def load_tracker(self):
        """Loads data from replay.tracker.events"""
        if hasattr(self.protocol, 'decode_replay_tracker_events'):
            contents = self._archive.read_file('replay.tracker.events')
            self.tracker = strip_key_prefix(as_dict([e for e in self.protocol.decode_replay_tracker_events(contents)],
                                                    '_event'), len('NNet.Replay.Tracker.S'))

    def load_attribute(self):
        """Loads data from replay.attributes.events"""
        contents = self._archive.read_file('replay.attributes.events')
        self.attributes = [e for e in self.protocol.decode_replay_attributes_events(contents)]

    def load(self, details=True, initdata=True, game=True, messages=True, tracker=True, attribute=True):
        if details:
            self.load_details()
        if initdata:
            self.load_initdata()
        if game:
            self.load_game()
        if messages:
            self.load_messages()
        if tracker:
            self.load_tracker()
        if attribute:
            self.load_attribute()

    def close(self):
        """Removes the MPQ archive from the class after reading"""
        self._archive = None

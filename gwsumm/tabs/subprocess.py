# coding=utf-8
# Copyright (C) Ryan Fisher (2014)
#
# This file is part of GWSumm
#
# GWSumm is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# GWSumm is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with GWSumm.  If not, see <http://www.gnu.org/licenses/>

"""Definition of the `SubprocessTab`
"""

import re

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from dateutil import tz

import numpy

from matplotlib.cm import get_cmap
from matplotlib.colors import Normalize

from astropy.time import Time

from glue.lal import Cache

from gwpy.segments import (DataQualityDict, SegmentList, Segment)
from gwpy.plotter import SegmentPlot

from ..config import (GWSummConfigParser, NoOptionError)
from ..state import ALLSTATE
from .registry import (get_tab, register_tab)
from .. import (globalv, html)
from ..data import (get_timeseries, get_timeseries_dict)
from ..segments import get_segments
from ..plot.registry import (get_plot, register_plot)
from ..utils import (vprint, re_quote)

__author__ = 'Ryan Fisher <ryan.fisher@ligo.org>'

DataTab = get_tab('default')
UTC = tz.gettz('UTC')
REQUESTSTUB = '+request'
NOMINALSTUB = '+nominal'
MODE_COLORS = ['grey', 'magenta', 'red', 'saddlebrown']


class SubprocessTab(DataTab):
    """Runs a subprocess and dumps output to html in a tab
    """
    type = 'archived-subprocess'

    @classmethod
    def from_ini(cls, config, section, plotdir='plots', **kwargs):
        """Define a new `SubprocessTab`.
        """
        new = super(DataTab, cls).from_ini(config, section, **kwargs)
        if len(new.states) > 1 or new.states[0].name != ALLSTATE:
            raise ValueError("SubprocessTab does not accept state selection")
        new.executable = config.get(section, 'executable')
        new.args = config.get(section, 'arguments')
        # Allowing for the gps_time to be passed as an option to the executable
        # e.g. "executable -s 123456789 -o 'other option'"
        new.gpstime_option = ""
        try:
            new.gpstime_option = config.get(section, 'gpstime_option')
        new.gps_time = config.get(section, 'gpstime')
        if new.gpstime_option!="":
            new.gps_time_with_option = " ".join([new.gpstime_option,new.gps_time])
        else:
            new.gps_time_with_option = new.gps_time

        return new

    def process(self, nds=None, multiprocess=True,
                config=GWSummConfigParser(), datacache=None,
                segmentcache=Cache(), datafind_error='raise', **kwargs):
        """Runs the executable with provided arguments as a subprocess.
        
        Runs with gpstime argument as first input to command.
        """
        ## Fix!!! Sanitize input before these two lines:
        executable=self.executable
        args=self.args
        gps_time=self.gps_time
        gps_time_with_option = self.gps_time_with_option
        #argument_list = [i for i in args.split()]
        command=[]
        command.append(executable)
        # Assumes gps time should be first argument with or without an option 
        # prefixing the time (e.g. -s 111111111)
        command.append(gps_time_with_option)
        #[command.append(arg) for arg in argument_list]
        for argument in args:
            command.append(argument)
        try:
            output=subprocess.check_output(command)
            self.result=output
        except CalledProcessError as err:
            self.result=""
            self.result+="Error encountered in subprocess call \n"
            self.result += "Command attempted: \n"
            self.result += err.cmd + "\n"
            self.result += "Return code: \n"
            self.result += err.returncode+ "\n"
            self.result += "Error Message: \n"
            self.result += err.cmd + "\n"
        except:
            raise


    def write_html(self):
        return super(SubprocessTab, self).write_html(self.result, plots=False)

register_tab(SubprocessTab)

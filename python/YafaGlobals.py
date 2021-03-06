# Copyright 2015 Nico Lugil <nico at lugil dot be>
#
# This file is part of Yafa!
#
# Yafa! is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Yafa! is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Yafa. If not, see <http://www.gnu.org/licenses/>.

from ParseSettings import Settings
import threading
import time
from Queue import Queue

# TODO: wrap stuff in class ?
# TODO: use single/multi lock?

task_q=Queue()

main_lock=threading.Lock()
settings = Settings()
class Mode:
    boot, wait_for_start, requested2run, run = ["boot", "wait_for_start", "requested2run", "run"]
mode = Mode.boot
timeleft = 10 #*60  # serves as initial value for worker countdown

lock_temperature=threading.Lock()
temperature='Not yet measured'



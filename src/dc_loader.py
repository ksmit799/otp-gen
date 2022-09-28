from panda3d.core import *
from panda3d.direct import *

from src.notifier import notify


class DCLoader:
    notify = notify.new_category("DCLoader")

    def __init__(self):
        self._dc_file = DCFile()
        self._dc_suffix = ""

        self._dclasses_by_name = {}
        self._dclasses_by_number = {}

        self._hash_value = 0

    @property
    def dc_file(self):
        return self._dc_file

    @property
    def dc_suffix(self):
        return self._dc_suffix

    @property
    def dclasses_by_name(self):
        return self._dclasses_by_name

    @property
    def dclasses_by_number(self):
        return self._dclasses_by_number

    @property
    def hash_value(self):
        return self._hash_value

    def read_dc_files(self, dc_file_names=None):
        if dc_file_names is None:
            read_result = self._dc_file.readAll()
            if not read_result:
                self.notify.error("Could not read dc file.")
        else:
            for dc_fileName in dc_file_names:
                pathname = Filename(dc_fileName)
                read_result = self._dc_file.read(pathname)
                if not read_result:
                    self.notify.error("Could not read dc file: %s" % pathname)

        self._hash_value = self._dc_file.getHash()

        # Now get the class definition for the classes named in the DC
        # file.
        for i in range(self._dc_file.getNumClasses()):
            dclass = self._dc_file.getClass(i)
            number = dclass.get_number()
            class_name = dclass.get_name() + self._dc_suffix

            self._dclasses_by_name[class_name] = dclass
            if number >= 0:
                self._dclasses_by_number[number] = dclass

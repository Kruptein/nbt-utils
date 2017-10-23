import os
import zlib
from collections import namedtuple

from nbt import NBT

Coord = namedtuple('Coord', ['x', 'y', 'z'])


class Region:
    def __init__(self, x, z, regionpath=os.getcwd()):
        self.x = x
        self.z = z
        self.filename = 'r.{}.{}.mca'.format(x, z)
        self.regionpath = regionpath
        self.is_read = False
        self.raw_data = None

    @classmethod
    def from_chunk_coord(cls, coord: Coord, regionpath=os.getcwd()):
        return cls(coord.x >> 5, coord.z >> 5, regionpath=regionpath)

    @classmethod
    def from_file(cls, fp, regionpath=os.getcwd()):
        parts = fp.split(".")
        return cls(parts[1], parts[2], regionpath=regionpath)

    @staticmethod
    def get_chunk_location_offset(coord):
        return 4 * ((coord.x & 31) + (coord.z & 31) * 32)

    @staticmethod
    def get_chunk_timestamp(coord):
        return Region.get_chunk_location_offset(coord) + 4096

    def read(self):
        fp = os.path.join(self.regionpath, self.filename)
        if not os.path.exists(fp):
            raise FileNotFoundError("The region file was not found in the current path: {}".format(fp))
        with open(fp, 'rb') as f:
            self.raw_data = b''.join(f.readlines())
        self.is_read = True

    def chunks(self):
        if not self.is_read:
            self.read()
        i = 0
        while i < 4095:
            yield self.__get_chunk_data(i)
            i += 4

    def get_chunk_data(self, coord: Coord):
        if not self.is_read:
            self.read()
        return self.__get_chunk_data(Region.get_chunk_location_offset(coord))

    def __get_chunk_data(self, location):
        # the sector offset is in orders of 4KiB sectors
        sector_offset = int.from_bytes(self.raw_data[location:location + 3], byteorder='big',
                                       signed=True) * 4 * 1024
        sector_count = self.raw_data[location + 3] * 4 * 1024
        raw_chunkdata = self.raw_data[sector_offset:sector_offset + sector_count]
        chunk_size = int.from_bytes(raw_chunkdata[:4], byteorder='big', signed=True)
        compression = raw_chunkdata[4]
        data = raw_chunkdata[5:]
        if compression == 2:
            data = zlib.decompress(data)
        return NBT(data=data)

import os
import zlib
from collections import namedtuple

from nbt import NBT

Coord = namedtuple('Coord', ['x', 'y', 'z'])


class Region:
    def __init__(self, x, z):
        self.x = x
        self.z = z
        self.filename = 'r.{}.{}.mca'.format(x, z)
        self.is_read = False
        self.raw_data = None

    @classmethod
    def from_chunk_coord(cls, coord: Coord):
        return cls(coord.x >> 5, coord.z >> 5)

    @staticmethod
    def get_chunk_location_offset(coord):
        return 4 * ((coord.x & 31) + (coord.z & 31) * 32)

    @staticmethod
    def get_chunk_timestamp(coord):
        return Region.get_chunk_location_offset(coord) + 4096

    def read(self):
        if not os.path.exists(self.filename):
            raise FileNotFoundError("The region file was not found in the current path: {}".format(os.getcwd()))
        with open(self.filename, 'rb') as f:
            self.raw_data = b''.join(f.readlines())
        self.is_read = True

    def get_chunk_data(self, coord: Coord):
        if not self.is_read:
            self.read()
        header_offset = Region.get_chunk_location_offset(coord)
        # the sector offset is in orders of 4KiB sectors
        sector_offset = int.from_bytes(self.raw_data[header_offset:header_offset + 3], byteorder='big',
                                       signed=True) * 4 * 1024
        sector_count = self.raw_data[header_offset + 3] * 4 * 1024
        raw_chunkdata = self.raw_data[sector_offset:sector_offset + sector_count]
        chunk_size = int.from_bytes(raw_chunkdata[:4], byteorder='big', signed=True)
        compression = raw_chunkdata[4]
        data = raw_chunkdata[5:]
        if compression == 2:
            data = zlib.decompress(data)
        return NBT(data=data), raw_chunkdata

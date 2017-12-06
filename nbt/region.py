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

    def __repr__(self):
        return "Region({},{})".format(self.x, self.z)

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
            self.raw_data = bytearray(b''.join(f.readlines()))
        self.is_read = True

    def write(self):
        fp = os.path.join(self.regionpath, self.filename)
        with open(fp, 'wb') as f:
            f.write(self.raw_data)

    def chunks(self):
        if not self.is_read:
            self.read()
        for i in range(0, 1024, 4):
            yield self.__get_chunk_data(i)

    def set_chunk_data(self, location, data):
        sector_offset = int.from_bytes(self.raw_data[location:location + 3], byteorder='big',
                                       signed=True) * 4 * 1024
        sector_count = self.raw_data[location + 3] * 4 * 1024
        if sector_offset == 0 and sector_count == 0:
            return
        raw_chunkdata = self.raw_data[sector_offset:sector_offset + sector_count]
        compression = raw_chunkdata[4]
        if compression == 2:
            data = zlib.compress(data)

        raw_chunkdata[:4] = len(data).to_bytes(4, byteorder='big', signed=True)  # set chunk size

        raw_chunkdata[5:] = data.ljust(sector_count - 5, b'\x00')  # 5 = lenght(4) + compression(1)
        self.raw_data[sector_offset:sector_offset + sector_count] = raw_chunkdata

    def get_chunk_data(self, coord: Coord):
        if not self.is_read:
            self.read()
        return self.__get_chunk_data(Region.get_chunk_location_offset(coord))

    def __get_chunk_data(self, location):
        # print("Handling chunk {}".format(location))
        # the sector offset is in orders of 4KiB sectors
        sector_offset = int.from_bytes(self.raw_data[location:location + 3], byteorder='big',
                                       signed=True) * 4 * 1024
        sector_count = self.raw_data[location + 3] * 4 * 1024
        if sector_offset == 0 and sector_count == 0:
            n = NBT()
            n.chunk_coord = location
            return n

        raw_chunkdata = self.raw_data[sector_offset:sector_offset + sector_count]
        chunk_size = int.from_bytes(raw_chunkdata[:4], byteorder='big', signed=True)
        compression = raw_chunkdata[4]
        data = raw_chunkdata[5:]
        if compression == 2:
            data = zlib.decompress(data)
        n = NBT(data=data)
        n.chunk_coord = location
        return n

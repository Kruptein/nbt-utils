import os

from nbt.region import Coord, Region


def get_referees(coord: Coord, regionpath=os.getcwd()):
    """
    Get all the commandblocks referencing the given coord.
    """

    for fl in os.listdir(regionpath):
        if fl.endswith(".mca"):
            get_ref_coord(coord, Region.from_file(fl, regionpath))


def get_ref_coord(coord: Coord, region: Region):
    for chunk in region.chunks():  # get_chunk_data(Coord(coord.x//16, coord.y//16, coord.z//16))
        if len(chunk.root[b'Level'][b'TileEntities'].tags) > 0:
            yield chunk

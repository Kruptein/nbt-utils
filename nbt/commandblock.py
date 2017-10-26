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
    print("Processing region: {}".format(region))
    absc = "{}:{}:{}".format(coord.x, coord.y, coord.z)
    for chunk in region.chunks():  # get_chunk_data(Coord(coord.x//16, coord.y//16, coord.z//16))
        for tag in chunk.root[b'Level'][b'TileEntities'].tags:
            if tag[b'id'].value == 'minecraft:command_block':
                relc = "{}:{}:{}".format(
                    tag[b'x'].value - coord.x,
                    tag[b'y'].value - coord.y,
                    tag[b'z'].value - coord.z,
                )
                if absc in tag[b'Command'] or relc in tag[b'Command']:
                    print(tag.tags)


if __name__ == '__main__':
    GENCOORD = Coord(-627, 4, -1034)
    CHUNKCOORD = Coord(GENCOORD.x // 16, GENCOORD.y // 16, GENCOORD.z // 16)
    PATH = "/home/darragh/dev/Lumen/run/saves/TutorialWorldV3.0.9/region"
    os.chdir(PATH)
    r = Region.from_chunk_coord(CHUNKCOORD, regionpath=PATH)
    a = list(r.chunks())

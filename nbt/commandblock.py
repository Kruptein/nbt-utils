import os

from nbt.region import Coord, Region


def test(regionpath):
    cb = []
    R = Region.from_file("r.-2.-2.mca", regionpath=os.getcwd())
    for c in list(R.chunks()):
        if c.root.tags == {}:
            continue
        for tag in c.root[b'Level'][b'TileEntities'].tags:
            # print(tag[b'id'])
            if tag[b'id'].value == b'minecraft:command_block':
                cb.append((c, tag))


def fix_command_blocks(regionpath):
    for fl in os.listdir(regionpath):
        if fl.endswith(".mca"):
            fix_command_blocks_in_region(Region.from_file(fl, regionpath=regionpath))


def fix_command_blocks_in_region(region):
    for chunk in region.chunks():
        print(chunk.chunk_coord)
        if b'Level' not in chunk.root:
            continue
        for tag in chunk.root[b'Level'][b'TileEntities'].tags:
            if tag[b'id'].value == b'minecraft:command_block':
                if b'translate:' in tag[b'Command'].value:
                    tag[b'Command'].value = tag[b'Command'].value.replace(b'translate:', b'\"translate\":')
        region.set_chunk_data(chunk.chunk_coord, chunk.write())
    region.write()


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
            if tag[b'id'].value == b'minecraft:command_block':
                relc = "{}:{}:{}".format(
                    tag[b'x'].value - coord.x,
                    tag[b'y'].value - coord.y,
                    tag[b'z'].value - coord.z,
                )
                if absc in tag[b'Command'] or relc in tag[b'Command']:
                    print(tag.tags)


if __name__ == '__main__':
    import os
    from nbt import region

    GENCOORD = region.Coord(-627, 4, -1034)
    CHUNKCOORD = region.Coord(GENCOORD.x // 16, GENCOORD.y // 16, GENCOORD.z // 16)
    PATH = "/home/darragh/dev/Lumen/run/saves/TutorialWorldV3.0.9/region"
    os.chdir(PATH)
    r = region.Region.from_file("r.-2.-2.mca", regionpath=os.getcwd())
    fix_command_blocks_in_region(r)

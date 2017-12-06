import os

from nbt.region import Region


def fix_command_blocks(regionpath):
    for fl in os.listdir(regionpath):
        if fl.endswith(".mca"):
            print(fl)
            fix_command_blocks_in_region(Region.from_file(fl, regionpath=regionpath))


def fix_command_blocks_in_region(region):
    for chunk in region.chunks():
        if b'Level' not in chunk.root:
            continue
        for tag in chunk.root[b'Level'][b'TileEntities'].tags:
            if tag[b'id'].value == b'minecraft:command_block':
                if b'translate:' in tag[b'Command'].value:
                    tag[b'Command'].value = tag[b'Command'].value.replace(b'translate:', b'\\"translate\\":')
                if b'text:' in tag[b'Command'].value:
                    tag[b'Command'].value = tag[b'Command'].value.replace(b'text:', b'\\"text\\":')
        region.set_chunk_data(chunk.chunk_coord, chunk.write())
    region.write()

import struct


class NBT:
    def __init__(self, data=None, fileobj=None):
        self.root = TagCompound(name='')
        self.chunk_coord = None
        if fileobj is not None:
            data = b''.join(fileobj.readlines())
        if data is not None:
            self.__pointer = 0
            self.raw_data = data
            self.root = get_tag(self._pop()).load(self)

    def __repr__(self):
        return repr(self.root) if self.root else 'NBT()'

    def _pop(self, size=1):
        self.__pointer += size
        return self.raw_data[self.__pointer - size:self.__pointer]

    def write(self, fileobj=None):
        output = TagByte(10).to_bytes() + self.root.to_bytes()
        if fileobj is not None:
            fileobj.write(output)
        else:
            return output


class Tag:
    def __init__(self, tag_type, name=None):
        self.tag_type = tag_type
        if name is None:
            self.name = TagEmptyString()
        else:
            if isinstance(name, str):
                self.name = TagString(name)
            else:
                self.name = name

    def to_bytes(self):
        pass

    def __contains__(self, item):
        if hasattr(self, 'tags'):
            return item in self.tags
        return item in self.__dict__


class TagEnd(Tag):
    TYPE = 0

    def __init__(self):
        super().__init__(TagEnd.TYPE)

    @classmethod
    def load(cls, nbt, parse_name=False):
        return cls()

    def to_bytes(self):
        return b'\x00'


class TagByte(Tag):
    TYPE = 1

    def __init__(self, value, name=None):
        super().__init__(TagByte.TYPE, name=name)
        self.value = value

    def __repr__(self):
        return "TagByte({}:{})".format(
            self.name.value if hasattr(self.name, 'value') else b'',
            self.value
        )

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        value = int.from_bytes(nbt._pop(), byteorder='big', signed=True)
        return cls(value, name)

    def to_bytes(self):
        return self.name.to_bytes() + struct.pack(">b", self.value)

    def to_obj(self):
        return self.value


class TagShort(Tag):
    TYPE = 2

    def __init__(self, value, name=None):
        super().__init__(TagShort.TYPE, name)
        self.value = value

    def __repr__(self):
        return "TagShort({}:{})".format(
            self.name.value if hasattr(self.name, 'value') else b'',
            self.value
        )

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        value = int.from_bytes(nbt._pop(2), byteorder='big', signed=True)
        return cls(value, name)

    def to_bytes(self):
        return self.name.to_bytes() + struct.pack(">h", self.value)

    def get_value_length(self):
        return len(self.to_bytes())

    def to_obj(self):
        return self.value


class TagInt(Tag):
    TYPE = 3

    def __init__(self, value, name=None):
        super().__init__(TagInt.TYPE, name)
        self.value = value

    def __repr__(self):
        return "TagInt({}:{})".format(
            self.name.value if hasattr(self.name, 'value') else b'',
            self.value
        )

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        d = nbt._pop(4)
        value = int.from_bytes(d, byteorder='big', signed=True)
        return cls(value, name)

    def to_bytes(self):
        return self.name.to_bytes() + struct.pack(">i", self.value)

    def to_obj(self):
        return self.value


class TagLong(Tag):
    TYPE = 4

    def __init__(self, value, name=None):
        super().__init__(TagLong.TYPE, name)
        self.value = value

    def __repr__(self):
        return "TagLong({}:{})".format(self.name.value, self.value)

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        value = int.from_bytes(nbt._pop(8), byteorder='big', signed=True)
        return cls(value, name)

    def to_bytes(self):
        return self.name.to_bytes() + struct.pack(">q", self.value)

    def to_obj(self):
        return self.value


class TagFloat(Tag):
    TYPE = 5

    def __init__(self, value, name=None):
        super().__init__(TagFloat.TYPE, name)
        self.value = value

    def __repr__(self):
        return "TagFloat({}:{})".format(
            self.name.value if hasattr(self.name, 'value') else b'',
            self.value
        )

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        value = struct.unpack('>f', nbt._pop(4))[0]
        return cls(value, name)

    def to_bytes(self):
        return self.name.to_bytes() + struct.pack(">f", self.value)

    def to_obj(self):
        return self.value


class TagDouble(Tag):
    TYPE = 6

    def __init__(self, value, name=None):
        super().__init__(TagDouble.TYPE, name)
        self.value = value

    def __repr__(self):
        return "TagDouble({}:{})".format(
            self.name.value if hasattr(self.name, 'value') else b'',
            self.value
        )

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        value = struct.unpack('>d', nbt._pop(8))[0]
        return cls(value, name)

    def to_bytes(self):
        return self.name.to_bytes() + struct.pack(">d", self.value)

    def to_obj(self):
        return self.value


class TagEmptyString:
    def __init__(self):
        pass

    def to_bytes(self):
        return b''


class TagByteArray(Tag):
    TYPE = 7

    def __init__(self, array=None, name=None):
        super().__init__(TagByteArray.TYPE, name)
        self.array = array

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        length = TagInt.load(nbt, False)
        array = TagByteArray.parse_array(length, nbt)
        return cls(array=array, name=name)

    @staticmethod
    def parse_array(length, nbt):
        array = []
        while len(array) != length.value:
            array.append(TagByte.load(nbt, parse_name=False))
        return array

    def to_bytes(self):
        return self.name.to_bytes() + TagInt(len(self.array)).to_bytes() + b''.join(
            x.to_bytes() for x in self.array)

    def to_obj(self):
        return [b.to_obj() for b in self.array]


class TagString(Tag):
    TYPE = 8

    def __init__(self, value, name=None):
        super().__init__(TagString.TYPE, name)
        if isinstance(value, str):
            self.value = bytes(value, 'utf-8')
        else:
            self.value = value
        self.length = TagShort(len(value))

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        length = TagShort.load(nbt, False)
        value = nbt._pop(length.value)
        return cls(value, name)

    def to_bytes(self):
        return self.name.to_bytes() + self.length.to_bytes() + self.value

    def to_obj(self):
        return self.value

    def __repr__(self):
        return "TagString({})".format(self.value)


class TagList(Tag):
    TYPE = 9

    def __init__(self, tag_id=None, tag_type=None, tags=None, name=None):
        super().__init__(TagList.TYPE, name)
        if tag_id is None and tag_type is None:
            raise Exception("Either tag_id or tag_type has to have a value")
        self.tags = []
        if tags is not None:
            self.tags = tags
        if tag_type is not None:
            tag_id = tag_type.TYPE
        self.tag_id = TagByte(int.from_bytes(tag_id, byteorder='big', signed=True))

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        tag_id = nbt._pop()
        length = TagInt.load(nbt, False)
        tags = TagList.parse_tags(tag_id, length, nbt)
        return cls(tag_id=tag_id, tags=tags, name=name)

    @staticmethod
    def parse_tags(tag_id, length, nbt):
        tags = []
        while len(tags) != length.value:
            tag = get_tag(tag_id).load(nbt, parse_name=False)
            tags.append(tag)
        return tags

    def to_bytes(self):
        return self.name.to_bytes() + self.tag_id.to_bytes() + TagInt(len(self.tags)).to_bytes() + b''.join(
            x.to_bytes() for x in self.tags)

    def to_obj(self):
        return [tag.to_obj() for tag in self.tags]

    def __repr__(self):
        return "TagList({})".format(self.name.value)

    def __getitem__(self, item):
        return self.tags[item]

    def __setitem__(self, item, value):
        self.tags[item] = value


class TagCompound(Tag):
    TYPE = 10

    def __init__(self, tags=None, name=None):
        super().__init__(TagCompound.TYPE, name)
        self.tags = {}
        if tags is not None:
            self.tags = tags

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        tags = TagCompound.parse_tags(nbt)
        return cls(tags, name)

    @staticmethod
    def parse_tags(nbt):
        tags = {}
        while True:
            try:
                tag_id = nbt._pop()
                tag = get_tag(tag_id).load(nbt)
            except KeyError:
                print("Could not interpret tag {}".format(tag_id))
                continue
            if isinstance(tag, TagEnd):
                break
            tags[tag.name.value] = tag
        return tags

    def to_bytes(self, root_tag=False):
        rt = TagByte(self.tag_type).to_bytes() if root_tag else b''
        return rt + self.name.to_bytes() + b''.join(
            TagByte(x.tag_type).to_bytes() + x.to_bytes() for x in self.tags.values()) + TagEnd().to_bytes()

    def to_obj(self):
        return {k: v.to_obj() for k, v in self.tags.items()}

    def __getitem__(self, item):
        if item in self.tags:
            return self.tags[item]

    def __setitem__(self, item, value):
        if item in self.tags:
            self.tags[item] = value

    def __repr__(self):
        return "TagCompound({})".format(self.name.value if hasattr(self.name, 'value') else b'')


class TagIntArray(Tag):
    TYPE = 11

    def __init__(self, array=None, name=None):
        super().__init__(TagIntArray.TYPE, name)
        self.array = array

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        length = TagInt.load(nbt, False)
        array = TagIntArray.parse_array(length, nbt)
        return cls(array=array, name=name)

    @staticmethod
    def parse_array(length, nbt):
        array = []
        while len(array) != length.value:
            tag = TagInt.load(nbt, parse_name=False)
            array.append(tag)
        return array

    def to_bytes(self):
        return self.name.to_bytes() + TagInt(len(self.array)).to_bytes() + b''.join(
            x.to_bytes() for x in self.array)

    def to_obj(self):
        return [i.to_obj() for i in self.array]


class TagLongArray(Tag):
    TYPE = 12

    def __init__(self, array=None, name=None):
        super().__init__(TagLongArray.TYPE, name)
        self.array = array

    @classmethod
    def load(cls, nbt, parse_name=True):
        name = get_name(nbt) if parse_name else TagEmptyString()
        length = TagInt.load(nbt, False)
        array = TagLongArray.parse_array(length, nbt)
        return cls(array=array, name=name)

    @staticmethod
    def parse_array(length, nbt):
        array = []
        while len(array) != length.value:
            tag = TagLong.load(nbt, parse_name=False)
            array.append(tag)
        return array

    def to_bytes(self):
        return self.name.to_bytes() + TagInt(len(self.array)).to_bytes() + b''.join(
            x.to_bytes() for x in self.array)

    def to_obj(self):
        return [i.to_obj() for i in self.array]


TAGS = {
    0: TagEnd,
    1: TagByte,
    2: TagShort,
    3: TagInt,
    4: TagLong,
    5: TagFloat,
    6: TagDouble,
    7: TagByteArray,
    8: TagString,
    9: TagList,
    10: TagCompound,
    11: TagIntArray,
    12: TagLongArray
}


def get_tag(tag_type):
    return TAGS[int.from_bytes(tag_type, byteorder='big', signed=True)]


def get_name(nbt):
    return TagString.load(nbt, parse_name=False)

from enum import IntFlag

class EntryAttribute(IntFlag):
    READ_ONLY = 0x1
    HIDDEN = 0x2
    SYSTEM = 0x4
    VOLUME = 0x8
    DIRECTORY = 0x10
    ARCHIVE = 0x20
    LFN = READ_ONLY | HIDDEN | SYSTEM | VOLUME
    FILE = 0

class DirectoryEntry:
    name: str
    start_cluster: int
    length: int
    attributes: EntryAttribute


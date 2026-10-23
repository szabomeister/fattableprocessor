import struct
from DirEntry import EntryAttribute

class FatAnalyzer:
  def __init__(self, file):
    self.filesystem = file
    self.jump_code = None
    self.identifier = None
    self.bytes_per_sector = None
    self.sector_per_alloc = None
    self.reserved_sectors = None
    self.no_of_fats = None
    self.root_entries = None
    self.total_sectors = None
    self.media_type = None
    self.sectors_per_fat = None
    self.sectors_per_track = None
    self.no_of_heads = None
    self.no_of_hidden_sectors = None
    self.total_sectors_32 = None
    self.drive_id = None
    self.volume_serial_id = None
    self.volume_name = None
    self.fat_type = None
    self.fat1_start_sector = None
    self.fat2_start_sector = None
    ...

  def read_sector(self, start_sector1):
    ...

  def read_cluster(self, cluster_num):
    first_sector = self.cluster_to_sector(cluster_num)
    self.filesystem.seek(first_sector * self.bytes_per_sector)
    retval = self.filesystem.read(self.sector_per_alloc * self.bytes_per_sector)
    return retval
    ...

  def read_fat1(self):
    ret = None
    fat1_start_byte = self.fat1_start_sector * self.bytes_per_sector
    self.filesystem.seek(fat1_start_byte)
    ret = self.filesystem.read(self.sectors_per_fat * self.bytes_per_sector)
    return ret
    ...

  def follow_fat_chain(self, actual_cluster):
    fat_table = self.read_fat1()
    actual_entry = struct.unpack("<H", fat_table[2*actual_cluster: 2*actual_cluster+2])[0]
    # print(f"actual fat entry: {actual_entry} {actual_entry:#x}")
    return actual_entry
    ...

  def read_file(self, first_cluster, file_size):
    iter = 0
    cluster_num = first_cluster
    remaining_size = file_size
    while iter < 30:
      part = self.read_cluster(cluster_num)
      if remaining_size < self.sector_per_alloc * self.bytes_per_sector:
        part = part[0:remaining_size]
      print(f"{part}")

      remaining_size -= (self.sector_per_alloc * self.bytes_per_sector)
      cluster_num = self.follow_fat_chain(cluster_num)
      if cluster_num == 0xffff:
        break
      iter += 1
    ...

  def read_directory(self, cluster):
    print(f"Reading directory entry cluster")
    directory_cluster_data = self.read_cluster(cluster)
    self.process_root_dir(directory_cluster_data)
    ...

  def cluster_to_sector(self, cluster_num):
    data_start_sector = (self.find_root_dir_first_sector() +
                         int((self.root_entries * 32) / self.bytes_per_sector))
    retval = data_start_sector + (cluster_num -2) * self.sector_per_alloc
    return retval
    ...

  def find_root_dir_first_sector(self):
    root_dir_start_sector = (self.no_of_hidden_sectors +
                             self.reserved_sectors +
                             self.sectors_per_fat *
                             self.no_of_fats)
    return root_dir_start_sector
    ...

  def process_root_dir_entry(self, data):
    if data[0] == 0xe5:
      print(f"deleted")
    elif data[0] == 0:
      print(f"empty")
    elif data[11] == 0xf:
      print(f"lfn")
      unicode_name = struct.unpack("<B5H3x6H2x2H", data[0:32])
      name=bytes( (0 if char == 0xffff else char for char in unicode_name) ).decode('utf-8').rstrip('\0')
      print(f"{unicode_name} {name}")
    else:
      # dos_name = struct.unpack("11s", data[0:11])
      # entry_attributes = struct.unpack("<B", data[11:12])
      # data_location_cluster = struct.unpack("<H", data[26:28])
      # data_length = struct.unpack("<i", data[28:32])

      dos_name,entry_attributes,data_location_cluster, data_length = struct.unpack("<11sB14xHi",data)
      attrib = EntryAttribute(entry_attributes)
      print(f"Attrib: {str(attrib)}")
      if EntryAttribute.DIRECTORY in attrib:
        print(f"Entry is directory")
      if EntryAttribute.LFN in attrib:
        print(f"Entry is LFN part")

      print(f"name: {dos_name} attrib: {entry_attributes:#x} s_cluster: {data_location_cluster} length: {data_length}")
    return data[0]
    ...

  def process_root_dir(self, data):
    pos = 0
    iter = 0
    data_len = len(data)

    while pos+32 <= data_len and iter < 30:
      entry = data[pos:pos+32]
      ret = self.process_root_dir_entry(entry)

      if ret == 0:
        break

      pos += 32
      iter += 1
    ...

  def process_sector(self, content):
    self.jump_code = struct.unpack("<BBB",content[0:3])
    self.identifier = struct.unpack("8s", content[3:11])[0]
    self.bytes_per_sector = struct.unpack("<H", content[11:13])[0]
    self.sector_per_alloc = struct.unpack("<B", content[13:14])[0]
    self.reserved_sectors = struct.unpack("<H", content[14:16])[0]
    self.no_of_fats = struct.unpack("<B", content[16:17])[0]
    self.root_entries = struct.unpack("<H", content[17:19])[0]
    self.total_sectors = struct.unpack("<H", content[19:21])[0]
    self.media_type = struct.unpack("<B", content[21:22])[0]
    self.sectors_per_fat = struct.unpack("<H", content[22:24])[0]
    self.sectors_per_track = struct.unpack("<H", content[24:26])[0]
    self.no_of_heads = struct.unpack("<H", content[26:28])[0]
    self.no_of_hidden_sectors = struct.unpack("<i", content[28:32])[0]
    self.total_sectors_32 = struct.unpack("<i", content[32:36])[0]
    self.drive_id = struct.unpack("<B", content[36:37])[0]
    self.volume_serial_id = struct.unpack(">i", content[39:43])[0]
    self.volume_name = struct.unpack("11s", content[43:54])[0]
    self.fat_type = struct.unpack("8s", content[54:62])[0]

    root_dir_start_sector =  (self.no_of_hidden_sectors +
                              self.reserved_sectors +
                              self.sectors_per_fat *
                              self.no_of_fats)
    root_dir_start = root_dir_start_sector * self.bytes_per_sector

    fat1_start_sector = (self.no_of_hidden_sectors + self.reserved_sectors)
    self.fat1_start_sector = fat1_start_sector
    fat1_start = fat1_start_sector * self.bytes_per_sector

    data_start_sector = (root_dir_start_sector +
                         int((self.root_entries * 32) / self.bytes_per_sector))
    data_start = data_start_sector * self.bytes_per_sector

    print(f"Jumpcode: {self.jump_code} oem: {self.identifier} \n\
    Bytes/sector: {self.bytes_per_sector} Sectors/cluster: {self.sector_per_alloc}\
    Reserved sectors: {self.reserved_sectors} Number of fats: {self.no_of_fats}\n\
    Root entries: {self.root_entries} Total sectors(16): {self.total_sectors}\
    Media type: {self.media_type} {self.media_type:#x} Sectors_per_fat: {self.sectors_per_fat}\
    Sectors_per_track: {self.sectors_per_track} NoHeads: {self.no_of_heads}\n\
    NoHiddenSec: {self.no_of_hidden_sectors} Total sectors: {self.total_sectors_32}\
    Drive_id: {self.drive_id} Volume name: {self.volume_name} Fat type: {self.fat_type}\n\
    fat1_start: {fat1_start} {fat1_start:#x} root_dir_start: {root_dir_start} {root_dir_start:#x}\
    data_start: {data_start} {data_start:#x} datastart sector: {data_start_sector:#x}")

    test = self.cluster_to_sector(0x1c)
    print(f"test cluster num {test} {test:#x}")
    ...

def main():
  with open("fat16.img", mode="rb") as file:
    analyzer = FatAnalyzer(file)
    sector1 = file.read(512)
    analyzer.process_sector(sector1)
    root_dir_start_sector_number = analyzer.find_root_dir_first_sector()
    root_dir_start_offset = root_dir_start_sector_number * analyzer.bytes_per_sector
    file.seek(root_dir_start_offset)
    root_dir_start_sector = file.read(512)
    analyzer.process_root_dir(root_dir_start_sector)

    # elso_txt_start_sector = analyzer.cluster_to_sector(24)
    # file.seek(elso_txt_start_sector * analyzer.bytes_per_sector[0])
    # elso_txt = file.read(analyzer.sector_per_alloc[0]*analyzer.bytes_per_sector[0])
    # elso_txt = analyzer.read_cluster(24)
    # print(elso_txt)
    # analyzer.follow_fat_chain(27)

    # analyzer.read_file(24, 6590)
    analyzer.read_file(6, 36)
    analyzer.read_directory(3)
    analyzer.read_file(7, 3124)

  ...

if __name__ == '__main__':
  main()
  

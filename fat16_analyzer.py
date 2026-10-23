import struct

def read_sector(start_sector1):
  ...

def read_cluster():
  ...

def cluster_to_sector(cluster_num, sectors_per_cluster, data_area_start_cluster):
  retval = data_area_start_cluster + (cluster_num -2) * sectors_per_cluster
  return retval 
  ...

def process_sector(content):
  jump_code = struct.unpack("<BBB",content[0:3])
  identifier = struct.unpack("8c", content[3:11])
  bytes_per_sector = struct.unpack("<H", content[11:13])
  sector_per_alloc = struct.unpack("<B", content[13:14])
  reserved_sectors = struct.unpack("<H", content[14:16])
  no_of_fats = struct.unpack("<B", content[16:17])
  root_entries = struct.unpack("<H", content[17:19])
  total_sectors = struct.unpack("<H", content[19:21])
  media_type = struct.unpack("<B", content[21:22])
  sectors_per_fat = struct.unpack("<H", content[22:24])
  sectors_per_track = struct.unpack("<H", content[24:26])
  no_of_heads = struct.unpack("<H", content[26:28])
  no_of_hidden_sectors = struct.unpack("<i", content[28:32])
  total_sectors_32 = struct.unpack("<i", content[32:36])
  drive_id = struct.unpack("<B", content[36:37])
  volume_serial_id = struct.unpack(">i", content[39:43])
  volume_name = struct.unpack("11c", content[43:54])
  fat_type = struct.unpack("8c", content[54:62])

  root_dir_start_sector =  (no_of_hidden_sectors[0] + reserved_sectors[0] + sectors_per_fat[0] * no_of_fats[0])
  root_dir_start = root_dir_start_sector * bytes_per_sector[0]

  fat1_start_sector = (no_of_hidden_sectors[0] + reserved_sectors[0])
  fat1_start = fat1_start_sector * bytes_per_sector[0]

  data_start_sector = root_dir_start_sector + int((root_entries[0] * 32) / bytes_per_sector[0])
  data_start = data_start_sector * bytes_per_sector[0] 

  print(f"Jumpcode: {jump_code} oem: {identifier} Bytes/sector: {bytes_per_sector} Sectors/cluster: {sector_per_alloc} Reserved sectors: {reserved_sectors} Number of fats: {no_of_fats} Root entries: {root_entries} Total sectors(16): {total_sectors} Media type: {media_type} {media_type[0]:#x} Sectors_per_fat: {sectors_per_fat} Sectors_per_track: {sectors_per_track} NoHeads: {no_of_heads} NoHiddenSec: {no_of_hidden_sectors} Total sectors: {total_sectors_32} Drive_id: {drive_id} Volume name: {volume_name} Fat type: {fat_type} fat1_start: {fat1_start} {fat1_start:#x} root_dir_start: {root_dir_start} {root_dir_start:#x} data_start: {data_start} {data_start:#x} datastart sector: {data_start_sector:#x}")
  
  test = cluster_to_sector(0x1c, sector_per_alloc[0], data_start_sector)
  print(f"test cluster num {test} {test:#x}")
  ...

def main():
  with open("fat.img", mode="rb") as file:
    sector1 = file.read(512)
    process_sector(sector1)

    
  ...

if __name__ == '__main__':
  main()
  

import sys
import struct
from binascii import *

Central_Directory_File_Count = 0
Central_Directory_File_Header_offset = 0
Local_File_Header_offset_list = []

# End of central directory record
def End_of_central_directory_record(zip_path):
    global Central_Directory_File_Header_offset
    global Central_Directory_File_Count
    end_of_central_directory_record_signature = b'\x50\x4b\x05\x06'
    
    print(f'\n# End of central directory record')
    
    try:
        with open(zip_path, 'rb') as f:
            file = f.read()
            position = file.find(end_of_central_directory_record_signature)

            if position == -1:
                print(f"End of central directory record Signature can't find.")
                return  
            f.seek(position)
            
            # End of central directory record Signature
            signature = f.read(4)
            if signature == end_of_central_directory_record_signature:
                edit_signature = ' '.join([signature.hex()[i:i+2] for i in range(0, len(signature.hex()), 2)])
                print(f'File signature (Magic Number): {edit_signature}')
            else:
                print(f'End of central directory record Signature is not valid.')
            
            # End of central directory record Disk number
            disk_number = f.read(2)
            big_endian_disk_number = int.from_bytes(disk_number, byteorder='little')
            print(f'Disk Start Number: {big_endian_disk_number}')
            
            # End of central directory record Disk # w/cd
            disk_wcd = f.read(2)
            big_endian_disk_wcd = int.from_bytes(disk_wcd, byteorder='little')
            print(f'Disk # w/cd: {big_endian_disk_wcd}')
            
            # End of central directory record Disk entries
            disk_enrties = f.read(2)
            big_endian_disk_enrties = int.from_bytes(disk_enrties, byteorder='little')
            print(f'Disk Entry: {big_endian_disk_enrties}')
            
            # End of central directory record Total entries
            total_entries = f.read(2)
            big_endian_total_entries = int.from_bytes(total_entries, byteorder='little')
            Central_Directory_File_Count = int(big_endian_total_entries)
            print(f'Total Entry: {big_endian_total_entries}')
            
            # End of central directory record Central directory size
            directory_size = f.read(4)
            big_endian_directory_size = int.from_bytes(directory_size, byteorder='little')
            print(f'Size of Central Directory: {big_endian_directory_size}')
            
            # End of central directory record Central Header Offset
            central_header_offset = f.read(4)
            big_endian_central_header_offset = int.from_bytes(central_header_offset, byteorder='little')
            print(f'Central Header Offset: {big_endian_central_header_offset}')
            Central_Directory_File_Header_offset = big_endian_central_header_offset

            # End of central directory record Comment len
            comment_len = f.read(2)
            big_endian_comment_len = int.from_bytes(comment_len, byteorder='little')
            if big_endian_comment_len == 0:
                print(f'Comment Length: None')
            else: 
                print(f'Comment Length: {big_endian_comment_len}')
            
    except FileNotFoundError:
        print(f"File {zip_path} can't find.")

# Central Directory File header
def Central_Directory_File_header(zip_path):
    global Central_Directory_File_Header_offset
    global Central_Directory_File_Header_size
    global Local_File_Header
    central_directory_file_head_signature = b'\x50\x4b\x01\x02'
    
    print(f'# Central Directory File header\n')
    
    for i in range(Central_Directory_File_Count):
        print(f'#{i+1}. Central Directory File header')
        try:
            with open(zip_path, 'rb') as f:
                
                f.seek(Central_Directory_File_Header_offset)
                
                # Central Directory File header Signature
                signature = f.read(4)
                if signature == central_directory_file_head_signature:
                    edit_signature = ' '.join([signature.hex()[i:i+2] for i in range(0, len(signature.hex()), 2)])
                    print(f'File signature (Magic Number): {edit_signature}')
                else:
                    print(f'Central Directory File header Signature is not valid.')
                
                # Central Directory File header Version
                version = f.read(2)
                big_endian_version = int.from_bytes(version, byteorder='little')
                print(f'Version made by: {big_endian_version}')
                
                # Central Directory File header Versneed
                versneed = f.read(2)
                big_endian_versneed = int.from_bytes(versneed, byteorder='little')
                print(f'Version needed to extract (minimum): {big_endian_versneed}')
                
                # Central Directory File header Flags
                flag = f.read(2)
                big_endian_flag = int.from_bytes(flag, byteorder='little')
                print(f'Flags: {big_endian_flag}')
                
                # Central Directory File header Compression
                compression = f.read(2)
                big_endian_compression = int.from_bytes(compression, byteorder='little')
                print(f'Compression method: {big_endian_compression}')
                
                # Central Directory File header Moditime / Modidate
                moditime = f.read(2)
                modidate = f.read(2)
                big_endian_moditime = int.from_bytes(moditime, byteorder='little')
                big_endian_modidate = int.from_bytes(modidate, byteorder='little')
                print(f'Moditime/Modidate: {big_endian_moditime}/{big_endian_modidate}')
                    
                # Central Directory File header Crc-32
                crc32 = f.read(4)
                big_endian_crc32 = int.from_bytes(crc32, byteorder='little')
                print(f'CRC-32 CheckSum: {big_endian_crc32}')
                
                # Central Directory File header Compressed size / Uncompressed size
                compressed_size = f.read(4)
                uncompressed_size = f.read(4)
                big_endian_compressed_size = int.from_bytes(compressed_size, byteorder='little')
                big_endian_uncompressed_size = int.from_bytes(uncompressed_size, byteorder='little')
                print(f'Compressed Size/Uncompressed Size: {big_endian_compressed_size}/{big_endian_uncompressed_size}')
                    
                # Central Directory File File name len / Extra field len
                file_name_len = f.read(2)
                extra_field_len = f.read(2)
                big_endian_file_name_len = int.from_bytes(file_name_len, byteorder='little')
                big_endian_extra_field_len = int.from_bytes(extra_field_len, byteorder='little')
                print(f'File Name Length/Extra Field Length: {big_endian_file_name_len}/{big_endian_extra_field_len}')
                
                # Central Directory File header File comment len
                comment_len = f.read(2) 
                big_endian_comment_len = int.from_bytes(comment_len, byteorder='little')
                print(f'File Comment Length: {big_endian_comment_len}')
                
                # Central Directory File header Disk start num
                disk_start_num = f.read(2) 
                big_endian_disk_start_num = int.from_bytes(disk_start_num, byteorder='little')
                print(f'Disk Start Number: {big_endian_disk_start_num}')
                
                # Central Directory File header Internal attr
                internal_attr = f.read(2) 
                big_endian_internal_attr = int.from_bytes(internal_attr, byteorder='little')
                print(f'Internal Attribute: {big_endian_internal_attr}')
                
                # Central Directory File header External attr
                external_attr = f.read(4) 
                big_endian_external_attr = int.from_bytes(external_attr, byteorder='little')
                print(f'External Attribute: {big_endian_external_attr}')
                
                # Central Directory File header Local Header Offset
                Local_File_Header_offset = f.read(4) 
                big_endian_Local_File_Header_offset = int.from_bytes(Local_File_Header_offset, byteorder='little')
                print(f'Local Header: {big_endian_Local_File_Header_offset}')
                
                # Push Local File Header Offset list
                Local_File_Header_offset_list.append(big_endian_Local_File_Header_offset)
                
                # Central Directory File header 
                file_name = f.read(big_endian_file_name_len)
                decode_file_name = file_name.decode('euc-kr', errors='ignore')
                print(f'File Name: {decode_file_name}\n')
                
                Central_Directory_File_Header_size = 46 + int(big_endian_file_name_len) + int(big_endian_extra_field_len) + int(big_endian_comment_len)
                Central_Directory_File_Header_offset = Central_Directory_File_Header_offset + Central_Directory_File_Header_size
                
        except FileNotFoundError:
            print(f"File {zip_path} can't find.")
        
# Local File Header
def Local_File_Header(zip_path):
    global Local_File_Header
    global Local_File_Header_offset_list
    local_file_header_signature = b'\x50\x4b\x03\x04'
    
    print(f'# Local File Header\n')

    for i in range(len(Local_File_Header_offset_list)):
        print(f'#{i+1}. Local File Header')

        try:
            with open(zip_path, 'rb') as f:
                # Local File Header Signature
    
                f.seek(Local_File_Header_offset_list[i])
                signature = f.read(4)
                if signature == local_file_header_signature:
                    edit_signature = ' '.join([signature.hex()[i:i+2] for i in range(0, len(signature.hex()), 2)])
                    print(f'File signature (Magic Number): {edit_signature}')
                else:
                    print(f'Local File Header Signature is not valid.')
                    
                #Local File Header Version
                version = f.read(2)
                big_endian_version = int.from_bytes(version, byteorder='little')
                print(f'Version needed to extract: {big_endian_version}')
                
                #Local File Header Flags
                flag = f.read(2)
                big_endian_flag = int.from_bytes(flag, byteorder='little')
                print(f'Flags: {big_endian_flag}')
                
                # Local File Header Compression
                compression = f.read(2)
                big_endian_compression = int.from_bytes(compression, byteorder='little')
                print(f'Compression method: {big_endian_compression}')
                
                # Local File Header Moditime / Modidate
                moditime = f.read(2)
                modidate = f.read(2)
                big_endian_moditime = int.from_bytes(moditime, byteorder='little')
                big_endian_modidate = int.from_bytes(modidate, byteorder='little')
                print(f'Moditime/Modidate: {big_endian_moditime}/{big_endian_modidate}')
                
                # Local File Header Crc-32
                crc32 = f.read(4)
                big_endian_crc32 = int.from_bytes(crc32, byteorder='little')
                print(f'CRC-32 CheckSum: {big_endian_crc32}')

                # Local File Header Compressed size / Uncompressed size
                compressed_size = f.read(4)
                uncompressed_size = f.read(4)
                big_endian_compressed_size = int.from_bytes(compressed_size, byteorder='little')
                big_endian_uncompressed_size = int.from_bytes(uncompressed_size, byteorder='little')
                print(f'Compressed Size/Uncompressed Size: {big_endian_compressed_size}/{big_endian_uncompressed_size}')
                
                # Local File Header File name len / Extra field len
                file_name_len = f.read(2)
                extra_field_len = f.read(2)
                big_endian_file_name_len = int.from_bytes(file_name_len, byteorder='little')
                big_endian_extra_field_len = int.from_bytes(extra_field_len, byteorder='little')
                print(f'File Name Length/Extra Field Length: {big_endian_file_name_len}/{big_endian_extra_field_len}')
                
                # Local File Header File name 
                file_name = f.read(big_endian_file_name_len)
                decode_file_name = file_name.decode('euc-kr', errors='ignore')
                print(f'File Name: {decode_file_name}\n')
                    
        except FileNotFoundError:
            print(f"File {zip_path} can't find.")

if __name__=='__main__':
    # usage
    if len(sys.argv) != 2:
        print("usage : python ./zip_parse.py ./zip_path")
        sys.exit()

    # zip path
    zip_path = sys.argv[1]

    End_of_central_directory_record(zip_path)
    print('')
    print(f'----------------------------------------------------------')
    print('')
    Central_Directory_File_header(zip_path)
    print('')
    print(f'----------------------------------------------------------')
    print('')
    Local_File_Header(zip_path)

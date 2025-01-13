# import struct
# import argparse
# import os

# def hexdump(bytes):
#     """주어진 바이트 데이터를 16진수 문자열로 변환"""
#     return ' '.join(f'{b:02X}' for b in bytes)

# def print_end_central_directory():
#     """
#     End of central directory record를 분석하여 출력.
#     - ZIP 파일의 끝에 위치하며 압축 파일의 정보를 제공함.
#     - 각 필드를 읽고 적절히 해석하여 출력.
#     - comment_len이 0일 경우 None으로 출력.
#     """
#     print("\n# End of central directory record")
#     disk_start_num = int.from_bytes(file.read(2), byteorder='little')
#     disk_cd = int.from_bytes(file.read(2), byteorder='little')
#     disk_entry = int.from_bytes(file.read(2), byteorder='little')
#     total_entry = int.from_bytes(file.read(2), byteorder='little')
#     size_cd = int.from_bytes(file.read(4), byteorder='little')
#     cd_offset = int.from_bytes(file.read(4), byteorder='little')
#     comment_len = int.from_bytes(file.read(2), byteorder='little')

#     # 주석이 없으면 'None', 있으면 UTF-8로 디코딩 후 출력
#     comment = 'None' if comment_len == 0 else file.read(comment_len).decode('utf-8', errors='ignore')

#     print(f"File signature (Magic Number): 50 4B 05 06")
#     print(f"Disk Start Number: {disk_start_num}")
#     print(f"Disk # w/cd: {disk_cd}")
#     print(f"Disk Entry: {disk_entry}")
#     print(f"Total Entry: {total_entry}")
#     print(f"Size of Central Directory: {size_cd}")
#     print(f"Central Header Offset: {cd_offset}")
#     print(f"Comment Length: {comment_len} ({comment})")

# def decode_filename(data):
#     """
#     파일명을 다양한 인코딩 방식으로 디코딩.
#     - utf-8, cp949, latin1 순으로 시도하여 디코딩.
#     - 디코딩 오류 발생 시 errors='ignore'로 처리.
#     """
#     try:
#         return data.decode('utf-8')
#     except UnicodeDecodeError:
#         try:
#             return data.decode('cp949')  # 한글 파일명에 적합
#         except UnicodeDecodeError:
#             return data.decode('latin1', errors='ignore')  # 최후의 수단

# def save_to_file(filename, data):
#     """
#     주어진 데이터를 파일로 저장하는 함수.
#     - 중앙 디렉토리 헤더의 데이터를 각각 파일로 저장.
#     - 'central_directory' 폴더를 생성한 후 파일별로 저장.
#     """
#     directory = 'central_directory'
#     if not os.path.exists(directory):
#         os.makedirs(directory)
    
#     file_path = os.path.join(directory, f'{filename}.bin')
#     with open(file_path, 'wb') as f:
#         f.write(data)
#     print(f"Saved central directory data to {file_path}")

# def print_central_directory_header(index):
#     """
#     Central Directory File header를 분석하여 출력.
#     - 각 필드를 해석하여 적절히 출력.
#     - 파일명, 압축 정보 등을 포함하여 출력.
#     - 데이터는 파일로 출력.
#     """
#     print(f"\n# {index}. Central Directory File header")
#     version_made_by = int.from_bytes(file.read(2), byteorder='little')
#     version_needed = int.from_bytes(file.read(2), byteorder='little')
#     flags = int.from_bytes(file.read(2), byteorder='little')
#     compression_method = int.from_bytes(file.read(2), byteorder='little')
#     mod_time = int.from_bytes(file.read(2), byteorder='little')
#     mod_date = int.from_bytes(file.read(2), byteorder='little')
#     crc32 = int.from_bytes(file.read(4), byteorder='little')
#     compressed_size = int.from_bytes(file.read(4), byteorder='little')
#     uncompressed_size = int.from_bytes(file.read(4), byteorder='little')
#     fname_len = int.from_bytes(file.read(2), byteorder='little')
#     extra_len = int.from_bytes(file.read(2), byteorder='little')
#     comment_len = int.from_bytes(file.read(2), byteorder='little')
#     disk_start_num = int.from_bytes(file.read(2), byteorder='little')
#     int_attr = int.from_bytes(file.read(2), byteorder='little')
#     ext_attr = int.from_bytes(file.read(4), byteorder='little')
#     local_header_offset = int.from_bytes(file.read(4), byteorder='little')

#     # 파일명을 디코딩 (utf-8, cp949 등 시도)
#     filename = decode_filename(file.read(fname_len))
#     extra_field = file.read(extra_len)  # Extra field 저장
#     comment_field = file.read(comment_len)  # Comment 저장

#     # 중앙 디렉토리 데이터를 파일로 저장
#     save_to_file(f'central_directory_{index}', extra_field + comment_field)

#     print(f"File signature (Magic Number): 50 4B 01 02")
#     print(f"Version made by: {version_made_by}")
#     print(f"Version needed to extract (minimum): {version_needed}")
#     print(f"Flags: {flags}")
#     print(f"Compression method: {compression_method}")
#     print(f"Moditime/Modidate: {mod_time}/{mod_date}")
#     print(f"CRC-32 CheckSum: {crc32}")
#     print(f"Compressed Size/Uncompressed Size: {compressed_size}/{uncompressed_size}")
#     print(f"File Name Length/Extra Field Length: {fname_len}/{extra_len}")
#     print(f"File Comment Length: {comment_len}")
#     print(f"Disk Start Number: {disk_start_num}")
#     print(f"Internal Attribute: {int_attr}")
#     print(f"External Attribute: {ext_attr}")
#     print(f"Local Header: {local_header_offset}")
#     print(f"File Name: {filename}")

# def print_local_file_header(index):
#     """
#     Local File Header를 분석하여 출력.
#     - 파일의 실제 압축 데이터 정보, 파일명 등을 포함하여 출력.
#     """
#     print(f"\n# {index}. Local File Header")
#     version_needed = int.from_bytes(file.read(2), byteorder='little')
#     flags = int.from_bytes(file.read(2), byteorder='little')
#     compression_method = int.from_bytes(file.read(2), byteorder='little')
#     mod_time = int.from_bytes(file.read(2), byteorder='little')
#     mod_date = int.from_bytes(file.read(2), byteorder='little')
#     crc32 = int.from_bytes(file.read(4), byteorder='little')
#     compressed_size = int.from_bytes(file.read(4), byteorder='little')
#     uncompressed_size = int.from_bytes(file.read(4), byteorder='little')
#     fname_len = int.from_bytes(file.read(2), byteorder='little')
#     extra_len = int.from_bytes(file.read(2), byteorder='little')

#     # 파일명을 디코딩 (utf-8, cp949 등 시도)
#     filename = decode_filename(file.read(fname_len))
#     file.read(extra_len)  # 추가 필드 건너뛰기

#     print(f"File signature (Magic Number): 50 4B 03 04")
#     print(f"Version needed to extract: {version_needed}")
#     print(f"Flags: {flags}")
#     print(f"Compression method: {compression_method}")
#     print(f"Moditime/Modidate: {mod_time}/{mod_date}")
#     print(f"CRC-32 CheckSum: {crc32}")
#     print(f"Compressed Size/Uncompressed Size: {compressed_size}/{uncompressed_size}")
#     print(f"File Name Length/Extra Field Length: {fname_len}/{extra_len}")
#     print(f"File Name: {filename}")

# def find_end_of_central_directory():
#     """
#     ZIP 파일의 끝에서 End of central directory record를 찾음.
#     - End of central directory record는 ZIP 파일의 끝에서 22바이트를 기준으로 위치.
#     """
#     file.seek(-22, 2)  # 파일 끝에서 22바이트 앞부터 검색
#     sig = file.read(4)
#     if sig == b'PK\x05\x06':
#         return True
#     else:
#         return False

# def parse_zip_file(file_path):
#     """
#     ZIP 파일을 열고 주요 정보를 분석 및 출력.
#     - End of central directory에서부터 시작하여 Central Directory 정보를 출력.
#     - Local File Header 정보도 출력.
#     """
#     global file
#     file = open(file_path, "rb")
#     index = 0

#     # ZIP 파일의 끝에서 중앙 디렉토리와 끝부분을 찾음
#     if find_end_of_central_directory():
#         print_end_central_directory()

#         # Central Directory의 시작 위치로 이동
#         file.seek(-22, 2)  # 중앙 디렉토리 시작점
#         file.seek(-file.read(4)[0], 1)  # End of central directory로부터 중앙 디렉토리 오프셋으로 이동
#         print("\n----------------------------------------------------------")
#         for i in range(3):  # 3개의 중앙 디렉토리 파일을 처리 (샘플 기준)
#             print_central_directory_header(i)
#         print("\n----------------------------------------------------------")

#         # Local File Header 정보 출력
#         file.seek(0)  # 파일의 시작으로 이동
#         signature = b""
#         while True:
#             signature = file.read(4)

#             if signature == b'PK\x03\x04':
#                 print_local_file_header(index)
#                 index += 1
#             elif signature == b'':  # EOF
#                 break
#             else:
#                 break
#             print()
#     else:
#         print("End of Central Directory not found.")

#     file.close()

# if __name__ == "__main__":
#     # 명령줄 인자를 처리하는 argparse 설정
#     parser = argparse.ArgumentParser(description="ZIP 파일을 분석하여 주요 정보를 출력하는 프로그램")
#     parser.add_argument('file_path', type=str, help="분석할 ZIP 파일 경로")
    
#     # 명령줄 인자로 받은 파일 경로를 읽음
#     args = parser.parse_args()
#     parse_zip_file(args.file_path)



# usage : python ./zip_parse.py ./zip_path

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
import binascii
import sys

def convert_binary_to_hex(data):
    # 바이너리 데이터 -> 16진수 문자열 변환 -> 대문자 변환
    hex_representation = binascii.hexlify(data)
    hex_string = hex_representation.decode('ascii').upper()
    # 두 글자씩 공백으로 구분하여 포맷
    return ' '.join(hex_string[i:i+2] for i in range(0, len(hex_string), 2))

def fetch_bytes(file_path, offset, length):
    with open(file_path, 'rb') as file:
        file.seek(offset)
        return file.read(length)  # 지정된 오프셋부터 길이만큼 데이터 읽어 반환

def locate_vbr(file_path):
    with open(file_path, 'rb') as file:
        content = file.read()

    ntfs_signature = bytearray([0x4E, 0x54, 0x46, 0x53])
    position = content.find(ntfs_signature)

    if position != -1:  # NTFS 시그니처를 검색하여 VBR 시작 위치 반환
        return position - 3
    else:
        raise Exception("VBR not located")

def extract_vbr_details(file_path, vbr_position):
    vbr_content = fetch_bytes(file_path, vbr_position, 512)
    sector_size = int.from_bytes(vbr_content[11:13], byteorder='little')
    cluster_sectors = vbr_content[13]
    mft_start_cluster = int.from_bytes(vbr_content[48:55], byteorder='little')

    # MFT 엔트리 시작 위치를 계산하여 반환
    mft_entry_start = (mft_start_cluster * cluster_sectors * sector_size) + vbr_position

    return sector_size, cluster_sectors, mft_entry_start

def extract_filename(attribute_data, attr_offset):
    name_length = int.from_bytes(attribute_data[4:8], byteorder='little')
    filename_data = attribute_data[attr_offset + 0x5A:attr_offset + name_length + 1]
    null_terminator = filename_data.find(b'\x00\x00')
    filename_data = filename_data[:null_terminator+1]
    filename = filename_data.decode('utf-16-le')

    # 파일 이름의 마지막 문자가 잘못된 경우 제거
    if ord(filename[-1]) < 32 or ord(filename[-1]) > 126:
        filename = filename[:-1]

    return filename

def parse_data_runs(attribute_data, attr_offset, sectors_per_cluster, sector_size, vbr_position):
    runlist_start = int.from_bytes(attribute_data[attr_offset + 0x20:attr_offset + 0x22], byteorder='little')

    run_header = attribute_data[attr_offset + runlist_start]
    run_header_hex = str(hex(run_header))[2:]
    run_length = int(run_header_hex[1])
    run_offset_length = int(run_header_hex[0])

    # Run List에서 클러스터 오프셋 읽어옴
    cluster_offset_bytes = attribute_data[attr_offset + runlist_start + 1 + run_length:attr_offset + runlist_start + 1 + run_length + run_offset_length]
    cluster_offset = int.from_bytes(cluster_offset_bytes, byteorder='little')

    # 실제 데이터 오프셋 계산
    data_offset = (cluster_offset * sectors_per_cluster * sector_size) + vbr_position
    file_length = int.from_bytes(attribute_data[attr_offset + runlist_start - 8:attr_offset + runlist_start], byteorder='little')

    return data_offset, file_length

def main_process(file_path):
    vbr_position = locate_vbr(file_path)  # VBR 위치 찾음
    sector_size, sectors_per_cluster, mft_start = extract_vbr_details(file_path, vbr_position)  # VBR에서 주요 정보를 추출합니다.

    print(f"Sector Size: {sector_size}")
    print(f"Sectors per Cluster: {sectors_per_cluster}")
    print(f"MFT Entry Start: {int(mft_start / sector_size)} sector")
    print("")

    current_mft_offset = mft_start
    mft_record_length = 1024

    record_count = 0

    while True:
        try:
            mft_record = fetch_bytes(file_path, current_mft_offset, mft_record_length)

            record_count += 1
            if record_count > 10000:  # 특정 횟수를 초과하면 루프 종료
                break

            # MFT 엔트리의 시그니처 확인
            if mft_record[:4] != b'FILE':
                current_mft_offset += mft_record_length
                continue

            # 삭제된 파일인지 확인하기 위해 플래그 검사
            if mft_record[22] != 0:
                current_mft_offset += mft_record_length
                continue

            print(f"Deleted File MFT Entry: {int(current_mft_offset / sector_size)} sector")

            # $FILENAME 속성을 검색하여 파일 이름 추출
            filename_attr_pos = mft_record.find(b'\x30\x00\x00\x00')
            if filename_attr_pos != -1:
                filename = extract_filename(mft_record, filename_attr_pos)
                print(f"Deleted Filename: {filename}")

                # $DATA 속성을 검색하여 파일의 위치와 크기 계산
                data_attr_pos = mft_record.find(b'\x80\x00\x00\x00')
                if data_attr_pos != -1:
                    data_offset, data_size = parse_data_runs(
                        mft_record, 
                        data_attr_pos,
                        sectors_per_cluster,
                        sector_size,
                        vbr_position
                    )

                    print(f"File Location: {int(data_offset / sector_size)} sector")
                    print(f"File Size: {data_size} bytes")

                    # 파일 데이터를 읽고 복구
                    recovered_file = fetch_bytes(file_path, data_offset, data_size)
                    output_file = f'recovered_{filename}'
                    with open(output_file, 'wb') as out:
                        out.write(recovered_file)

                    print(f"Recovered File: {output_file}")
                    print("")

            current_mft_offset += mft_record_length

        except Exception as e:
            print(f"Error: {str(e)}")
            current_mft_offset += mft_record_length
            continue

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python ntfs_deleted_file_recovery.py <image_path>")
        sys.exit(1)

    disk_image_path = sys.argv[1]
    main_process(disk_image_path)

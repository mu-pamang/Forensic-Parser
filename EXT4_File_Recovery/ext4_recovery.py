import os
import sys

def analyze_deleted_inodes(inode_data):
    """
    inode table에서 삭제된 inode 정보 분석
    """
    deleted_inodes = []
    for offset in range(0, len(inode_data), 256):  # 256바이트씩 분석
        entry = inode_data[offset:offset + 256]

        file_size = int.from_bytes(entry[4:8], 'little') + (int.from_bytes(entry[0x6C:0x6C + 4], 'little') << 32)
        deletion_time = int.from_bytes(entry[0x14:0x14 + 4], 'little')
        inode_version = int.from_bytes(entry[0x64:0x64 + 4], 'little')
        start_bytes = entry[:4]
        user_id = int.from_bytes(entry[2:4], 'little')

        # 삭제 시간(deletion_time)이 있고, 파일 크기(file_size)가 0이며, UID가 1000인 경우
        if deletion_time != 0 and file_size == 0 and user_id == 0x3E8:
            deleted_inodes.append({
                "inode_version": inode_version,
                "start_bytes": start_bytes,
            })
    return deleted_inodes

# 저널에서 삭제된 파일의 원본 inode 검색

def locate_original_inodes(journal_data, deleted_inodes):
    located_entries = []
    """
    삭제된 inode 목록, journal 데이터에서 원본 inode 엔트리 찾기
    """
    for inode in deleted_inodes:
        inode_version = inode["inode_version"]
        start_bytes = inode["start_bytes"]

        version_bytes = inode_version.to_bytes(4, 'little') #inode 기록 찾기

        for offset in range(0, len(journal_data) - 4, 4):  # 4바이트 단위 비교
            journal_segment = journal_data[offset:offset + 4]

            if journal_segment == version_bytes: # 같은 inode 기록 찾음
                inode_start = offset - 0x64
                entry = journal_data[inode_start:inode_start + 256]

                file_size = int.from_bytes(entry[4:8], 'little') + (int.from_bytes(entry[0x6C:0x6C + 4], 'little') << 32)
                deletion_time = int.from_bytes(entry[0x14:0x14 + 4], 'little')
                inode_version = int.from_bytes(entry[0x64:0x64 + 4], 'little')
                start_bytes_current = entry[:4]

                # depth 조건과 크기, 삭제 상태 확인 (= depth 0 일 때)
                if int.from_bytes(entry[0x2E:0x2E + 2], 'little') != 0:
                    break

                block_addr = int.from_bytes(entry[60:64], 'little')

                # 삭제된 inode와 비교하여 inode의 size가 X, dtime = 0, 첫4바이트 같으면 원본 inode로 식별 
                if file_size != 0 and deletion_time == 0 and start_bytes_current == start_bytes:
                    located_entries.append({
                        "inode_version": inode_version,
                        "journal_offset": offset,
                        "start_bytes": start_bytes_current,
                        "file_size": file_size,
                        "block_addr": block_addr,
                    })
                    break

    return located_entries

def recover_file_from_dd(image_path, output_dir, block_addr, file_size, sector_size=4096):
    """
    dd 이미징에서 삭제 데이터 추출
    """
    offset = block_addr * sector_size  # 섹터 크기로 위치 계산
    output_file_name = f"recovered_{block_addr}.dat"  # 파일명 변경
    output_path = os.path.join(output_dir, output_file_name)

    with open(image_path, "rb") as image:
        image.seek(offset)
        data = image.read(file_size)

    with open(output_path, "wb") as extracted_file:
        extracted_file.write(data)

    print(f"Recovered file saved at: {output_path}")


def main(inode_table_path, journal_path, disk_image_path, recovery_dir):
    """
    메인 함수
    """
    with open(inode_table_path, "rb") as inode_table:
        inode_data = inode_table.read()

    with open(journal_path, "rb") as journal:
        journal_data = journal.read()

    deleted_inodes = analyze_deleted_inodes(inode_data)
    matched_entries = locate_original_inodes(journal_data, deleted_inodes)

    if matched_entries:
        os.makedirs(recovery_dir, exist_ok=True)

        for entry in matched_entries:
            print(f"Located Entry:\n"
                  f"  Inode Version: {entry['inode_version']}\n"
                  f"  Journal Offset: {entry['journal_offset']}\n"
                  f"  Start Bytes: {entry['start_bytes']}\n"
                  f"  File Size: {entry['file_size']}\n"
                  f"  Block Address: {entry['block_addr']}\n")

            recover_file_from_dd(
                image_path=disk_image_path,
                output_dir=recovery_dir,
                block_addr=entry["block_addr"],
                file_size=entry["file_size"]
            )
    else:
        print("No matching entries found.")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python ext4_recovery_tool.py <inode_table> <journal> <disk_image>")
        sys.exit(1)

    inode_table_path = sys.argv[1]
    journal_path = sys.argv[2]
    disk_image_path = sys.argv[3]
    recovery_dir = "./recovered_data"

    main(inode_table_path, journal_path, disk_image_path, recovery_dir)

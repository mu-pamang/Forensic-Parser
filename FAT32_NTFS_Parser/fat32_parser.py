import struct 
import time 
import sys  

SECTOR_SIZE = 512  # FAT32 파일 시스템에서 각 섹터의 크기를 512바이트로 설정

def read_mbr(file):
    """
    파일로부터 MBR(Master Boot Record)을 읽고, 각 파티션 엔트리를 분석하는 함수
    """
    file.seek(0)  # 파일 포인터를 파일 시작 위치로 이동
    mbr = file.read(SECTOR_SIZE)  # MBR 크기만큼 파일을 읽어 `mbr` 변수에 저장
    
    print("\n# MBR") 
    partitions = []  # 유효한 파티션 정보 저장을 위한 리스트 초기화
    
    for i in range(4):  # MBR 내 최대 4개의 파티션 엔트리를 순회
        partition_entry = mbr[446 + i * 16: 446 + (i + 1) * 16]  # 각 파티션 엔트리(16바이트) 읽기
        boot_flag, chs_addr, part_type, end_chs, lba_start, sectors_count = struct.unpack('<B3sB3sII', partition_entry)  # 엔트리 값 해석
        
        if part_type != 0x00:  # 파티션 유형이 0x00이 아닐 때만 유효한 파티션으로 간주
            print(f"\n@ Partition {i}")  # 현재 파티션 번호 출력
            print(f"Boot Flag: 0x{boot_flag:X}")  # 부팅 플래그 출력
            print(f"CHS Addr: 0x{chs_addr.hex()}")  # CHS 주소 출력
            print(f"Starting CHS Addr: 0x{chs_addr.hex()}")  # 시작 CHS 주소 출력
            print(f"Part Type: 0x{part_type:X}")  # 파티션 유형 출력
            print(f"Ending CHS Addr: 0x{end_chs.hex()}")  # 끝 CHS 주소 출력
            print(f"Starting LBA Addr: {lba_start} sector")  # 시작 LBA 주소 출력
            print(f"Size in Sector: 0x{sectors_count:X}")  # 섹터 크기 출력
            partitions.append((i, lba_start))  # 유효한 파티션 정보를 리스트에 추가
    
    print("\n-----MBR Check Complete-----") 
    return partitions  # 유효한 파티션 정보 리스트 반환

def parse_reserved_area(file, start_sector, partition_index):
    """
    파일 시스템의 Reserved Area를 파싱하는 함수
    """
    print(f"\n@ Partition {partition_index}")  # Reserved Area 파싱 시작을 알리는 메시지 출력
    file.seek(start_sector * SECTOR_SIZE)  # Reserved Area 시작 섹터로 파일 포인터 이동
    reserved_area = file.read(SECTOR_SIZE)  # Reserved Area 크기만큼 파일에서 데이터 읽기
    
    jump_boot_code = " ".join([f"{byte:02X}" for byte in reserved_area[:3]])  # Jump Boot Code 읽기
    oem_id = reserved_area[3:11].decode('ascii')  # OEM ID를 ASCII로 변환
    oem_id_hex = " ".join([f"{byte:02X}" for byte in reserved_area[3:11]])  # OEM ID를 16진수 형식으로 변환
    bytes_per_sector = struct.unpack('<H', reserved_area[11:13])[0]  # 섹터당 바이트 수
    sectors_per_cluster = struct.unpack('<B', reserved_area[13:14])[0]  # 클러스터당 섹터 수
    reserved_sectors_count = struct.unpack('<H', reserved_area[14:16])[0]  # 예약 섹터 수
    sectors_per_track = struct.unpack('<H', reserved_area[24:26])[0]  # 트랙당 섹터 수
    fat_size = struct.unpack('<I', reserved_area[36:40])[0]  # FAT 크기
    root_dir_cluster = struct.unpack('<I', reserved_area[44:48])[0]  # 루트 디렉터리 클러스터

    # Reserved Area 정보 출력
    print("\n#Reserved Area")
    print(f"sector: {start_sector}")
    print(f"Jump Boot Code: {jump_boot_code}")
    print(f"OEM ID (str/hex):  {oem_id} / {oem_id_hex}")
    print(f"Bytes Per Sector:  {bytes_per_sector}")
    print(f"Sectors Per Cluster:  0x{sectors_per_cluster:X}")
    print(f"Reserved Sector Count:  0x{reserved_sectors_count:X}")
    print(f"Sector per track:  0x{sectors_per_track:X}")
    print(f"FAT32 Size:  {fat_size}")
    print(f"Root directory cluster offset: {root_dir_cluster} cluster")
    
    return start_sector + reserved_sectors_count, fat_size, sectors_per_cluster, root_dir_cluster

def parse_fsinfo(file, fsinfo_sector):
    """
    파일 시스템의 FSINFO 영역을 파싱하여 클러스터 관련 정보를 추출하는 함수
    """
    file.seek(fsinfo_sector * SECTOR_SIZE)  # FSINFO 영역의 시작 위치로 이동
    fsinfo = file.read(SECTOR_SIZE)  # FSINFO 크기만큼 데이터 읽기
    
    # FSINFO 영역의 서명 및 클러스터 관련 정보 읽기
    signature1 = fsinfo[0:4]
    signature2 = fsinfo[484:488]
    num_free_clusters, next_free_cluster = struct.unpack('<II', fsinfo[488:496])

    try:
        # ASCII 변환 가능한 경우 ASCII 출력
        signature1_ascii = signature1.decode('ascii')
        signature2_ascii = signature2.decode('ascii')
    except UnicodeDecodeError:
        # 변환 불가 시, 16진수 형식으로 출력
        signature1_ascii = "".join([f"\\x{byte:02X}" for byte in signature1])
        signature2_ascii = "".join([f"\\x{byte:02X}" for byte in signature2])

    # FSINFO 정보 출력
    print("\nFSINFO")
    print(f"Signature: b'{signature1_ascii}'")
    print(f"Signature: b'{signature2_ascii}'")
    print(f"Number of free cluster: 0x{num_free_clusters:X}")
    print(f"Next free cluster: 0x{next_free_cluster:X}")

def parse_fat_area(file, fat_start_sector, fat_size):
    """
    FAT Area 정보를 파싱하는 함수
    """
    print("\n# FAT Area")
    print(f"sector (FAT Area #1): {fat_start_sector}")
    print(f"Backup FAT Area (FAT Area #2): {fat_start_sector + fat_size} sector")

    media_type = "f8 ff ff 0f"
    partition_status = "ff ff ff ff"
    
    print(f"Media Type: {media_type}")
    print(f"Partition status: {partition_status}")

def parse_data_area(file, data_start_sector):
    """
    Data Area 정보를 출력하는 함수
    """
    print("\n# Data Area")
    print(f"sector: {data_start_sector}")

def get_file_clusters(file, fat_start_sector, root_dir_cluster, sectors_per_cluster):
    """
    FAT 테이블을 순회하여 파일 클러스터의 위치를 동적으로 식별하는 함수
    """
    file_clusters = []  # 파일 클러스터 위치 저장 리스트 초기화
    cluster = root_dir_cluster  # 첫 클러스터 설정
    fat_offset = fat_start_sector * SECTOR_SIZE  # FAT 오프셋 계산
    
    while cluster < 0x0FFFFFF8:  # FAT32 마지막 클러스터 범위 내에서 순회
        file_clusters.append(cluster)  # 현재 클러스터 추가
        file.seek(fat_offset + cluster * 4)  # 다음 클러스터 위치로 이동
        next_cluster = struct.unpack('<I', file.read(4))[0]  # 다음 클러스터 값 읽기
        if next_cluster >= 0x0FFFFFF8:  # 마지막 클러스터 도달 시 종료
            break
        cluster = next_cluster  # 다음 클러스터로 업데이트
    
    return file_clusters  # 파일 클러스터 리스트 반환

def parse_file_clusters(file, clusters, sectors_per_cluster):
    """
    파일의 각 클러스터 위치 정보를 출력하는 함수
    """
    print("\n# File")
    for i, cluster in enumerate(clusters):
        cluster_location = cluster * sectors_per_cluster * SECTOR_SIZE  # 클러스터 위치 계산
        print(f"{i}. Cluster location: {cluster_location}")

def fat32_parser(file_path):
    """
    FAT32 파일 시스템의 구조를 분석하고, 각 영역의 정보를 출력하는 함수
    """
    start_time = time.time()  # 시작 시간 기록
    with open(file_path, 'rb') as f:  # 파일을 바이너리 읽기 모드로 열기
        partitions = read_mbr(f)  # MBR 분석 및 파티션 정보 추출

        for partition_index, partition_start in partitions:  # 각 유효한 파티션에 대해 반복
            reserved_start_sector, fat_size, sectors_per_cluster, root_dir_cluster = parse_reserved_area(f, partition_start, partition_index)  # Reserved Area 파싱
            parse_fsinfo(f, reserved_start_sector + 1)  # FSINFO 파싱
            parse_fat_area(f, reserved_start_sector, fat_size)  # FAT Area 파싱
            data_start_sector = reserved_start_sector + 2 * fat_size  # Data Area 시작 위치 계산
            parse_data_area(f, data_start_sector)  # Data Area 파싱

            file_clusters = get_file_clusters(f, reserved_start_sector, root_dir_cluster, sectors_per_cluster)  # 파일 클러스터 위치 동적 계산
            parse_file_clusters(f, file_clusters, sectors_per_cluster)  # 파일 클러스터 위치 출력


# 명령 줄 인수를 통해 파일 경로를 받아서 실행
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 FAT32_parser.py <path_to_fat32_image>")  # 사용법 출력
    else:
        fat32_parser(sys.argv[1])  # 파일 경로를 인수로 받아 분석 수행

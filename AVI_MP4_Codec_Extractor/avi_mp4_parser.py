import struct  
import argparse  
import os  
import subprocess  

# ----------------- AVI Parsing -----------------
"""
AVI 파일의 청크를 분석하고, movi 청크에서 H.264 데이터를 추출해
FFmpeg를 사용하여 이미지 프레임으로 변환하는 기능.
"""

def extract_h264_data(file_path, movi_data, output_folder):
    """
    H.264 코덱 데이터를 추출하고 FFmpeg로 이미지를 변환하는 함수
    """
    temp_file = os.path.join(output_folder, "temp_movi_data.h264")  # movi 데이터를 임시 저장할 파일 경로 지정

    # movi 데이터를 임시 파일로 저장
    with open(temp_file, "wb") as f:
        f.write(movi_data)  # 바이너리 형태의 movi 데이터 쓰기

    # FFmpeg 명령어 구성
    output_pattern = os.path.join(output_folder, "frame_%04d.jpg")  # 이미지 출력 파일명 패턴 지정
    command = [
        "ffmpeg",         # FFmpeg 실행 명령
        "-y",             # 기존 출력 파일 덮어쓰기
        "-i", temp_file,  # 입력 파일로 임시 movi 데이터 지정
        output_pattern    # 출력 파일명 패턴 지정
    ]

    print(f"\nExecuting ffmpeg command: {' '.join(command)}")  # 실행 명령 출력
    try:
        subprocess.run(command, check=True)  # FFmpeg 실행
        print(f"Frames extracted to: {output_folder}")  # 성공 메시지 출력
    except subprocess.CalledProcessError as e:  # FFmpeg 실행 중 에러 발생 시 처리
        print(f"Error while running ffmpeg: {e}")  # 에러 메시지 출력
    finally:
        # 임시 파일 삭제
        if os.path.exists(temp_file):  # 파일이 존재할 경우
            os.remove(temp_file)  # 임시 파일 삭제


def parse_avi(file_path):
    """
    AVI 파일의 청크를 분석하고, movi 청크 데이터를 처리하는 함수
    """
    with open(file_path, "rb") as file:  # 바이너리 모드로 AVI 파일 열기
        data = file.read()  # 파일 내용을 모두 읽어 data 변수에 저장

    file_size = len(data)  # 파일 크기 계산
    print("\navi file format")  # 파일 형식 출력
    print(f"\nfile size: {hex(file_size)}")  # 전체 파일 크기 출력
    print(f"file data size: {hex(file_size - 8)}")  # RIFF 헤더 제외 데이터 크기 출력

    # AVI 파일에서 탐지할 청크의 시그니처와 이름 매핑
    chunk_signatures = {
        b'idx1': "idxl",              # 인덱스 청크
        b'strf': "strf",              # 스트림 포맷 청크
        b'avih': "avih",              # AVI 헤더 청크
        b'hdrl': "hdrl",              # 헤더 리스트 청크
        b'JUNK': "JUNK",              # 쓸모없는 데이터
        b'movi': "movi",              # movi: 영상 데이터 포함
        b'INFOISFT': "INFOISFT",      # 소프트웨어 정보 청크
        b'LIST': "stream list",       # stream list 청크
    }

    detected_chunks = []  # 탐지된 청크 정보를 저장할 리스트
    movi_data = None  # movi 청크 데이터 초기화

    # 청크 탐색
    for signature, chunk_name in chunk_signatures.items():  # 각 청크 시그니처 탐색
        offset = 0  # 초기 오프셋 설정
        while offset < file_size:  # 파일 끝까지 탐색
            offset = data.find(signature, offset)  # 현재 오프셋 이후에서 시그니처 찾기
            if offset == -1:  # 시그니처를 찾을 수 없으면 종료
                break

            size_offset = offset + len(signature)  # 청크 크기가 저장된 위치 계산
            if size_offset + 4 <= file_size:       # 파일 크기를 초과하지 않도록 검사
                chunk_size = struct.unpack('<I', data[size_offset:size_offset + 4])[0]  # 청크 크기 읽기
                detected_chunks.append((chunk_name, offset, chunk_size))  # 탐지된 청크 정보 저장
                if chunk_name == "movi":          # movi 청크일 경우
                    movi_data = data[offset + 8:offset + 8 + chunk_size]  # movi 데이터 저장
            offset += 1  # 다음 탐색 위치로 이동

    # 탐지된 청크 정보를 출력
    for chunk_name, offset, chunk_size in sorted(detected_chunks, key=lambda x: x[1]):  # 오프셋 기준 정렬 후 출력
        print(f"\n{chunk_name} start offset: {hex(offset)}")  # 청크 시작 오프셋 출력
        print(f"{chunk_name} size: {hex(chunk_size)}")  # 청크 크기 출력

    # movi 청크 데이터 처리
    if movi_data:
        print("\nExtracting H.264 data from movi chunk...")  # movi 데이터 추출 메시지 출력
        output_folder = os.path.join(os.path.dirname(file_path), "output_frames")  # 출력 폴더 경로 설정
        os.makedirs(output_folder, exist_ok=True)  # 폴더가 없으면 생성
        extract_h264_data(file_path, movi_data, output_folder)  # movi 데이터를 이용한 프레임 추출


# ----------------- MP4 Parsing -----------------
"""
MP4 파일의 박스(box) 구조를 분석하여 각 박스의 시작 위치와 크기를 출력하고,
필요 시 재귀적으로 하위 박스를 탐색하는 기능.
"""

def read_from_file(file, num_bytes):
    """
    파일에서 지정된 크기만큼 데이터를 읽는 함수.
    """
    data = file.read(num_bytes)  # num_bytes만큼 데이터를 읽음
    if len(data) < num_bytes:  # 읽은 데이터가 지정된 크기보다 작으면 EOFError 발생
        raise EOFError(f"Expected {num_bytes} bytes but got {len(data)} bytes")
    return data


def read_box_header(file):
    """
    MP4 박스의 헤더를 읽고, 오프셋, 크기, 타입을 반환하는 함수.
    """
    offset = file.tell()  # 현재 파일 위치(오프셋) 저장
    box_size = struct.unpack(">I", read_from_file(file, 4))[0]  # 박스 크기 읽기
    box_type = read_from_file(file, 4).decode("utf-8")  # 박스 타입(4바이트) 읽기

    if box_size == 1:  # 확장 박스 크기 처리 (64비트 크기)
        box_size = struct.unpack(">Q", read_from_file(file, 8))[0]  # 64비트 크기 읽기

    return offset, box_size, box_type  # 오프셋, 박스 크기, 박스 타입 반환


def process_children(file, end_offset, depth=0):
    """
    MP4 박스의 하위 박스를 재귀적으로 탐색하는 함수.
    """
    while file.tell() < end_offset:  # 탐색 범위 내에서 반복
        offset, box_size, box_type = read_box_header(file)  # 박스 정보 읽기
        print(f"\n{' ' * depth * 4}{box_type} box start offset: {hex(offset)}")  # 박스 시작 오프셋 출력
        print(f"{' ' * depth * 4}{box_type} box size: {hex(box_size)}")  # 박스 크기 출력

        if box_type in ["moov", "trak", "mdia", "minf", "stbl", "dinf"]:  # 하위 박스를 재귀적으로 탐색할 경우
            process_children(file, offset + box_size, depth + 1)  # 재귀 호출
        else:
            file.seek(offset + box_size)  # 현재 박스를 건너뛰고 다음으로 이동


def parse_mp4(file_path):
    """
    MP4 파일을 분석하여 박스 구조를 탐색하는 함수.
    """
    with open(file_path, "rb") as file:  # 바이너리 모드로 MP4 파일 열기
        print("\nmp4 file format\n")  # 파일 형식 출력
        print("-" * 30)
        print("\n# Offset info")
        try:
            while True:
                offset, box_size, box_type = read_box_header(file)  # 상위 박스 정보 읽기
                print(f"\n{box_type} box start offset: {hex(offset)}")  # 박스 시작 오프셋 출력
                print(f"{box_type} box size: {hex(box_size)}")  # 박스 크기 출력

                if box_type in ["moov", "trak", "mdia", "minf", "stbl", "dinf"]:  # 재귀 탐색 대상 박스
                    process_children(file, offset + box_size, depth=1)  # 하위 박스 탐색
                else:
                    file.seek(offset + box_size)  # 다음 박스로 이동
        except EOFError:  # 파일 끝에 도달했을 때 예외 처리
            pass


# ----------------- Main Function -----------------
"""
입력된 파일의 확장자에 따라 AVI 파일과 MP4 파일 분석을 선택적으로 수행.
"""
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse AVI or MP4 files.")  # 명령줄 인자 처리
    parser.add_argument("file_path", type=str, help="Path to the AVI or MP4 file.")  # 입력 파일 경로 인자
    args = parser.parse_args()

    # 파일 확장자에 따라 적절한 분석 함수 호출
    file_extension = os.path.splitext(args.file_path)[-1].lower()  # 파일 확장자 소문자로 추출
    if file_extension == ".avi":  # AVI 파일일 경우
        parse_avi(args.file_path)  # AVI 분석 함수 호출
    elif file_extension == ".mp4":  # MP4 파일일 경우
        parse_mp4(args.file_path)  # MP4 분석 함수 호출
    else:
        print("Unsupported file format. Please provide an AVI or MP4 file.")  # 지원하지 않는 파일 포맷 처리

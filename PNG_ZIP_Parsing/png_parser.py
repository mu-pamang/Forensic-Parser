import struct
import argparse
import os

def save_chunk_to_file(chunk_type, chunk_data, index):
    """청크 데이터를 파일로 저장하는 함수"""
    directory = "chunks_output"
    if not os.path.exists(directory):
        os.makedirs(directory)
    
    file_path = os.path.join(directory, f"chunk_{index}_{chunk_type}.bin")
    with open(file_path, 'wb') as chunk_file:
        chunk_file.write(chunk_data)
    
    print(f"Saved chunk {chunk_type} to {file_path}")

def read_png(file_path):
    """ PNG 파일을 읽고 주요 구조를 분석하며, 청크 데이터를 파일로 출력 """
    with open(file_path, 'rb') as f:
        # 파일 헤더 읽기
        signature = f.read(8)
        print(f"# File Header signature (Magic Number)")
        print(f"{' '.join(f'{b:02X}' for b in signature)}\n")
        
        chunk_list = []  # Chunk list 저장
        index = 0  # 청크 인덱스
        
        while True:
            # 청크 헤더 읽기 (Length, Chunk Type)
            chunk_header = f.read(8)
            if len(chunk_header) < 8:
                break  # 파일 끝 도달
            
            length, chunk_type = struct.unpack('>I4s', chunk_header)
            chunk_type_str = chunk_type.decode('ascii')
            chunk_list.append(chunk_type)  # 청크 타입 저장
            
            # 청크 데이터를 읽음
            chunk_data = f.read(length)
            
            # 청크 데이터를 파일로 저장
            save_chunk_to_file(chunk_type_str, chunk_data, index)
            index += 1  # 인덱스 증가
            
            # IHDR 청크일 경우 정보 출력
            if chunk_type_str == 'IHDR':
                width, height, bit_depth, color_type, comp_method, filter_method, interlace_method = struct.unpack('>IIBBBBB', chunk_data)
                print(f"# IHDR info\nWidth:  {width}\nHeight:  {height}\nBit depth:  {bit_depth}")
                color_type_str = {0: "Grayscale", 2: "RGB", 3: "Indexed Color", 4: "Grayscale with alpha", 6: "RGB with alpha"}
                print(f"Color Type:  {color_type} ({color_type_str.get(color_type, 'Unknown')})")
                print(f"Compression method: {comp_method}\nFilter method:  {filter_method}\nInterlace method:  {interlace_method}\n")
            
            # CRC 값 읽기
            crc = f.read(4)
        
        # Chunk list 출력
        print(f"# Chunk list")
        print([f"b'{chunk.decode()}'" for chunk in chunk_list])
        
        # 파일 푸터 출력
        print(f"# File Footer signature")
        print(f"{' '.join(f'{b:02X}' for b in crc)}\n")
        
        print("Chunk 영역 추출 완료.\n프로그램 종료.")

if __name__ == "__main__":
    # 명령줄 인자를 처리하는 argparse 설정
    parser = argparse.ArgumentParser(description="PNG 파일을 분석하여 주요 정보를 출력하는 프로그램")
    parser.add_argument('file_path', type=str, help="분석할 PNG 파일 경로")
    
    # 명령줄 인자로 받은 파일 경로를 읽음
    args = parser.parse_args()
    read_png(args.file_path)

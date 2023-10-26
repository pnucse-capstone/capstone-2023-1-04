import pickle
import os

#알파벳 단위로 끊어서 변환해야 하는 경우를 위해, 모든 알파벳을 db에 추가
class AlphabetMaker:
    def __init__(self):
        self.data = [
            ('에이', '외래어', '어휘', None, '에이', None, '일반어', '명사', 'A', None),
            ('에이', '외래어', '어휘', None, '에이', None, '일반어', '명사', 'a', None),
            ('비', '외래어', '어휘', None, '비', None, '일반어', '명사', 'B', None),
            ('비', '외래어', '어휘', None, '비', None, '일반어', '명사', 'b', None),
            ('시', '외래어', '어휘', None, '시', None, '일반어', '명사', 'C', None),
            ('시', '외래어', '어휘', None, '시', None, '일반어', '명사', 'c', None),
            ('디', '외래어', '어휘', None, '디', None, '일반어', '명사', 'D', None),
            ('디', '외래어', '어휘', None, '디', None, '일반어', '명사', 'd', None),
            ('이', '외래어', '어휘', None, '이', None, '일반어', '명사', 'E', None),
            ('이', '외래어', '어휘', None, '이', None, '일반어', '명사', 'e', None),
            ('에프', '외래어', '어휘', None, '에프', None, '일반어', '명사', 'F', None),
            ('에프', '외래어', '어휘', None, '에프', None, '일반어', '명사', 'f', None),
            ('지', '외래어', '어휘', None, '지', None, '일반어', '명사', 'G', None),
            ('지', '외래어', '어휘', None, '지', None, '일반어', '명사', 'g', None),
            ('에이치', '외래어', '어휘', None, '에이치', None, '일반어', '명사', 'H', None),
            ('에이치', '외래어', '어휘', None, '에이치', None, '일반어', '명사', 'h', None),
            ('아이', '외래어', '어휘', None, '아이', None, '일반어', '명사', 'I', None),
            ('아이', '외래어', '어휘', None, '아이', None, '일반어', '명사', 'i', None),
            ('제이', '외래어', '어휘', None, '제이', None, '일반어', '명사', 'J', None),
            ('제이', '외래어', '어휘', None, '제이', None, '일반어', '명사', 'j', None),
            ('케이', '외래어', '어휘', None, '케이', None, '일반어', '명사', 'K', None),
            ('케이', '외래어', '어휘', None, '케이', None, '일반어', '명사', 'k', None),
            ('엘', '외래어', '어휘', None, '엘', None, '일반어', '명사', 'L', None),
            ('엘', '외래어', '어휘', None, '엘', None, '일반어', '명사', 'l', None),
            ('엠', '외래어', '어휘', None, '엠', None, '일반어', '명사', 'M', None),
            ('엠', '외래어', '어휘', None, '엠', None, '일반어', '명사', 'm', None),
            ('엔', '외래어', '어휘', None, '엔', None, '일반어', '명사', 'N', None),
            ('엔', '외래어', '어휘', None, '엔', None, '일반어', '명사', 'n', None),
            ('오', '외래어', '어휘', None, '오', None, '일반어', '명사', 'O', None),
            ('오', '외래어', '어휘', None, '오', None, '일반어', '명사', 'o', None),
            ('피', '외래어', '어휘', None, '피', None, '일반어', '명사', 'P', None),
            ('피', '외래어', '어휘', None, '피', None, '일반어', '명사', 'p', None),
            ('큐', '외래어', '어휘', None, '큐', None, '일반어', '명사', 'Q', None),
            ('큐', '외래어', '어휘', None, '큐', None, '일반어', '명사', 'q', None),
            ('알', '외래어', '어휘', None, '알', None, '일반어', '명사', 'R', None),
            ('알', '외래어', '어휘', None, '알', None, '일반어', '명사', 'r', None),
            ('에스', '외래어', '어휘', None, '에스', None, '일반어', '명사', 'S', None),
            ('에스', '외래어', '어휘', None, '에스', None, '일반어', '명사', 's', None),
            ('티', '외래어', '어휘', None, '티', None, '일반어', '명사', 'T', None),
            ('티', '외래어', '어휘', None, '티', None, '일반어', '명사', 't', None),
            ('유', '외래어', '어휘', None, '유', None, '일반어', '명사', 'U', None),
            ('유', '외래어', '어휘', None, '유', None, '일반어', '명사', 'u', None),
            ('브이', '외래어', '어휘', None, '브이', None, '일반어', '명사', 'V', None),
            ('브이', '외래어', '어휘', None, '브이', None, '일반어', '명사', 'v', None),
            ('더블유', '외래어', '어휘', None, '더블유', None, '일반어', '명사', 'W', None),
            ('더블유', '외래어', '어휘', None, '더블유', None, '일반어', '명사', 'w', None),
            ('엑스', '외래어', '어휘', None, '엑스', None, '일반어', '명사', 'X', None),
            ('엑스', '외래어', '어휘', None, '엑스', None, '일반어', '명사', 'x', None),
            ('와이', '외래어', '어휘', None, '와이', None, '일반어', '명사', 'Y', None),
            ('와이', '외래어', '어휘', None, '와이', None, '일반어', '명사', 'y', None),
            ('지', '외래어', '어휘', None, '지', None, '일반어', '명사', 'Z', None),
            ('지', '외래어', '어휘', None, '지', None, '일반어', '명사', 'z', None),
        ]

def main():
    output_path = 'data/processed/dictionary'
    os.makedirs(output_path, exist_ok=True)
    output_file = os.path.join(output_path, 'alphabet_dict.pkl')

    with open(output_file, 'wb') as file:
        pickle.dump(AlphabetMaker().data, file)

    print(f"{output_file} 파일에 데이터가 저장되었습니다.")

if __name__ == "__main__":
    main()
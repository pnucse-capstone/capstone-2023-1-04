import json
import os
from typing import List, Dict
import re
import pickle

class IpaMakerByJson:

    def __init__(self):
        self.ipa = ipa_to_kor()

    def make_dict_word_item_list(self, raw_json_dir_path: str) -> List[Dict]:
        print(f'ipa_raw_json_dir_path: {raw_json_dir_path}')
        if not os.path.exists(raw_json_dir_path):
            os.makedirs(raw_json_dir_path, exist_ok=True)
            raise Exception(f'ERR - ipa_raw_json_dir_path: {raw_json_dir_path}')

        raw_json_files = [x for x in os.listdir(raw_json_dir_path) if '.json' in x]
        print(f'ipa_raw_json_files.size: {len(raw_json_files)}')

        raw_word_item_list = []
        for f_idx, file_name in enumerate(raw_json_files):
            print(f'f_idx: {f_idx}, file_name: {file_name}')
            root_data = None
            with open(os.path.join(raw_json_dir_path, file_name), mode='r', encoding='utf-8') as f:
                root_data = json.load(f)

            ipa_dict_bundle = root_data["en_US"][0]
            ipa_list = []
            for idx, (key, value) in enumerate(ipa_dict_bundle.items()):
                txt = f"{key} {value}"
                txt = self.ipa.process_line(txt)
                txt_index = str(txt).index('/')
                txt_value = txt[txt_index:].strip()
                txt_key = txt[:txt_index].strip()
                txt_val_list = str(txt_value).replace(" ","").split(',')
                for txt_val in  txt_val_list:
                    txt_val_single = {"word": txt_key, "pronun": str(txt_val).replace("/","")}
                    ipa_list.append(txt_val_single)

            return ipa_list
        


class ipa_to_kor:
    def __init__(self):
        self.CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
        self.JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
        self.JONGSUNG_LIST = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    # 한글 자모 분리
    def _decompose_char(self, char):
        # 합쳐진 한글과 '가' 사이 유니코드 차이 계산
        uni = ord(char) - ord('가')
        # 초성 분리
        choseong = (uni // 28) // 21
        # 중성 분리
        jungseong = (uni // 28) % 21
        # 종성 분리
        jongseong = uni % 28
        return choseong, jungseong, jongseong
    

    # 초성이 'ㅇ'인 경우
    def has_choseong_ㅇ(self, char):
        choseong, _, _ = self._decompose_char(char)
        return self.CHOSUNG_LIST[choseong] == 'ㅇ'
    
    # 초성에 'ㅇ'을 다른 자음으로 변경
    def change_choseong(self, char, new_choseong):
        choseong, jungseong, jongseong = self._decompose_char(char)
        choseong = self.CHOSUNG_LIST.index(new_choseong)
        new_uni = choseong * 21 * 28 + jungseong * 28 + jongseong
        return chr(ord('가') + new_uni)
    
    # 종성이 비어 있는 경우
    def has_jongseong_empty(self, char):
        _, _, jongseong = self._decompose_char(char)
        return jongseong == 0
    
    # 종성에 다른 자음을 추가
    def change_jongseong(self, char, new_jongseong):
        choseong, jungseong, _ = self._decompose_char(char)
        jongseong = self.JONGSUNG_LIST.index(new_jongseong)
        new_uni = choseong * 21 * 28 + jungseong * 28 + jongseong
        return chr(ord('가') + new_uni)

    # 최종 string 에 단도 자음 발생 시 대처
    def add_u(self, result):
        modified_result = []
        for i in range(len(result)):
            if result[i] == 'ㄴ':
                modified_result.append('느')
            elif result[i] == 'ㄹ':
                modified_result.append('르')
            elif result[i] == 'ㅁ':
                modified_result.append('므')
            else:
                modified_result.append(result[i])

        result_with_u = ''.join(modified_result)
        return result_with_u


    # 자음 단독 사용을 방지하기 위해 연음 적용
    def liaison_result(self, result):
        while True:
            modified = False

            # result에 대해 한글자 씩 체크
            for i in range(len(result) - 1):
                # 현재 글자가 단독으로 쓰인 자음이고 다음 글자가 초성 'ㅇ'으로 시작하는 경우
                if result[i] in self.CHOSUNG_LIST and result[i+1] not in self.CHOSUNG_LIST and result[i+1] not in self.JUNGSUNG_LIST and self.has_choseong_ㅇ(result[i + 1]):
                    # 현재 자음을 다음 글자의 초성으로 바꾸고 현재 위치의 자음은 제거
                    new_char = self.change_choseong(result[i + 1], result[i])
                    result = result[:i] + new_char + result[i + 2:]
                    modified = True
                    break

                # 현재 글자가 단독으로 쓰인 자음이고 그 앞에 문자의 종성이 없는 경우
                elif i > 0 and result[i] in self.CHOSUNG_LIST and result[i-1] not in self.CHOSUNG_LIST and result[i-1] not in self.JUNGSUNG_LIST and self.has_jongseong_empty(result[i - 1]):
                    # 현재 자음을 앞 글자의 종성으로 바꾸고 현재 위치의 자음은 제거
                    new_char = self.change_jongseong(result[i - 1], result[i])
                    result = result[:i - 1] + new_char + result[i + 1:]
                    modified = True
                    break

            # 현재 글자가 마지막 위치에 있고 단독으로 쓰인 자음이며 그 앞에 문자의 종성이 없는 경우
            if len(result) > 1 and result[-1] in self.CHOSUNG_LIST and self.has_jongseong_empty(result[-2]):
                new_char = self.change_jongseong(result[-2], result[-1])
                result = result[:-2] + new_char
                modified = True

            # 단독 문자가 없을 시 종료
            if not modified:
                break

        return result


    # IPA 발음과 한글 매칭
    def ipa_to_hangeul(self, ipa_string):
        
        # 규칙 기반 발음 변환
        rule = {
            # 외래어 표기법 제 3장 표기세칙 제 1절 영어의 표기 제 9항 1호
            'wə' : '워', 'wɔ' : '워', 'wou' : '워', 'wα' : '와', 
            'wæ' : '왜', 'we' : '웨', 'wi' : '위', 'wu' : '우',
            # 반모음+ # 10/16 추가
            'ja': '야', 'jɑ': '야', 'jʌ': '여', 'jo': '요', 'ju': '유',
            'jɛ': '얘', 'je': '예', 'wɛ': '왜',  'wʌ': '워', 'ɥi': '위',

            # 외래어 표기법 제 3장 표기세칙 제 1절 영어의 표기 제 9항 2호
            'ɡw':'구', 'hw': '후', 'kw': '쿠',

            # 외래어 표기법 제 3장 표기세칙 제 1절 영어의 표기 제 9항 3호
            'djə':'디어',
            'ljə': '리어',
            'njə': '니어'

        }


        # 자음 발음 변환
        consonants = {
            # 두 글자로 이루어진 IPA 자음 발음 우선 변환
            'ts': ['ㅊ', '츠'], 'dz': ['ㅈ', '즈'], 'tʃ': ['ㅊ', '치'], 'dʒ': ['ㅈ', '지'],

            # 나머지 자음
            'p': ['ㅍ', '프'], 'b': ['ㅂ', '브'], 't': ['ㅌ', '트'], 'd': ['ㄷ', '드'], 'k': ['ㅋ', '크'],
            'ɡ': ['ㄱ', '그'], 'f': ['ㅍ', '프'], 'v': ['ㅂ', '브'], 'θ': ['ㅅ', '스'], 'ð': ['ㄷ', '드'],
            's': ['ㅅ', '스'], 'z': ['ㅈ', '즈'], 'ʃ': ['시', '슈'], 'ʒ': ['ㅈ', '지'], 'm': ['ㅁ', 'ㅁ'],
            'n': ['ㄴ', 'ㄴ'], 'ɲ': ['니', '뉴'], 'ŋ': ['ㅇ', 'ㅇ'], 'ɫ': ['ㄹ', 'ㄹ'], 'ɹ': ['ㄹ', '르'],
            'h': ['ㅎ', '흐'], 'ç': ['ㅎ', '히'], 'x': ['ㅎ', '흐']
        }

        # 모음, 반모음 발음 변환
        vowels = {
            # 반모음
            'j': '이', 'ɥ': '위', 'w': '오',
            
            # 모음
            'i': '이', 'ɪ': '이', 'y': '위', 'e': '에', 'ø': '외', 'ɛ': '에', 'ɛ̃': '앵', 'ɝ': '어', 'œ': '외',
            'œ̃': '욍', 'æ': '애', 'a': '아', 'ɑ': '아', 'ã': '앙', 'ʌ': '어', 'ɔ': '오', 'ɔ̃': '옹', 'o': '오',
            'u': '우', 'ʊ': '우', 'ə': '어', 'ɚ': '어'
        }

        result = ''
        index = 0
        ipa_string = ipa_string.replace('ˈ', '').replace('ˌ', '')

        while index < len(ipa_string):
            is_matched = False

            # 규칙 기반 매칭
            if not is_matched:
                for k, v in rule.items():
                    if ipa_string.startswith(k, index):
                        result += v
                        index += len(k)
                        is_matched = True
                        break

            # 자음 매칭
            if not is_matched:
                for k, v in consonants.items():
                    if ipa_string.startswith(k, index):
                        next_index = index + len(k)
                        # 모음 앞에서는 v[0]를 사용
                        if next_index < len(ipa_string) and any(ipa_string[next_index:].startswith(vowel) for vowel in vowels.keys()):
                            result += v[0]
                        # 모음 앞이 아닐 때(자음 앞 또는 어말) v[1]를 사용
                        else:
                            result += v[1]
                        index += len(k)
                        is_matched = True
                        break

            # 모음, 반모음 매칭
            if not is_matched:
                for k, v in vowels.items():
                    if ipa_string.startswith(k, index):
                        result += v
                        index += len(k)
                        is_matched = True
                        break

            if not is_matched:
                result += ipa_string[index]
                index += 1
        return result


    def process_line(self, line):
        # /, / 사이의 IPA 발음 변환
        ipa_pron = re.findall(r'/(.*?)/', line)

        for word in ipa_pron:
            converted_word = self.liaison_result(self.ipa_to_hangeul(word))
            converted_word = self.add_u(converted_word)
            line = line.replace(f'/{word}/', f'/{converted_word}/')

        return line


    def converter(self, input_file_path, output_file_path):
        with open(input_file_path, 'r', encoding='utf-8') as infile:
            lines = infile.readlines()
        processed_lines = [self.process_line(line) for line in lines]
        with open(output_file_path, 'w', encoding='utf-8') as outfile:
            outfile.writelines(processed_lines)


def main():
    ipa_path = 'data/raw/ipa'
    ipa_pickle_path = 'data/processed/dictionary'

    if not os.path.exists(ipa_pickle_path):
        os.makedirs(ipa_pickle_path, exist_ok=True)
        raise Exception(f'ERR - pickle_dir_path: {ipa_pickle_path}')

    ipa_list = IpaMakerByJson().make_dict_word_item_list(ipa_path)
    with open(os.path.join(ipa_pickle_path, "ipa_dict.pickle"), 'wb') as f:
        pickle.dump(ipa_list, f)

    ipa = ipa_to_kor()
    print(ipa.liaison_result(ipa.ipa_to_hangeul("sns*")))

if __name__ == "__main__":
    main()


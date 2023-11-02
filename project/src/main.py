import ast
import re

import Levenshtein
import numpy as np

from database.db_manager import DatabaseManager
from transformer_architecture import predict
from transformer_architecture.make_vocab import tokenizer_kor



# 경로
ENG_DB_PATH = 'data/database/eng_database.db'
IPA_DB_PATH = 'data/database/ipa_database.db'
ALPHABET_DB_PATH = 'data/database/alphabet_database.db'


class IPACompareWithUrimal:
    def __init__(self):
        self.db_manager_ipa = DatabaseManager(IPA_DB_PATH)
        self.db_manager_eng = DatabaseManager(ENG_DB_PATH)
        self.total_count = 0

    def word_pronunciation(self, words):
        # Check in 우리샘사전 DB
        if self.db_manager_eng.check_word_existence(words):
            # print("우리샘사전 DB\n")
            self.total_count += 1
            return self.db_manager_eng.check_word_existence(words)[5]
        else:
            return None

    def sentence_pronunciation_loneword(self, txt):
        pattern = re.compile(r'[a-zA-Z.]+')
        pattern_korean = re.compile(r'[가-힣ㄱ-ㅎ]+')
        is_exist = pattern.search(txt)
        is_exist_korean = pattern_korean.search(txt)
        if(is_exist):
            sentences = is_exist.group()
            pronun = self.word_pronunciation(sentences)
            if pronun:
                return dict({"IPA_Words": sentences, "IPA_Pronun": is_exist_korean.group(), "Uri_Pronun": pronun})
        return None

    def words_pronunciation(self, words):
        # Check in 우리샘사전 DB
        list_words = self.db_manager_eng.check_words_existence(words)
        return list_words

    def words_pronunciation_ipa(self, words):
        # Check in ipa사전 DB
        list_words = self.db_manager_ipa.check_words_existence(words)
        return list_words


class TextPronunciation:
    def __init__(self):
        self.db_manager_ipa = DatabaseManager(IPA_DB_PATH)
        self.db_manager_eng = DatabaseManager(ENG_DB_PATH)
        self.db_manager_alp = DatabaseManager(ALPHABET_DB_PATH)

        self.total_count = 0
        self.single_alphabet_count = 0
        self.our_sam_database_count = 0
        self.ipa_database_count = 0
        self.upper_case_count = 0
        self.no_result_count = 0

    def get_pronunciation(self, word, db_manager):
        char_list_pronun = [db_manager.check_word_existence(char)[
            5] for char in word]
        return ''.join(char_list_pronun)

    def word_pronunciation(self, word):
        word_str = str(word)
        self.total_count += 1  # Increment the word count each time this method is called
        # Single alphabet case
        if len(word_str) == 1 and word_str.isalpha() and word_str.isascii():
            self.single_alphabet_count += 1
            return self.get_pronunciation(word, self.db_manager_alp)

        # Check in 우리샘사전 DB
        if self.db_manager_eng.check_word_existence(word):
            self.our_sam_database_count += 1
            return self.db_manager_eng.check_word_existence(word)[5]

        # Check in IPA DB
        elif self.db_manager_ipa.check_word_existence(word):
            self.ipa_database_count += 1
            return self.db_manager_ipa.check_word_existence(word)[5]

        # All uppercase case
        elif word_str.isupper():
            self.upper_case_count += 1
            return self.get_pronunciation(word, self.db_manager_alp)

        # 딥러닝 case
        else:
            if word_str.find('\'') == -1:
                pass
            else:
                word_str = word_str.replace("'", "") 
            self.no_result_count += 1
            result = predict.single_predict(word_str)
            if bool(re.search(r'[^ㄱ-ㅎ가-힣]', result)):
                str_result = ""
                for char in result:
                    str_result += self.get_pronunciation(char, self.db_manager_alp)
                return str_result   
            else: 
                return result


    def sentence_pronunciation(self, txt):
        pattern = re.compile(r'[a-zA-Z\']+')
        sentences = pattern.findall(txt)
        for value in sentences:
            txt = txt.replace(value, self.word_pronunciation(value), 1)
        return txt



def eng_to_kor_translation(self, str):
    predic = self.model.predict([[self.ENGLISH2IDX.get(char, 0) for char in str] + [0] * (self.max_len_src - len(str))])
    _idx2korean = [np.argmax(val) for val in predic[0]]
    return [self.IDX2KOREAN[idx] for idx in _idx2korean if idx != 0]


@staticmethod
# 자음, 모음으로 이루어진 한글 합치기
def combine_korean_characters(characters):
    # 초성, 중성, 종성 리스트
    cho = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
    jung = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ']
    jong = ['', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']

    idx = 0
    while idx < len(characters) - 2:
        if characters[idx] in jung and characters[idx+1] in cho and characters[idx+2] in jung:
            characters.insert(idx+1, '')
            idx += 2
        else:
            idx += 1
            
    result = []
    idx = 0
    while idx < len(characters):
        c = characters[idx]
        # c가 초성인 경우
        if c in cho:
            # 현재 문자와 다음 두 문자를 조합하여 한글 문자 생성
            try:
                a = cho.index(c)
                b = jung.index(characters[idx+1])
                c = jong.index(characters[idx+2])
                combined_char = chr(a * 21 * 28 + b * 28 + c + 0xAC00)
                result.append(combined_char)
                idx += 3
            except (IndexError, ValueError):  # 다음 문자가 없거나 종성이 없는 경우
                try:
                    a = cho.index(c)
                    b = jung.index(characters[idx+1])
                    combined_char = chr(a * 21 * 28 + b * 28 + 0xAC00)
                    result.append(combined_char)
                    idx += 2
                except (IndexError, ValueError):  # 다음 문자가 없는 경우
                    result.append(c)
                    idx += 1
        else:
            result.append(c)
            idx += 1

    return ''.join(result)


# 딕셔너리로 변환하는 함수
def parse_line(line):
    return ast.literal_eval(line)

def decompose_hangul(s):
    # 각 한글 음절의 유니코드 범위
    SBASE, LBASE, VBASE, TBASE = 0xAC00, 0x1100, 0x1161, 0x11A7
    LCOUNT, VCOUNT, TCOUNT = 19, 21, 28
    NCOUNT = VCOUNT * TCOUNT  # 자음 개수 * 모음 개수
    result = []
    for c in s:
        if '가' <= c <= '힣':
            offset = ord(c) - SBASE
            l = offset // NCOUNT  # 초성 인덱스
            v = (offset % NCOUNT) // TCOUNT  # 중성 인덱스
            t = (offset % TCOUNT)  # 종성 인덱스
            result.extend([chr(LBASE + l), chr(VBASE + v),
                          chr(TBASE + t) if t > 0 else ''])
        else:
            result.append(c)
    return result

# Levenshtein Distance
def jamo_edit_distance(str1, str2):
    distance = Levenshtein.distance(str1,str2)
    return distance

def calculate_accuracy(true_labels, predicted_labels):
    correct = 0
    error_acceptance = 0
    total = len(true_labels)
    for true_label, predicted_label in zip(true_labels, predicted_labels):
        # 자모 edit distance를 사용하여 레이블 간의 거리 계산
        distance = jamo_edit_distance(true_label, predicted_label)
        # 거리가 0이면 정확하게 예측한 경우
        if distance == 0:
            correct += 1
        elif distance == 1:
            error_acceptance += 1

    if error_acceptance == 1:
        accuracy = (correct + 1) / total
    else:
        accuracy = correct / total
    return accuracy


def compare(INPUT_SOURCE_PATH, OUTPUT_SOURCE_PATH):
    accuracy = 0
    total = 0
    with open(INPUT_SOURCE_PATH, 'r', encoding='utf-8') as infile:
        sentences_src = infile.readlines()

    with open(OUTPUT_SOURCE_PATH, 'r', encoding='utf-8') as infile:
        sentences_trg = infile.readlines()
        
    for idx, val in enumerate(sentences_src):
        total += 1
        accuracy += calculate_accuracy(val.replace(" ", ""),sentences_trg[idx].replace(" ", ""))
    return accuracy / total

if __name__ == '__main__':
    text_pronunciation = TextPronunciation()
    while(True):
        output_sentence = input("텍스트를 입력하세요: ")
        transformed_sentence = text_pronunciation.sentence_pronunciation(output_sentence.strip())
        print(transformed_sentence)

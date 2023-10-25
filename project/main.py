import pickle
import argparse

import numpy as np
import re
from db_manager import DatabaseManager
import predict
import ast
from make_vocab import tokenizer_kor
import Levenshtein


# 경로
ENG_DB_PATH = 'data/processed/database/eng_database.db'
IPA_DB_PATH = 'data/processed/database/ipa_database.db'
ALPHABET_DB_PATH = 'data/processed/database/alphabet_database.db'

PATH_SRC = 'data/raw/test_sentence/source.txt'
PATH_TRG = 'data/raw/test_sentence/target.txt'

OUTPUT_SOURCE_PATH = 'data/processed/test_results/RESULT.txt'

INPUT_SOURCE_TARGET_PATH = 'data/processed/database/ipa_database.txt'

OUTPUT_IPA_COMPARE_URISAM = 'data/processed/test_results/ipa_compare_with_urisam.txt'
OUTPUT_IPA_COMPARE_URISAM_MATCHED = 'data/processed/test_results/ipa_compare_with_urisam_matched.txt'
OUTPUT_IPA_COMPARE_URISAM_UNMATCHED = 'data/processed/test_results/ipa_compare_with_urisam_unmatched.txt'
OUTPUT_IPA_MINIMIZED = 'data/processed/test_results/ipa_minimized.txt'


class Seq2SeqModel:
    SPACE = [' ']
    PAD = ['<pad>']
    ENGLISH_LETTERS = PAD + [chr(i) for i in range(ord('A'), ord('Z')+1)] + [chr(i) for i in range(ord('a'), ord('z')+1)] + SPACE
    IDX2ENGLISH = dict(enumerate(ENGLISH_LETTERS))
    ENGLISH2IDX = {v: k for k, v in IDX2ENGLISH.items()}

    CONSONANTS = [chr(letter) for letter in range(ord('ㄱ'), ord('ㅎ')+1)]
    VOWEL = [chr(letter) for letter in range(ord('ㅏ'), ord('ㅣ')+1)]
    KOREAN_LETTERS = PAD + CONSONANTS + VOWEL + SPACE
    IDX2KOREAN = dict(enumerate(KOREAN_LETTERS))
    KOREAN2IDX = {v: k for k, v in IDX2KOREAN.items()}

    def __init__(self):
        # self.model = load_model('data/our_sam_model.h5')
        self.max_len_src = 50
        self.max_len_trg = 50

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

# 10/16 새로 만듬
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
            # print("우리샘사전 DB\n")
            self.our_sam_database_count += 1
            return self.db_manager_eng.check_word_existence(word)[5]

        # Check in IPA DB
        elif self.db_manager_ipa.check_word_existence(word):
            self.ipa_database_count += 1
            return self.db_manager_ipa.check_word_existence(word)[5]

        # All uppercase case
        elif word_str.isupper():
            # print("알파벳이고 모두 대문자 DB\n")
            self.upper_case_count += 1
            return self.get_pronunciation(word, self.db_manager_alp)

        # 딥러닝 case
        else:
            # print("Deep러닝 DB\n")
            self.no_result_count += 1
            # print(word_str)
            result = predict.single_predict(word_str)
            return result

    def sentence_pronunciation(self, txt):
        pattern = re.compile(r'[a-zA-Z]+')
        sentences = pattern.findall(txt)
        
        for value in sentences:
            txt = txt.replace(value, self.word_pronunciation(value), 1)

        return txt

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
    # -------------------------------------------------------------------------------------
    # 단어 하나만 입력해서 확인합니다.
    # -------------------------------------------------------------------------------------
    while(True):
        output_sentence = input("텍스트를 입력하세요: ")

        transformed_sentence = text_pronunciation.sentence_pronunciation(output_sentence.strip())
        print(transformed_sentence)
    # -------------------------------------------------------------------------------------

    # -------------------------------------------------------------------------------------
    # 하나 이상의 한/영 문장의 txt파일을 읽어서 변환된 결과들을 다른 txt파일에 저장합니다.
    # -------------------------------------------------------------------------------------
    # with open(PATH_SRC, 'r', encoding='utf-8') as infile:
    #     sentences = infile.readlines()
    # output_sentences = []
    # for sentence in sentences:
    #     transformed_sentence = text_pronunciation.sentence_pronunciation(sentence.strip())
    #     output_sentences.append(transformed_sentence)

    # with open(OUTPUT_SOURCE_PATH, 'w', encoding='utf-8') as outfile:
    #     outfile.write('\n'.join(output_sentences))

    # print(f"Processing complete. Results saved to {OUTPUT_SOURCE_PATH}")
    # print(f"Total words processed: {text_pronunciation.total_count}")
    # print(f"single_alphabet_count: {text_pronunciation.single_alphabet_count}")
    # print(f"our_sam_database_count: {text_pronunciation.our_sam_database_count}")
    # print(f"ipa_database_count: {text_pronunciation.ipa_database_count}")
    # print(f"upper_case_count: {text_pronunciation.upper_case_count}")
    # print(f"deep_learning_case_count: {text_pronunciation.no_result_count}")
    # print(f"Processing Rate: {1 - (text_pronunciation.no_result_count / text_pronunciation.total_count)}")

    # print(compare(OUTPUT_SOURCE_PATH, PATH_TRG))


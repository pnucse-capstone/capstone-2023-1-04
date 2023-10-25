from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import List, Tuple
from enum import Enum

@dataclass
class WordInfo:
    word: str
    pronunciation: str
    pos: str
    word_type: str
    source: str

@dataclass_json
@dataclass
class DictWordItem:
    word: str = ''
    word_type: str = ''
    word_unit: str = ''
    # [word, pronuciation], wordinfo->conju_info->abbreviation_info/conjugation_info
    conju_list: List[Tuple[str, str]] = field(default_factory=list)
    pronun_list: List[str] = field(default_factory=list)  # pronunciation_info -> pronunciation
    sense_no: str = ''  # senseinfo -> sense_no
    sense_type: str = ''  # senseinfo -> type
    pos: str = ''  # senseinfo -> pos
    origin_lang: str = ''  # original_language_info -> original_language
    origin_lang_type: str = ''  # original_language_info -> language_type

@dataclass
class KT_TTS:
    id: str = '000000'
    sent: str = ""

class HangulJamo:
    def __init__(self):
        # @TODO : 영어에 대한 처리를 해야됨.
        # @TODO : 띄어쓰기 처리 추가 했고
        # @TODO : 숫자 처리
        # @TODO :

        ''' 'O' 는 기호같은거 처리하기 위해 '''
        self.initial = [
            ' ',
            'ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
            'ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ'
        ]
        self.medial = [
            '',
            'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ',
            'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ', 'ㅣ'
        ]
        self.final = [
            '',
            'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ',
            'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ',
            'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
        ]

        self.all_jamo = [
            '', ' ', 'ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ',
            'ㄲ', 'ㄸ', 'ㅃ', 'ㅆ', 'ㅉ',
            'ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ',
            'ㅢ', 'ㅣ', 'ㄳ', 'ㄵ', 'ㄶ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅄ'
        ]

    def get_jamo_tok2ids(self):
        initial_tok2ids = {x: i for i, x in enumerate(self.initial)}
        medial_tok2ids = {x: i for i, x in enumerate(self.medial)}
        final_tok2ids = {x: i for i, x in enumerate(self.final)}

        return initial_tok2ids, medial_tok2ids, final_tok2ids

    def get_jamo_ids2tok(self):
        initial_ids2tok = {i: x for i, x in enumerate(self.initial)}
        medial_ids2tok = {i: x for i, x in enumerate(self.medial)}
        final_ids2tok = {i: x for i, x in enumerate(self.final)}

        return initial_ids2tok, medial_ids2tok, final_ids2tok

    def get_all_jamo_converter(self):
        all_jamo_ids2tok = {i: x for i, x in enumerate(self.all_jamo)}
        all_jamo_tok2ids = {x: i for i, x in enumerate(self.all_jamo)}

        return all_jamo_ids2tok, all_jamo_tok2ids

    def get_length(self):
        return len(self.all_jamo)

MECAB_POS_TAG = {
    0: "O",
    1: "NNG", 2: "NNP",  # 일반 명사, 고유명사
    3: "NNB", 4: "NNBC",  # 의존 명사, 단위를 나타내는 명사
    5: "NR", 6: "NP",  # 수사, 대명사
    7: "VV", 8: "VA",  # 동사, 형용사
    9: "VX", 10: "VCP", 11: "VCN",  # 보조 용언, 긍정 지정사, 부정 지정사
    12: "MM", 13: "MAG",  # 관형사, 일반 부사
    14: "MAJ", 15: "IC",  # 접속 부사, 감탄사
    16: "JKS", 17: "JKC",  # 주격 조사, 보격 조사
    18: "JKG", 19: "JKO",  # 관형격 조사, 목적격 조사
    20: "JKB", 21: "JKV",  # 부사격 조사, 호격 조사
    22: "JKQ", 23: "JX", 24: "JC",  # 인용격 조사, 보조사, 접속 조사
    25: "EP", 26: "EF", 27: "EC",  # 선어말 어미, 종결 어미, 연결 어미
    28: "ETN", 29: "ETM",  # 명사형 전성 어미, 관형형 전성 어미
    30: "XPN", 31: "XSN",  # 체언 접두사, 명사 파생 접미사
    32: "XSV", 33: "XSA", 34: "XR",  # 동사 파생 접미사, 형용사 파생 접미사, 어근
    35: "SF", 36: "SE",  # (마침표, 물음표, 느낌표), 줄임표
    37: "SSO", 38: "SSC",  # 여는 괄호, 닫는 괄호
    39: "SC", 40: "SY",  # 구분자, (붙임표, 기타 기호)
    41: "SL", 42: "SH", 43: "SN",  # 외국어, 한자, 숫자
}

@dataclass
class KrStdDict:
    id: int
    word: str
    lexi_super: str
    origin: str
    pronun: str

@dataclass
class ConjuInfo:
    word: str = ""
    pronun: List[str] = field(default_factory=list)

@dataclass
class OurSamDict:
    target_code: str = ""
    word: str = ""
    sense_id: str = ""
    pronun: List[str] = field(default_factory=list)
    pos: str = ""
    cat: str = ""
    conjugation: List[ConjuInfo] = field(default_factory=list)
    abbreviation: List[ConjuInfo] = field(default_factory=list)

#==================================================
@dataclass
class OurSamItem:
#==================================================
    input_sent: str = ""
    pred_sent: str = ""
    ans_sent: str = ""
    conv_sent: str = ""

    input_word: List[str] = field(default_factory=list)
    pred_word: List[str] = field(default_factory=list)
    our_sam_word: List[str] = field(default_factory=list)
    pos: str = 'None'
    ans_word: List[str] = field(default_factory=list)



class Section(): #Enum class의 집합

    class WordType(Enum):
        고유어 = "고유어"
        한자어 = "한자어"
        외래어 = "외래어"
        혼종어 = "혼종어"
        활용어 = "활용어"
        ERROR = "ERROR"

        def __eq__(self, value):
            return self.name == value

        def __str__(self):
            return self.name

    class Pos(Enum):
        명사 = "명사"
        동사 = "동사"
        형용사 = "형용사"
        ERROR = "ERROR"

        def __eq__(self, value):
            return self.name == value

        def __str__(self):
            return self.name

    class SenseNo(Enum):
        ONE = "001"
        ERROR = "ERROR"

        def __eq__(self, value):
            return self.value == value

        def __str__(self):
            return self.name

    class SenseType(Enum):
        일반어 = "일반어"
        ERROR = "ERROR"

        def __eq__(self, value):
            return self.name == value

        def __str__(self):
            return self.name

    class OriginLangType(Enum):
        영어 = "영어"
        고유어 = "고유어"
        한자어 = "한자어"
        ERROR = "ERROR"

        def __eq__(self, value):
            return self.name == value

        def __str__(self):
            return self.name




### main ###
if "__main__" == __name__:
    hangul_jamo = HangulJamo()
    all = ['']
    for a in hangul_jamo.initial:
        if a not in all:
            all.append(a)
    print(all)

    for b in hangul_jamo.medial:
        if b not in all:
            all.append(b)
    print(all)

    for c in hangul_jamo.final:
        if c not in all:
            all.append(c)
    print(all)
    print(len(all))

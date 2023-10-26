import string
from collections import Counter
import pickle
from torchtext.vocab import Vocab
from jamo import h2j, j2hcj
from torchtext import data as ttd

def build_alphabet_vocab():
    # 알파벳 문자로 vocab을 생성합니다.
    alphabet = list(string.ascii_lowercase)  # 알파벳 소문자 리스트 생성
    alphabet += string.ascii_uppercase  # 대문자
    alphabet += " "

    # Vocab 객체를 생성합니다.
    eng_vocab = Vocab(
        Counter(alphabet),
        specials=["<pad>"],
        specials_first=False,
    )

    eng = ttd.Field(tokenize=list,
                    lower=False,
                    batch_first=True,
                    use_vocab=True,
                    pad_token="<pad>",
                    )

    eng.vocab = eng_vocab
    print(len(eng.vocab))

    # vocab의 크기와 모든 알파벳 출력
    print("Vocab size:", len(eng_vocab))
    print("Alphabet tokens:", eng_vocab.itos)

    with open('data/pickles/eng.pickle', 'wb') as eng_file:
        pickle.dump(eng, eng_file)

def build_jaso_vocab():
    # 초성, 중성, 종성 리스트
    CHO = ["ㄱ", "ㄲ", "ㄴ", "ㄷ", "ㄸ", "ㄹ", "ㅁ", "ㅂ", "ㅃ", "ㅅ", "ㅆ", "ㅇ", "ㅈ", "ㅉ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    JUNG = ["ㅏ", "ㅐ", "ㅑ", "ㅒ", "ㅓ", "ㅔ", "ㅕ", "ㅖ", "ㅗ", "ㅘ", "ㅙ", "ㅚ", "ㅛ", "ㅜ", "ㅝ", "ㅞ", "ㅟ", "ㅠ", "ㅡ", "ㅢ", "ㅣ"]
    JONG = ["", "ㄱ", "ㄲ", "ㄳ", "ㄴ", "ㄵ", "ㄶ", "ㄷ", "ㄹ", "ㄺ", "ㄻ", "ㄼ", "ㄽ", "ㄾ", "ㄿ", "ㅀ", "ㅁ", "ㅂ", "ㅄ", "ㅅ", "ㅆ", "ㅇ",
            "ㅈ", "ㅊ", "ㅋ", "ㅌ", "ㅍ", "ㅎ"]
    extra_chars = [" ", "<pad>", "<sos>", "<eos>"]

    all_chars = CHO + JUNG + JONG + extra_chars

    # Vocab 객체를 생성합니다.
    kor_vocab = Vocab(
        Counter(all_chars),
        specials=[],
        specials_first=False,

    )
    # Field 객체를 생성합니다.
    kor = ttd.Field(
        tokenize=tokenizer_kor,
        lower=True,
        batch_first=True,
        init_token='<sos>',
        eos_token='<eos>',
        pad_token="<pad>",
        use_vocab=True,  # vocab을 사용할 것임을 나타냅니다.
    )

    print("Vocab size:", len(kor_vocab))
    print("Alphabet tokens:", kor_vocab.itos)

    kor.vocab = kor_vocab
    print(len(kor.vocab))

    with open('data/pickles/kor.pickle', 'wb') as kor_file:
        pickle.dump(kor, kor_file)


# tokenizer 함수 정의 (tokenize 함수의 예시)
def tokenizer_kor(text):
    print("hie")
    return list(j2hcj(h2j(text)))

if __name__ == '__main__':
    build_alphabet_vocab()
    build_jaso_vocab()
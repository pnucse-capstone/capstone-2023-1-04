import pickle
import argparse

import torch
from soynlp.tokenizer import LTokenizer

from .utils import Params, clean_text, display_attention

from transformer_architecture.transformer import Transformer

from .tools.unicode import join_jamos 


import ast
import re


# 경로
PARAMS1_PATH = 'models/config/params1.json' # model 15
PARAMS2_PATH = 'models/config/params2.json' # model 21
PATH = 'data/raw/test_sentence/source.txt'
OUTPUT_PATH = 'data/model_kt.txt'

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

            result.extend([chr(LBASE + l), chr(VBASE + v), chr(TBASE + t) if t > 0 else ''])
        else:
            result.append(c)

    return result

def calculate_ratio(list1, list2):
    tmp = list1
    count = 0

    if len(list1) >= len(list2):
        pass
    else:
        list1 = list2
        list2 = tmp

    size = len(list1)

    for idx, val in enumerate(list2):
        if val == list1[idx]:
            count += 1
    if count:
        return size / count
    else:
        return 0

# 파일에서 데이터 읽어오기
def read_data(filename):
    data = []
    with open(filename, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()  # 빈 줄이 아닌 경우에만 처리
            if line:
                data.append(parse_line(line))
    return data


def read_data_raw(filename):
    data = []
    pattern = re.compile(r'[^a-zA-Z ]')
    with open(filename, 'r', encoding='utf-8') as file:
        
        for line in file:
            modified = pattern.sub('', line)
            modified = modified.strip()  # 빈 줄이 아닌 경우에만 처리
            if modified:
                if len(modified) != 1:
                    data.append(modified)
    return data


def predict(config):
    
    input = clean_text(config.input)
    if len(input) > 3 and len(input) <= 12:
        params = Params(PARAMS1_PATH) # model 15
    else:
        params = Params(PARAMS2_PATH) # model 21
        
    # params = Params(Params2_PATH)
    
    # load tokenizer and torchtext Fields
    # pickle_tokenizer = open('pickles/tokenizer.pickle', 'rb')
    # cohesion_scores = pickle.load(pickle_tokenizer)
    # tokenizer = LTokenizer(scores=cohesion_scores)
    pickle_kor = open('data/pickles/kor.pickle', 'rb')
    kor = pickle.load(pickle_kor)
    kor_idx = kor.vocab.stoi['<eos>']

    pickle_eng = open('data/pickles/eng.pickle', 'rb')
    eng = pickle.load(pickle_eng)

    # select model and load trained model
    model = Transformer(params)
    model.load_state_dict(torch.load(params.save_model, map_location='cpu'))
    model.to(params.device)
    model.eval()

    # convert input into tensor and forward it through selected model
    tokenized = list(input)
    indexed = [eng.vocab.stoi[token] for token in tokenized]

    source = torch.LongTensor(indexed).unsqueeze(0).to(params.device)  # [1, source_len]: unsqueeze to add batch size
    target = torch.zeros(1, params.max_len).type_as(source.data)       # [1, max_len]

    encoder_output = model.encoder(source)
    next_symbol = kor.vocab.stoi['<sos>']

    for i in range(0, params.max_len):
        target[0][i] = next_symbol
        decoder_output, _ = model.decoder(target, source, encoder_output)  # [1, target length, output dim]
        prob = decoder_output.squeeze(0).max(dim=-1, keepdim=False)[1]
        next_word = prob.data[i]
        next_symbol = next_word.item()
    try:
        eos_idx = int(torch.where(target[0] == kor_idx)[0][0])
        target = target[0][:eos_idx].unsqueeze(0)
    except Exception as e:
        return config.input, config.input
    

    # translation_tensor = [target length] filed with word indices
    target, attention_map = model(source, target)
    target = target.squeeze(0).max(dim=-1)[1]

    translated_token = [kor.vocab.itos[token] for token in target]
    translation = translated_token[:translated_token.index('<eos>')]
    translation = ''.join(translation)

    #print(f'eng> {config.input}')
    #print(f'kor> {join_jamos(translation)}')
    return config.input, join_jamos(translation)
    # display_attention(tokenized, translated_token, attention_map[4].squeeze(0)[:-1])

def multi_predict(lis):
    parser = argparse.ArgumentParser(description='Kor-Eng Translation prediction')
    parser.add_argument('--input', type=str, default="")
    list_predict = []
    for idx, val in enumerate(lis):
        print(f"{idx}: {val}")
        option = parser.parse_args(['--input', str(val).lower()])
        inp, out = predict(option)
        list_predict.append({"input": inp, "output": out})
        if idx % 10 == 0:
            print(f"{idx} / {len(lis)}")

    return list_predict

def single_predict(lone):
    parser = argparse.ArgumentParser(description='Kor-Eng Translation prediction')
    parser.add_argument('--input', type=str, default=str(lone).lower())
    option = parser.parse_args()
    inp, out = predict(option)
    return out

if __name__ == '__main__':
    # data = read_data_raw(PATH) # txt 파일
    # word_list_minimized = []
    # for val in range(0, len(word_list), 100):
    #     word_list_minimized.append(word_list[val])
    list_predict = multi_predict([])
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as outfile:
        for tmp_dict in list_predict:
            tmp_dict = str(tmp_dict).strip()
            if tmp_dict:
                outfile.write(tmp_dict + '\n')

    for idx, val in enumerate(list_predict):
        print(f"{idx}: input: {val['input']}, output: {val['output']}")

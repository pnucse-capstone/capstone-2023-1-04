import json
import os
import pickle
import copy
import re

from definition.data_def import KrStdDict, OurSamDict, ConjuInfo, WordInfo, DictWordItem

import xml.etree.ElementTree as ET
from typing import List, Dict
from collections import deque


# ''' JSON 버전 '''
#======================================================
class OurSamMakerByJson:
#======================================================
    def __init__(self):
        print(f'[OurSamMakerByJson][__init__] __init__ !')
        self.TARGET_INFO = {
            'word_type': ['고유어', '한자어', '외래어', '혼종어'],
            'pos': ['명사', '동사', '형용사'],
            'sense_no': ['001'],
            'sense_type': ['일반어'],
            'origin_lang_type': ['영어', '고유어', '한자어']
        }
        print(f'[OurSamMakerByJson][__init__] Target_info:\n{self.TARGET_INFO}')

    def make_dict_word_item_list(self, raw_json_dir_path: str) -> List[DictWordItem]:
        print(f'[OurSamMakerByJson][make_dict_word_item_list] raw_json_dir_path: {raw_json_dir_path}')
        if not os.path.exists(raw_json_dir_path):
            os.makedirs(raw_json_dir_path, exist_ok=True)
            raise Exception(f'ERR - raw_json_dir_path: {raw_json_dir_path}')

        raw_json_files = [x for x in os.listdir(raw_json_dir_path) if '.json' in x]
        print(f'[OurSamMakerByJson][make_dict_word_item_list] raw_json_files.size: {len(raw_json_files)}')

        raw_word_item_list: List[DictWordItem] = []
        for f_idx, file_name in enumerate(raw_json_files):
            print(f'[OurSamMakerByJson][make_dict_word_item_list] f_idx: {f_idx}, file_name: {file_name}')
            root_data = None
            with open(os.path.join(raw_json_dir_path, file_name), mode='r', encoding='utf-8') as f:
                root_data = json.load(f)

            item_arr = root_data['channel']['item']
            print(f'[OurSamMakerByJson][make_dict_word_item_list] item_arr.size: {len(item_arr)}')

            for item_idx, item_obj in enumerate(item_arr):
                dic_word_item = DictWordItem(
                    word=item_obj['wordinfo']['word'],
                    word_type=item_obj['wordinfo']['word_type'],
                    word_unit=item_obj['wordinfo']['word_unit']
                )

                if 'conju_info' in item_obj['wordinfo'].keys():
                    for conju_item in item_obj['wordinfo']['conju_info']:
                        if ('abbreviation_info' in conju_item.keys()) \
                                and ('pronunciation_info' in conju_item['abbreviation_info'].keys()):
                            abbreviation_info_obj = conju_item['abbreviation_info']
                            dic_word_item.conju_list.append(abbreviation_info_obj['abbreviation'])
                            dic_word_item.conju_list.append(abbreviation_info_obj['pronunciation_info']['pronunciation'])
                        if ('conjugation_info' in conju_item.keys()) \
                                and ('pronunciation_info' in conju_item['conjugation_info'].keys()):
                            conjugation_info_obj = conju_item['conjugation_info']
                            dic_word_item.conju_list.append(conjugation_info_obj['conjugation'])
                            dic_word_item.conju_list.append(conjugation_info_obj['pronunciation_info']['pronunciation'])

                if 'pronunciation_info' in item_obj['wordinfo'].keys():
                    for p_info in item_obj['wordinfo']['pronunciation_info']:
                        dic_word_item.pronun_list.append(p_info['pronunciation'])
                else:
                    dic_word_item.pronun_list = [dic_word_item.word]

                # if 'original_language_info' in item_obj['wordinfo'].keys():
                #     original_lang_info = item_obj['wordinfo']['original_language_info'][0]
                #     origin_lang = original_lang_info['original_language']
                #     language_type = original_lang_info['language_type']

                #     origin_lang = re.sub(r'\[.*?\]|\([^)]*\)', '', origin_lang)
                #     origin_lang = origin_lang.split(',')[0].strip()

                #     dic_word_item.origin_lang = origin_lang
                #     dic_word_item.origin_lang_type = language_type
                
                if 'original_language_info' in item_obj['wordinfo'].keys():
                    original_lang_info_list = item_obj['wordinfo']['original_language_info']
                    origin_lang_list = []
                    language_type_list = []

                    for original_lang_info in original_lang_info_list:
                        origin_lang = original_lang_info['original_language']
                        language_type = original_lang_info['language_type']

                        origin_lang = re.sub(r'\[.*?\]|\([^)]*\)', '', origin_lang)
                        origin_lang = origin_lang.split(',')[0].strip()

                        origin_lang_list.append(origin_lang)
                        language_type_list.append(language_type)

                    dic_word_item.origin_lang = ' '.join(origin_lang_list)
                    dic_word_item.origin_lang_type = ' '.join(language_type_list)

                if 'senseinfo' in item_obj.keys():
                    dic_word_item.sense_no = item_obj['senseinfo']['sense_no']
                    if 'pos' in item_obj['senseinfo'].keys():
                        dic_word_item.pos = item_obj['senseinfo']['pos']

                    if 'type' in item_obj['senseinfo'].keys():
                        dic_word_item.sense_type = item_obj['senseinfo']['type']

                raw_word_item_list.append(copy.deepcopy(dic_word_item))
        return raw_word_item_list







    def get_filtered_word_item(
            self,
            dict_word_item_list: List[DictWordItem]
    ):
        print(f'[OurSamMakerByJson][get_filtered_word_item] dict_word_item_list.size: {len(dict_word_item_list)}')

        deq_word_item_list = deque(dict_word_item_list)
        deque_size = len(deq_word_item_list)

        for _ in range(deque_size):
            curr_item = deq_word_item_list.popleft()

            ''' 혼종어를 제외한 갯수 ''' # 개별로 했을 때 1,164,952 -> 897,693
            if curr_item.word_type not in self.TARGET_INFO['word_type']:
                continue

            # ''' 명사만을 추출 ''' # 개별로 했을 때 1,164,952 -> 563,694
            # if curr_item.pos not in self.TARGET_INFO['pos']:
            #     continue
            # # 혼종어 제외, 명사만 추출 개수: 1,164,952 -> 500,296

            # ''' sense id == 001 ''' # 위에꺼까지 종합: 1,164,952 -> 360,705
            # if (curr_item.sense_no not in self.TARGET_INFO['sense_no']) and ('' != curr_item.sense_no):
            #     continue

            ''' 일반어 ''' # 1,164,952 -> 268,343
            if curr_item.sense_type not in self.TARGET_INFO['sense_type']:
                continue

            deq_word_item_list.append(curr_item)
        print(f'[OurSamMakerByJson][get_filtered_word_item] deq_word_item_list.size: {len(deq_word_item_list)}')

        ''' word나 pronun_list, conju_list에서 특수 기호 제거 '''
        for word_item in deq_word_item_list:
            # Process word
            word_item.word = word_item.word.replace('^', ' ').replace('-', '')

            # Process pronun_list and conju_list
            for list_name in ['pronun_list', 'conju_list']:
                if not isinstance(getattr(word_item, list_name), list):
                    # str -> list
                    setattr(word_item, list_name, [getattr(word_item, list_name).replace('^', ' ').replace('-', '')])
                else:
                    for idx, list_item in enumerate(getattr(word_item, list_name)):
                        setattr(word_item, list_name, [re.sub(r'[^가-힣]+', '', item) for item in getattr(word_item, list_name)])


        return deq_word_item_list

    def get_splited_kor_eng_dict(
            self,
            src_dict_path: str
    ):
        print(f'[OurSamMakerByJson][get_splited_kor_eng_dict] src_dict_path: {src_dict_path}')

        # init
        kor_dict: List[DictWordItem] = []
        eng_dict: List[DictWordItem] = []

        raw_dict: List[DictWordItem] = []
        with open(src_dict_path, mode='rb') as r_f:
            raw_dict = pickle.load(r_f)
        print(f'[OurSamMakerByJson][get_splited_kor_eng_dict] raw_dict.size: {len(raw_dict)}')

        # split
        for raw_idx, raw_item in enumerate(raw_dict):
            if '' == raw_item.origin_lang_type:
                kor_dict.append(raw_item)
            elif '영어' == raw_item.origin_lang_type:
                eng_dict.append(raw_item)

        print(f'[OurSamMakerByJson][get_splited_kor_eng_dict] kor_dict.size: {len(kor_dict)}')
        print(f'[OurSamMakerByJson][get_splited_kor_eng_dict] eng_dict.size: {len(eng_dict)}')

        return kor_dict, eng_dict

    def make_lang_item_info_json(
            self,
            target_dict: List[DictWordItem],
            lang: str
    ):
        print(f'[OurSamMakerByJson][make_lang_item_info_json] lang: {lang}, target_dict.size: {len(target_dict)}')

        json_format = {
            'root': []
        }

        target_dict.sort(key=lambda x: x.word)
        for item in target_dict:
            json_format['root'].append(item.to_json(ensure_ascii=False))
        print(f'[OurSamMakerByJson][make_lang_item_info_json] json_format.root.size: {len(json_format["root"])}')

        return json_format

    def get_word_type_cnt_info(
            self,
            target_dict: List[DictWordItem],
            target_word_type: str
    ):
        print(f'[OurSamMakerByJson][get_word_type_cnt_info] target_dict.size: {len(target_dict)}, '
              f'target_word_type: {target_word_type}')

        ret_cnt = 0
        for idx, dict_item in enumerate(target_dict):
            if target_word_type == dict_item.word_type:
                ret_cnt += 1
        print(f'[OurSamMakerByJson][get_word_type_cnt_info] target_lang_type: {target_word_type}, count: {ret_cnt}')

        return ret_cnt

    def get_conju_items_count(
            self,
            target_dict: List[DictWordItem],
    ):
        print(f'[OurSamMakerByJson][get_conju_items_count] target_dict.size: {len(target_dict)}')

        ret_cnt = 0
        for idx, dict_items in enumerate(target_dict):
            ret_cnt += len(dict_items.conju_list)
        print(f'[OurSamMakerByJson][get_conju_items_count] conju_list.size: {ret_cnt}')

        return ret_cnt

### MAIN ###
if "__main__" == __name__:
    print("[dict_maker] __main__")

    b_use_xml_version_maker = False
    b_use_json_version_maker = True



    if b_use_json_version_maker:
        print(f'[our_sam_maker][__main__] maker - json_version')
        dict_maker_json_ver = OurSamMakerByJson()

        raw_word_item_pkl_path = 'data/processed/dictionary/raw_dict_word_item.pkl'
        filtered_word_item_pkl_path = 'data/processed/dictionary/filtered_dict_word_item.pkl'
        b_make_raw_word_item_list = True

        if b_make_raw_word_item_list:
            word_item_list = dict_maker_json_ver.make_dict_word_item_list(raw_json_dir_path='data/raw/our_sam')
            print(f'[our_sam_maker][__main__] word_item_list.size: {len(word_item_list)}')

            ''' Save '''
            with open(raw_word_item_pkl_path, mode='wb') as f:
                pickle.dump(word_item_list, f)

        raw_word_item_list = []
        with open(raw_word_item_pkl_path, mode='rb') as f:
            raw_word_item_list = pickle.load(f)
        print(f'[our_sam_maker][__main__] raw_word_item_list.size: {len(raw_word_item_list)}')

        dict_word_item_list = dict_maker_json_ver.get_filtered_word_item(dict_word_item_list=raw_word_item_list)
        print(f'[our_sam_maker][__main__] dict_word_item_list.size: {len(dict_word_item_list)}')

        ''' Save '''
        with open(filtered_word_item_pkl_path, mode='wb') as f:
            ''' 정렬 ! '''
            list(dict_word_item_list).sort(key=lambda x: x.word)
            pickle.dump(dict_word_item_list, f)

        #============================================================
        ''' 만들어진 기분석 사전에서 한글과 영어 분리하기'''
        kor_dict, eng_dict = dict_maker_json_ver.get_splited_kor_eng_dict(src_dict_path=filtered_word_item_pkl_path)

        ''' Save '''
        with open('data/processed/dictionary/kor_dict.json', mode='w', encoding='utf-8') as k_f:
            kor_save_json = dict_maker_json_ver.make_lang_item_info_json(target_dict=kor_dict, lang='kor')
            json.dump(kor_save_json, k_f, indent=4, ensure_ascii=False)
            print(f'[our_sam_maker][__main__] Save Complete ! - Kor Dict')

        with open('data/processed/dictionary/eng_dict.json', mode='w', encoding='utf-8') as e_f:
            eng_save_json = dict_maker_json_ver.make_lang_item_info_json(target_dict=eng_dict, lang='eng')
            json.dump(eng_save_json, e_f, indent=4, ensure_ascii=False)
            print(f'[our_Sam_maker][__main__] Save Complete ! - Eng Dict')

        dict_maker_json_ver.get_word_type_cnt_info(target_dict=list(dict_word_item_list), target_word_type='고유어')
        dict_maker_json_ver.get_word_type_cnt_info(target_dict=list(dict_word_item_list), target_word_type='한자어')
        dict_maker_json_ver.get_word_type_cnt_info(target_dict=list(dict_word_item_list), target_word_type='외래어')

        dict_maker_json_ver.get_conju_items_count(target_dict=list(dict_word_item_list))
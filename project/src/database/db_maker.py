import os
import sqlite3
import pickle
from definition.data_def import Section
import collections

# 기반 데이터베이스 생성 클래스
class BaseDatabaseMaker:
    def __init__(self, data_filename):
        self.data_file = os.path.join('data/dictionary', data_filename)

    def load_data(self):
        with open(self.data_file, 'rb') as file:
            return pickle.load(file)

    def setup_db(self, db_file):
        if os.path.exists(db_file):
            os.remove(db_file)

        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(self.table)
        return conn, cursor

#단어 정보 데이터베이스 생성 클래스
class DatabaseMaker(BaseDatabaseMaker):
    table = '''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                word TEXT,
                word_type TEXT,
                word_unit TEXT,
                conju_list TEXT,
                pronun_list TEXT,
                sense_no TEXT,
                sense_type TEXT,
                pos TEXT,
                origin_lang TEXT,
                origin_lang_type TEXT
            )
        '''
    def insert_data(self, conn, cursor, data, word_type=None):
        id_counter = 1
        sorted_data = sorted(data if word_type is None else [item for item in data if item.word_type == word_type], key=lambda item: item.word)
        word_check = None

        for item in sorted_data:
            if item.word == word_check:
                continue
            conju_list = '/'.join(str(x) for x in item.conju_list) if item.conju_list else None
            pronun_list = '/'.join(str(x) for x in item.pronun_list) if item.pronun_list else None

            row = (
                id_counter,
                item.word if item.word else None,
                item.word_type if item.word_type else None,
                item.word_unit if item.word_unit else None,
                conju_list,
                pronun_list,
                item.sense_no if item.sense_no else None,
                item.sense_type if item.sense_type else None,
                item.pos if item.pos else None,
                str(item.origin_lang).replace(" ", "") if item.origin_lang else None, # 띄어쓰기 제거해야 일치율 올라감
                item.origin_lang_type if item.origin_lang_type else None
            )
            cursor.execute('''
                INSERT INTO words 
                (id, word, word_type, word_unit, conju_list, pronun_list, sense_no, sense_type, pos, origin_lang, origin_lang_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', row)
            word_check = item.word
            id_counter += 1

        conn.commit()
        conn.close()


#활용형 데이터베이스 생성 클래스
class DatabaseConjuMaker(BaseDatabaseMaker):
    table = '''
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY,
                word TEXT,
                pronun_list TEXT
            )
        '''

    def extract_conju(self):
        data = self.load_data()
        tmp_data = [{'conjugated_word': conju, 'pronun_list': pronun}
                    for value in data if value.conju_list and value.sense_no == Section.SenseNo.ONE
                    for conju, pronun in zip(value.conju_list[::2], value.conju_list[1::2])
                    if conju.strip()]
        tmp_data_fin = list(map(dict, collections.OrderedDict.fromkeys(tuple(sorted(d.items())) for d in tmp_data)))
        return tmp_data_fin


    def insert_data(self, conn, cursor, data):
        id_counter = 1
        sorted_data = sorted(data, key=lambda item: item['conjugated_word'])

        for item in sorted_data:
            row = (
                id_counter,
                item['conjugated_word'],
                item['pronun_list']
            )
            cursor.execute('''
                INSERT INTO words 
                (id, word, pronun_list)
                VALUES (?, ?, ?)
            ''', row)
            id_counter += 1

        conn.commit()
        conn.close()

#IPA 데이터 베이스 생성 클래스
class DatabaseIpaMaker(BaseDatabaseMaker):
    table = '''
             CREATE TABLE IF NOT EXISTS words (
                 id INTEGER PRIMARY KEY,
                 word TEXT,
                 word_type TEXT,
                 word_unit TEXT,
                 conju_list TEXT,
                 pronun_list TEXT,
                 sense_no TEXT,
                 sense_type TEXT,
                 pos TEXT,
                 origin_lang TEXT,
                 origin_lang_type TEXT
             )
         '''
    def insert_data(self, conn, cursor, data):
        id_counter = 1
        sorted_data = sorted(data, key=lambda item: item['word'])

        for item in sorted_data:
            row = (
                id_counter,
                item['word'],
                None,
                None,
                None,
                item['pronun'],
                None,
                None,
                None,
                item['word'],
                None
            )
            cursor.execute('''
                INSERT INTO words 
                (id, word, word_type, word_unit, conju_list, pronun_list, sense_no, sense_type, pos, origin_lang, origin_lang_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', row)
            id_counter += 1

        conn.commit()
        conn.close()
        
#알파벳 데이터베이스 생성 클래스
class DatabaseAlphabetMaker(BaseDatabaseMaker):
    table = '''
             CREATE TABLE IF NOT EXISTS words (
                 id INTEGER PRIMARY KEY,
                 word TEXT,
                 word_type TEXT,
                 word_unit TEXT,
                 conju_list TEXT,
                 pronun_list TEXT,
                 sense_no TEXT,
                 sense_type TEXT,
                 pos TEXT,
                 origin_lang TEXT,
                 origin_lang_type TEXT
             )
         '''
    def insert_data(self, conn, cursor, data):
        id_counter = 1

        for item in data:
            row = (
                id_counter,
                item[0],
                item[1],
                item[2],
                None,
                item[4],
                None,
                item[6],
                item[7],
                item[8],
                None
            )
            cursor.execute('''
                INSERT INTO words 
                (id, word, word_type, word_unit, conju_list, pronun_list, sense_no, sense_type, pos, origin_lang, origin_lang_type)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', row)
            id_counter += 1

        conn.commit()
        conn.close()
        

# 데이터베이스 내보내기
class DatabaseExporter:
    def __init__(self, db_file):
        self.db_file = db_file
    
    #완성된 데이터베이스를 txt 파일로 내보냄
    def to_txt(self, output_file=None):
        if output_file is None:
            output_file = self.db_file.replace('.db', '.txt')

        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM words")
        rows = cursor.fetchall()
        with open(output_file, 'w', encoding='utf-8') as txt:
            for row in rows:
                txt.write(str(row) + '\n')
        conn.close()


def main():
    to_make_oursam = True
    to_make_ipa = True
    to_make_alphabet = True

    #pkl 파일로부터 word_type에 따라 db_files 에 지정된 이름으로 각각 데이터 베이스 생성
    if to_make_oursam:
        db_dir = 'data/processed/database'
        pkl_file_name = 'filtered_dict_word_item.pkl'
        word_types = ['고유어', '한자어', '외래어', '혼종어']
        db_files = ['kor_database.db', 'chn_database.db', 'eng_database.db', 'mixed_database.db']
        db_files = [os.path.join(db_dir, db_file) for db_file in db_files]
    
        db_manager = DatabaseMaker(pkl_file_name)
        data = db_manager.load_data()

        for word_type, db_file in zip(word_types, db_files):
            conn, cursor = db_manager.setup_db(db_file)
            db_manager.insert_data(conn, cursor, data, word_type)
            exporter = DatabaseExporter(db_file)
            exporter.to_txt()
    
        conn, cursor = db_manager.setup_db(os.path.join(db_dir, 'total_database.db'))
        db_manager.insert_data(conn, cursor, data)
        exporter = DatabaseExporter(os.path.join(db_dir, 'total_database.db'))
        exporter.to_txt()
    
        db_conju_manager = DatabaseConjuMaker(pkl_file_name)
        data_conju = db_conju_manager.extract_conju()
        conn, cursor = db_conju_manager.setup_db(os.path.join(db_dir, 'conju_database.db'))
        db_conju_manager.insert_data(conn, cursor, data_conju)
        exporter = DatabaseExporter(os.path.join(db_dir, 'conju_database.db'))
        exporter.to_txt()

    # ipa 데이터베이스 생성
    if to_make_ipa:
        db_dir = 'data/pickle/database'
        pkl_file_name ='ipa_dict.pickle'

        db_ipa_manager = DatabaseIpaMaker(pkl_file_name)
        data_ipa = db_ipa_manager.load_data()
        conn, cursor = db_ipa_manager.setup_db(os.path.join(db_dir, 'ipa_database.db'))
        db_ipa_manager.insert_data(conn, cursor, data_ipa)
        exporter = DatabaseExporter(os.path.join(db_dir, 'ipa_database.db'))
        exporter.to_txt()
        
    # 알파벳 데이터베이스 생성
    if to_make_alphabet:
        db_dir = 'data/pickle/database'
        pkl_file_name ='alphabet_dict.pkl'

        db_manager = DatabaseAlphabetMaker(pkl_file_name)
        data = db_manager.load_data()
        conn, cursor = db_manager.setup_db(os.path.join(db_dir, 'alphabet_database.db'))
        db_manager.insert_data(conn, cursor, data)
        exporter = DatabaseExporter(os.path.join(db_dir, 'alphabet_database.db'))
        exporter.to_txt()


if __name__ == '__main__':
    main()
import sqlite3
import pandas as pd
import re


class DatabaseWordChecker:
    def __init__(self, db_file_path, input_file_path):
        self.db_file_path = db_file_path
        self.input_file_path = input_file_path
        self.words_in_db = self.get_words_from_db()

    #db에서 origin_lang 부분 fetch
    def get_words_from_db(self):
        conn = sqlite3.connect(self.db_file_path)
        cursor = conn.cursor()
        cursor.execute("SELECT origin_lang FROM words")
        words_in_db = set([row[0].lower() for row in cursor.fetchall() if row[0]])
        conn.close()
        return words_in_db

    #fetch한 단어와 eng_source 비교 후 단어 match 확인
    def extract_alpha_to_list(self):
        with open(self.input_file_path, 'r', encoding='utf-8') as file:
            content = file.readlines()

        extracted_data = []
        current_number = 0
        for line in content:
            number_match = re.match(r'^(\d+)', line)
            if number_match:
                current_number = int(number_match.group(1))

            alpha_words = re.findall(r'[a-zA-Z]+', line)
            if alpha_words:
                extracted_data.append((str(current_number).zfill(6), alpha_words))

        return [(sentence, word) for sentence, words in extracted_data for word in words]

    #math 결과 excel 파일로 저장
    def write_results_to_excel(self, entries):
        word_dict = {}
        for sentence_number, original_word in entries:
            word = original_word.lower()
            in_database = 1 if word in self.words_in_db else 0
            not_in_database = 0 if word in self.words_in_db else 1
            not_in_database_but_upper = 0

            if not_in_database and original_word.isupper():
                not_in_database = 0
                not_in_database_but_upper = 1

            key = original_word if not in_database else word

            if key in word_dict:
                word_dict[key]['Sentence Number'].append(sentence_number)
            else:
                word_dict[key] = {
                    'Sentence Number': [sentence_number],
                    'Word': original_word,
                    'InDatabase': in_database,
                    'NotInDatabase': not_in_database,
                    'NotInDatabaseButUpper': not_in_database_but_upper
                }

        data = []
        for key, values in word_dict.items():
            sentence_count = len(values['Sentence Number'])
            data.append([','.join(values['Sentence Number']), sentence_count, values['Word'], values['InDatabase'], values['NotInDatabase'], values['NotInDatabaseButUpper']])

        df = pd.DataFrame(data, columns=["Sentence Number", "Sentence Count", "Word", "InDatabase", "NotInDatabase", "NotInDatabaseButUpper"])
        df.to_excel("data/processed/analysis_results/db_word_checker_results.xlsx", index=False, engine='openpyxl')

if __name__ == "__main__":
    db_file_path = "data/processed/database/eng_database.db"
    input_file_name = "data/raw/test_sentence/eng_source.txt"
    db_checker = DatabaseWordChecker(db_file_path, input_file_name)
    entries = db_checker.extract_alpha_to_list()
    db_checker.write_results_to_excel(entries)

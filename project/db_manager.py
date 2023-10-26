import sqlite3


class DatabaseManager:
    def __init__(self, db_file):
        self.db_file = db_file
        self.conn = sqlite3.connect(self.db_file)
        self.cursor = self.conn.cursor()

    def execute_and_commit(self, query, params):
        self.cursor.execute(query, params)
        self.conn.commit()

    def check_word_existence(self, word):
        select_query = '''
            SELECT *
            FROM words
            WHERE origin_lang = ?
        '''
        self.cursor.execute(select_query, (word,))
        result = self.cursor.fetchone()
        if result:
            return result

        select_query = '''
        SELECT *
        FROM words
        WHERE origin_lang = ?
        '''
        self.cursor.execute(select_query, (word.lower(),))
        result = self.cursor.fetchone()
        if result:
            return result

        select_query = '''
                SELECT *
                FROM words
                WHERE origin_lang = ?
                COLLATE NOCASE
            '''
        self.cursor.execute(select_query, (word,))
        return self.cursor.fetchone()

    #단일 query는 시간이 많이 걸리기 때문에, 데이터 한번에 query
    def check_words_existence(self, words_tuple):
        # 쿼리에 필요한 바인딩 개수를 words_tuple의 길이로 동적으로 생성
        placeholders = ', '.join(['?' for _ in range(len(words_tuple))])

        select_query = f'''
            SELECT pronun_list, origin_lang
            FROM words
            WHERE origin_lang IN ({placeholders})
            COLLATE NOCASE
        '''
        self.cursor.execute(select_query, words_tuple)
        result = self.cursor.fetchall()
        return result

    def input_data(self, text, pron=True):
        count = int(input(f"{text}의 개수: "))

        if pron:
            data_list = '/'.join(
                [f"{input(f'{text} 데이터: ')}/{input('발음 데이터: ')}" for _ in range(count)])
        else:
            data_list = '/'.join([input(f'{text} 데이터: ')
                                 for _ in range(count)])

        return data_list

    #db에 있는 단어 검색

    def search_word(self, word):
        result = self.check_word_existence(word)

        if result is None:
            print(f"단어 '{word}'를 찾을 수 없습니다.\n")
        else:
            print(f"단어 '{word}' 검색 완료\n")
            print(result, '\n')

    #db에 새로운 단어를 추가할 수 있도록 하는 함수
    def insert_word(self, word):
        result = self.check_word_existence(word)

        # if result is not None:
        #     print(f"단어 '{word}'는 이미 데이터베이스에 존재합니다.\n")
        #     return
        word_unit = input("발음: ")
        # word_type = input("단어 유형: ")
        # conju_list = self.input_data("활용")
        # pronun_list = self.input_data("발음", False)
        # sense_no = input("의미 번호: ")
        # sense_type = input("의미 유형: ")
        # pos = input("품사: ")
        origin_lang = input("원어: ")
        # origin_lang_type = input("원어 유형: ")

        select_query = '''
            SELECT id, word
            FROM words
        '''
        self.cursor.execute(select_query)
        all_words = self.cursor.fetchall()
        sorted_words = sorted(all_words, key=lambda item: item[1])

        for i, word_item in enumerate(sorted_words, start=1):
            if word <= word_item[1]:
                insert_index = i
                break
        else:
            insert_index = len(sorted_words) + 1

        self.execute_and_commit(
            "UPDATE words SET id = id + 10000000 WHERE id >= ?", (insert_index,))
        self.execute_and_commit(
            "UPDATE words SET id = id - 9999999 WHERE id >= ?", (insert_index + 10000000,))

        insert_query = '''
            INSERT INTO words (id, word, word_type, word_unit, conju_list, pronun_list, sense_no, sense_type, pos, origin_lang, origin_lang_type)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        '''
        self.execute_and_commit(insert_query, (insert_index, word_unit,
                                None, None, None, word_unit, None, None, None, origin_lang, None))
        print(f"단어 '{word}' 추가 완료\n")

    #단어 삭제
    def delete_word(self, word):
        result = self.check_word_existence(word)

        if result is None:
            print(f"단어 '{word}'를 찾을 수 없습니다.\n")
            return

        word_id = result[0]
        self.execute_and_commit(
            "DELETE FROM words WHERE origin_lang = ?", (word,))
        self.execute_and_commit(
            "UPDATE words SET id = id - 1 WHERE id > ?", (word_id,))
        print(f"단어 '{word}' 삭제 완료\n")

    #단어 수정
    def modify_word(self, word):
        result = self.check_word_existence(word)

        if result is None:
            print(f"단어 '{word}'를 찾을 수 없습니다.\n")
            return

        print("수정을 원하는 항목을 선택해주세요\n")
        print("1. word_type\n2. word_unit\n3. conju_list\n"
              "4. pronun_list\n5. sense_no\n6. sense_type\n"
              "7. pos\n8. origin_lang\n9. origin_lang_type")

        select = input()

        if select == '3':
            modify_text = self.input_data("활용")
        elif select == '4':
            modify_text = self.input_data("발음", False)
        else:
            print("수정할 내용을 입력하세요")
            modify_text = input()

        modify_query = '''
            UPDATE words
            SET {} = ?
            WHERE word = ?
        '''
        columns = ['word_type', 'word_unit', 'conju_list', 'pronun_list',
                   'sense_no', 'sense_type', 'pos', 'origin_lang', 'origin_lang_type']
        column = columns[int(select) - 1]

        self.execute_and_commit(
            modify_query.format(column), (modify_text, word))
        print(f"단어 '{word}' 수정 완료\n")


class DatabaseConjuManager(DatabaseManager):

    def search_word(self, word):
        result = self.check_word_existence(word)

        if result is None:
            print(f"단어 '{word}'를 찾을 수 없습니다.\n")
        else:
            print(f"단어 '{word}' 검색 완료\n")
            print(result, '\n')

    def insert_word(self, word):
        result = self.check_word_existence(word)

        if result is not None:
            print(f"단어 '{word}'는 이미 데이터베이스에 존재합니다.\n")
            return

        # conju_list = input("활용: ")
        pronun_list = input("발음: ")

        select_query = '''
            SELECT id, word
            FROM words
        '''
        self.cursor.execute(select_query)
        all_words = self.cursor.fetchall()
        sorted_words = sorted(all_words, key=lambda item: item[1])

        for i, word_item in enumerate(sorted_words, start=1):
            if word <= word_item[1]:
                insert_index = i
                break
        else:
            insert_index = len(sorted_words) + 1

        self.execute_and_commit(
            "UPDATE words SET id = id + 10000000 WHERE id >= ?", (insert_index,))
        self.execute_and_commit(
            "UPDATE words SET id = id - 9999999 WHERE id >= ?", (insert_index + 10000000,))

        insert_query = '''
            INSERT INTO words (id, word, pronun_list)
            VALUES (?, ?, ?)
        '''
        self.execute_and_commit(
            insert_query, (insert_index, word, pronun_list))
        print(f"단어 '{word}' 추가 완료\n")

    def modify_word(self, word):
        result = self.check_word_existence(word)

        if result is None:
            print(f"단어 '{word}'를 찾을 수 없습니다.\n")
            return

        # print("수정을 원하는 항목을 선택해주세요\n")
        # print("1. conju_list\n 1. pronun_list")
        #
        # select = input()
        #
        # if select == '1':
        #     modify_text = input("활용: ")
        # elif select == '2':
        #     modify_text = input("발음: ")
        # else:
        #     print("수정할 내용을 입력하세요")
        #     modify_text = input()
        modify_text = input("발음 수정: ")
        modify_query = '''
            UPDATE words
            SET {} = ?
            WHERE word = ?
        '''
        columns = ['conju_list', 'pronun_list']
        column = columns[1]

        self.execute_and_commit(
            modify_query.format(column), (modify_text, word))
        print(f"단어 '{word}' 수정 완료\n")


def main():

    do_conju = False
    if do_conju:
        db_manager = DatabaseConjuManager(
            'data/processed/database/conju_database.db')
        actions = {
            "1": db_manager.search_word,
            "2": db_manager.insert_word,
            "3": db_manager.delete_word,
            "4": db_manager.modify_word,
        }
    else:
        db_manager = DatabaseManager('data/processed/database/eng_database.db')
        actions = {
            "1": db_manager.search_word,
            "2": db_manager.insert_word,
            "3": db_manager.delete_word,
            "4": db_manager.modify_word,
        }

    while True:
        choice = input(
            "원하는 작업을 선택하세요:\n1. 단어 검색\n2. 단어 추가\n3. 단어 삭제\n4. 단어 수정\n5. 종료\n")

        if choice == "5":
            break
        elif choice in actions:
            word = input("대상 단어를 입력하세요: ")
            actions[choice](word)
        else:
            print("유효한 선택이 아닙니다. 다시 선택해주세요.")

    db_manager.conn.close()


if __name__ == "__main__":
    main()

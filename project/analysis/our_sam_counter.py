import os
import json


#단어 counting 및 분석을 위한 class 정의
class OurSamCounter:
    def __init__(self, input_directory):
        self.input_directory = input_directory
        self.word_unit_counts = {
            #각 단어 type 별로, 품사에 따라 count
            "고유어": {"어휘": 0, "구": 0, "명사": 0, "대명사": 0, "수사": 0, "조사": 0, "동사": 0, "형용사": 0,
                      "관형사": 0, "부사": 0, "감탄사": 0, "접사": 0, "의존 명사": 0, "보조 동사": 0},
            "외래어": {"어휘": 0, "구": 0, "명사": 0, "대명사": 0, "수사": 0, "조사": 0, "동사": 0, "형용사": 0,
                      "관형사": 0, "부사": 0, "감탄사": 0, "접사": 0, "의존 명사": 0, "보조 동사": 0},
            "한자어": {"어휘": 0, "구": 0, "명사": 0, "대명사": 0, "수사": 0, "조사": 0, "동사": 0, "형용사": 0,
                      "관형사": 0, "부사": 0, "감탄사": 0, "접사": 0, "의존 명사": 0, "보조 동사": 0},
            "혼종어": {"어휘": 0, "구": 0, "명사": 0, "대명사": 0, "수사": 0, "조사": 0, "동사": 0, "형용사": 0,
                      "관형사": 0, "부사": 0, "감탄사": 0, "접사": 0, "의존 명사": 0, "보조 동사": 0},
        }
        self.file_count = 0
        self.total_word_count = 0

    def count_words(self):
        for filename in os.listdir(self.input_directory):
            if filename.endswith(".json"):
                self.file_count += 1
                file_path = os.path.join(self.input_directory, filename)

                with open(file_path, "r", encoding="utf-8") as file:
                    data = json.load(file)

                for item in data["channel"]["item"]:
                    word_type = item["wordinfo"].get("word_type")
                    word_unit = item["wordinfo"].get("word_unit")
                    pos = item["senseinfo"].get("pos")

                    #단어의 type(고유어, 외래어, ..)과 unit(어휘, 구)에 따라 count
                    if word_type in self.word_unit_counts and word_unit in self.word_unit_counts[word_type]:
                        self.word_unit_counts[word_type][word_unit] += 1

                    #품사별로 나누어서 count
                    if pos in ["명사", "대명사", "수사", "조사", "동사", "형용사",
                               "관형사", "부사", "감탄사", "접사", "의존 명사", "보조 동사"] and word_type in self.word_unit_counts:
                        self.word_unit_counts[word_type][pos] += 1
                    self.total_word_count += 1

    #txt 파일로 통계 낸 결과를 저장
    def save_to_file(self, output_file):
        with open(output_file, "w", encoding="utf-8") as file:
            file.write(f"파일 개수: {self.file_count}\n")
            file.write(f"전체 단어 개수: {self.total_word_count}\n")
            for word_type, counts in self.word_unit_counts.items():
                file.write("=" * 20 + "\n")
                file.write(f"{word_type} 개수:\n")
                file.write("-" * 20 + "\n")
                for word_unit, count in counts.items():
                    file.write(f"{word_unit}: {count}\n")
        print(f"결과가 {output_file} 파일에 저장되었습니다.")

if __name__ == "__main__":
    counter = OurSamCounter("data/raw/our_sam")
    counter.count_words()
    counter.save_to_file("data/processed/analysis_results/our_sam_counter_results.txt")

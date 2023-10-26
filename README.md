# 지식베이스와 딥러닝을 통한 영어 - 한글 <br/>Grapheme-to-Phoneme 모델의 성능 향상 연구

## 1. 프로젝트 소개

- 한국어와 영어가 혼용된 텍스트를 올바른 발음으로 변환하는 것을 목표로 한다.  <br/>
- 지식베이스와 딥러닝 방식을 결합하여, 기존의 TTS 보다 혼용 텍스트에 대해서 높은 정확도를 달성하고자 한다. 

## 2. 팀소개

### RNG 아니조 팀

<table>
    <tr>
    <td>
      권민규
    </td>
    <td>
      <ul>
        <li>데이터 수집 및 분석</li>
        <li>모델 설계</li>
        <li>우리말샘 데이터 전처리 및 모델 구현</li>
        <li>추가 데이터 수집 및 전처리</li>
        <li><a href = "mailto: jimbo98@pusan.ac.kr">jimbo98@pusan.ac.kr</a></li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>
      고상현
    </td>
    <td>
      <ul>
        <li>데이터 수집 및 분석</li>
        <li>모델 설계</li>
        <li>IPA 변환 규칙 구현 및 모델 최적화</li>
        <li>모델 성능 평가</li>
        <li><a href = "mailto: trmy894@gmail.com">trmy894@gmail.com</a></li>
      </ul>
    </td>
  </tr>
  <tr>
    <td>
      박건우
    </td>
    <td>
      <ul>
        <li>데이터 수집 및 분석</li>
        <li>모델 설계</li>
        <li>IPA 데이터 전처리 및 모델 구현</li>
        <li>데이터 통계 도출</li>
        <li><a href = "mailto: swa10000@pusan.ac.kr">swa10000@pusan.ac.kr</a></li>
      </ul>
    </td>
  </tr>
</table>

## 3. 구성도
### 전체 구성도
![플로우차트](https://github.com/pnucse-capstone/capstone-2023-1-04/assets/84282849/a94c0ab6-90ab-4013-ba35-d24cc4f25643)
<p> 전체문장에서 영단어들을 분리시켜 입력한다.</p></br>

<p>1. 알파벳 단어 하나만 입력으로 들어올 시, 그대로 알파벳 이름을 출력한다.</p>
<p>2. 지식 베이스에 있는 단어가 입력으로 들어올 시, 지식 베이스에 있는 발음으로 출력한다.</p>
<p>3. 위에 해당하지 않는 대문자로만 이루어진 단어들은 단어마다 알파벳 이름 그대로 출력한다.</br>   
       ex)DPICM = 디피아이시엠
</p>
<p>4. 위에 해당하지 않는 단어가 입력으로 들어오면, 모델을 사용해서 발음을 출력한다.</p>
![한영혼용이미지](https://github.com/pnucse-capstone/capstone-2023-1-04/assets/84282849/3c5db9f8-8f4f-40fc-9009-02796896da5d)


<p>-> Wife한테 다녀와도 되냐고 물었더니 ok 했어서 물어봤어요 But your friend랑 같이 있으면 i am 신뢰에요~</p>
<p>-> 와이프한테 다녀와도 되냐고 물었더니 오케이 했어서 물어봤어요 벗 유어 프렌드랑 같이 있으면 아이 앰 신뢰에요~</p>

</br>
<strong>추후에 원하는 문장을 입력할 수 있는 웹페이지와 TTS 모델을 결합 예정</strong>

### 파일 구조
```
project                         
├── data                          // 데이터베이스 파일과 tokenizer pickle 파일
│   ├── analysis_results          
│   │    └── our_sam_counter_results.txt   // 전처리 결과          
│   ├── database
│   │    ├── alphabet_database.db          // 알파벳 데이터베이스  
│   │    ├── eng_database.db               // 외래어 데이터베이스
│   │    └── ipa_database.db               // IPA 데이터베이스  
│   └── pickles                           // tokenizer pickle 파일
│       ├── eng.pickle                        
│       ├── kor.pickle
│       ├── NanumSquareR
│       └── tokenizer.pickle
├── models                       // 모델
│   ├── config
│   │   ├── params1              // 모델 파라미터
│   │   └── params2              // 모델 파라미터2
│   ├── model15.pt               // 사용할 모델
│   └── model21.pt               // 사용할 모델2
├── src                          // 소스 코드 모음
│   ├── analysis
│   │   ├── db_word_checker.py   // 통계용
│   │   └── our_sam_counter.py   // 통계용            
│   ├── database                      
│   │   ├── definition
│   │   │   └── data_def.py      // dataclass                    
│   │   ├── db_maker.py          // DB 생성 코드 
│   │   └── db_manager.py        // DB 관리 코드
│   ├── picklers                          
│   │   ├── pkl_alp_maker.py    // alphabet DB생성을 위한 pickle 생성 코드
│   │   ├── pkl_ipa_maker.py    // ipa DB생성을 위한 pickle 생성 코드
│   │   └── pkl_sam_maker.py    // 외래어 DB생성을 위한 pickle 생성 코드           
│   ├── transformer_architecture // 딥 러닝 모델 관련 코드
│   │    ├── __init__.py
│   │    ├── predict.py          // 모델 예측 코드
│   │    ├── trainer.py          // 모델 학습 코드
│   │    ├── utils.py            // utils
│   │    └── tools        
│   │        ├── learning.py        
│   │        └── unicode.py       //기타 유니코드
│   └── main.py                   // 실제 main 코드 
└── requirements.txt              // 패키치 설치 파일
```
## 4. 시연 영상

## 5. 설치 및 사용법
1. 구동환경 : pytorch 2.0.1 / CUDA 11.7
2. 패키지 : requirements.txt 참고  
3. 설치  
- 버전에 맞는 pytorch 및 cuda 설치

- 패키지 설치
```
pip install -r requirements.txt
```

4. 사용법
```
python main.py 
```
"텍스트를 입력하세요: " 라는 문구가 나오면, 발음이 궁금한 영단어나 한글/영어 혼용 텍스트를 입력한다.

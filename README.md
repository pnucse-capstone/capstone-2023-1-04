# 지식베이스와 딥러닝을 통한 영어 - 한글 Grapheme-to-Phoneme 모델의 성능 향상 연구

## 1. 프로젝트 소개

한국어와 영어가 혼용된 텍스트를 올바른 발음으로 변환하는 것을 목표로 한다.  
지식베이스와 딥러닝 방식을 결합하여, 기존의 TTS 보다 높은 정확도를 달성하고자 한다. 

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
        <li><a href = "mailto: chhj0319@pusan.ac.kr">chhj0319@pusan.ac.kr</a></li>
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

<p>1. 알파벳 단어 하나만 입력으로 들어올 시, 그대로 알파벳 이름을 출력한다.</p>
<p>2. 지식 베이스에 있는 단어가 입력으로 들어올 시, 지식 베이스에 있는 발음으로 출력한다.</p>
<p>3. 위에 해당하지 않는 대문자로만 이루어진 단어들은 단어마다 알파벳 이름그대로 출력한다. ex)DPICM = 디피아이시엠</p>
<p>4. 위에 해당하지 않는 단어가 입력으로 들어오면, 모델을 사용해서 발음을 출력한다.</p>



### 파일 구조
main 소스 파일 위치와 pretrained model 위치를 명시해놓음
```
source                           // 소스 모음 (Inpainting model clone 위치)
├── bin                          // main program 소스 폴더
│   ├── Enum.py                      // Enum
│   ├── main.py                      // main 소스 파일
│   └── yolov8n-seg.pt               // YOLOv8 segmentation pretrained model
├── deepfillv2                       // Inpainting model : deepfillv2
│   └── pretrained                      // pretrained model 폴더
│       └── states_pt_places2.pth         // deepfillv2 pretrained model (다운로드 해야 함)
├── lama                             // Inpainting model : lama
│   └── big-lama                        // pretrained model 폴더
│       └── models                     
│           └── best.ckpt                 // lama pretrained model (다운로드 해야 함)
│       └── config.yaml                   // lama config 파일
├── MAT                              // Inpainting model : MAT
│   └── pretrained                      // pretrained model 폴더
│       └── Places_512.pkl                // MAT pretrained model (다운로드 해야 함)
└── requirements.txt                // 패키치 설치 파일
```
## 4. 시연 영상

## 5. 설치 및 사용법
1. 구동환경 : pytorch 2.0.1 / CUDA 11.7
2. 패키지 : requirements.txt 참고  
3. 설치  
- 버전에 맞는 pytorch 및 cuda 설치
- 모델 준비 : source 폴더 아래에 clone  
```
git clone https://github.com/advimman/lama.git
git clone https://github.com/nipponjo/deepfillv2-pytorch.git
git clone https://github.com/fenglinglwb/MAT.git
```
레포지토리의 폴더에 있는 파일 복사 붙여넣기

- 패키지 설치
```
pip install -r requirements.txt
conda install ninja
```

- pretrained model : 파일 구조도를 참고하여 배치  
[LaMa](https://github.com/advimman/lama#links) (https://github.com/advimman/lama)  
[Deepfillv2](https://drive.google.com/u/0/uc?id=1tvdQRmkphJK7FYveNAKSMWC6K09hJoyt&export=download) (https://github.com/nipponjo/deepfillv2-pytorch)   
[MAT](https://mycuhk-my.sharepoint.com/personal/1155137927_link_cuhk_edu_hk/_layouts/15/onedrive.aspx?id=%2Fpersonal%2F1155137927%5Flink%5Fcuhk%5Fedu%5Fhk%2FDocuments%2FRelease%2FMAT&ga=1) (https://github.com/fenglinglwb/mat)  

4. 사용법
```
python main.py <<Inpainting Model 이름>>
```
Inpainting Model 이름 : LAMA, DEEPFILLV2, MAT 중 하나를 적는다.

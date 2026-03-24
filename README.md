# Spark ML 실무 발제 - 부동산 가격 예측 프로젝트

## 📋 프로젝트 개요

### 기술 스택

- **Apache Spark**: 3.5.0+
- **PySpark**: Spark Python API
- **Structured Streaming**: 실시간 데이터 처리
- **Docker**: python:3.11 기반 커스텀 이미지 (Dockerfile + docker-compose.yml)
- **Machine Learning**: LinearRegression 모델

### 실습 시나리오

#### Offline Phase (모델 학습)

- 과거 부동산 데이터를 학습하여 선형회귀 모델 생성
- 모델을 PipelineModel 형태로 직렬화하여 저장
- **실행자**: 발제자 (사전 준비)

#### Online Phase (실시간 예측)

- 소켓을 통해 실시간 부동산 정보 수집
- 저장된 모델을 로드하여 즉시 가격 예측

### 데이터 구조

```
입력 피처 (Input Features):
- area: 면적 (m²)
- floor: 층수
- distance_to_station: 역세권 거리 (m)

예측 타겟 (Target):
- price: 주택 가격 (백만원)
```

## 📁 프로젝트 구조

```
Spark-ML/
├── docker-compose.yml          # Docker Compose 설정
├── app/
│   ├── train_model.py           # [Offline] 모델 학습 스크립트
│   ├── predict_housing.py       # [Online] 실시간 예측 스크립트
│   ├── model/                   # 학습된 모델 저장 폴더 (자동 생성)
│   └── data/
│       └── sample_house.csv     # 학습용 샘플 데이터
├── README.md                    # 본 문서
└── .gitignore
```

## 🚀 빠른 시작 (Quick Start)

**가장 빠르게 실습하는 방법:**

```bash
# 1. 프로젝트 클론 및 이동
git clone https://github.com/YOUR_GITHUB/Spark-ML.git
cd Spark-ML

# 2. Docker 컨테이너 시작 (처음 실행이면 --build 권장)
docker-compose up -d --build

# 3. PySpark 셸로 즉시 실습 시작
docker-compose exec spark /bin/bash
pyspark --master local[*]

# 이제 Python 명령어 입력 가능:
>>> df = spark.read.csv("/app/data/sample_house.csv", header=True, inferSchema=True)
>>> df.show()
>>> df.count()
>>> exit()
```

---

## 🚀 상세 설치 및 실행

```bash
git clone https://github.com/YOUR_GITHUB/Spark-ML.git
cd Spark-ML
```

### 2단계: Docker 컨테이너 시작

```bash
docker-compose up -d --build   # 처음 한 번은 --build, 이후에는 생략 가능
```

컨테이너 상태 확인:

```bash
docker-compose ps
```

### 3단계: Offline Phase - 모델 학습

```bash
docker-compose exec spark spark-submit /app/train_model.py
```

**예상 출력**:

```
[INFO] SparkSession 생성 완료
[INFO] 데이터 로드 완료: 10 행
+----+-----+-------------------+-----+
|area|floor|distance_to_station|price|
+----+-----+-------------------+-----+
|45.5|  3.0|              150.0|250.0|
|67.2|  8.0|              200.0|450.0|
...
[INFO] 모델 저장 완료: /app/model
```

### 4단계: Online Phase - 실시간 예측 

이 단계에서는 **컨테이너 안에서 nc 서버를 열고**, 같은 컨테이너 안의 Spark가 그 서버에 붙어서 데이터를 읽습니다. (localhost 기준이 같도록 단순화)

#### Step 4-1: 컨테이너에서 nc 서버 시작 (먼저 실행)

터미널 A (호스트)에서:

```bash
cd Spark-ML
docker-compose exec spark nc -lk 9999
```

이 터미널은 **계속 열어둔 상태에서** 나중에 이 창에 직접 데이터를 입력합니다.

#### Step 4-2: 컨테이너에서 스트리밍 시작

터미널 B (호스트에서 새 터미널)에서:

```bash
cd Spark-ML
docker-compose exec spark spark-submit /app/predict_housing.py
```

**예상 출력**:

```
[INFO] SparkSession 생성 완료
[INFO] 모델 로드 완료 ✓
[INFO] 소켓 스트림 생성 완료 (localhost:9999)
[INFO] 데이터 파싱 완료
[INFO] 예측 파이프라인 구성 완료
[INFO] 스트리밍 시작...
[INFO] 컨테이너 nc 터미널(docker-compose exec spark nc -lk 9999)에서 데이터를 입력하세요
```

#### Step 4-3: nc 터미널에서 데이터 입력

다시 터미널 A (nc -lk 9999가 떠 있는 곳)로 돌아가서, 한 줄씩 입력 후 Enter:

```text
84,15,300⏎
120,8,100⏎
52.3,5,250⏎
```

##### Windows 사용자

**Option 1: ncat 사용** (nmap에 포함됨)

```powershell
# ncat 설치 위치 예: C:\Program Files (x86)\Nmap\ncat.exe
# 또는 PATH에 추가했으면 바로 사용 가능

echo "84,15,300" | ncat localhost 9999
echo "120,8,100" | ncat localhost 9999
echo "52.3,5,250" | ncat localhost 9999
```

**Option 2: PowerShell로 직접 전송**

```powershell
# PowerShell에서 TCP 연결
$stream = New-Object System.Net.Sockets.TcpClient
$stream.Connect("localhost", 9999)
$writer = New-Object System.IO.StreamWriter($stream.GetStream())
$writer.WriteLine("84,15,300")
$writer.Flush()
$writer.Close()
$stream.Close()
```

**Option 3: WSL (Windows Subsystem for Linux) 사용**

WSL 환경에서 Mac 명령어와 동일하게 사용 가능:

```bash
echo "84,15,300" | nc localhost 9999
```

### 5단계: 결과 확인

스트리밍 서버 콘솔에서 예측 결과 확인:

```
+--------+----+-------+--------+
|면적(m²)|층수|역거리(m)|예상가격(백만원)|
+--------+----+-------+--------+
|84.0    |15.0|300.0  |573.45  |
+--------+----+-------+--------+

+--------+----+-------+--------+
|면적(m²)|층수|역거리(m)|예상가격(백만원)|
+--------+----+-------+--------+
|120.0   |8.0 |100.0  |702.34  |
+--------+----+-------+--------+
```

## 💡 핵심 학습 포인트

### 🎯 주요 3가지 사용법

#### 방법 1️⃣: spark-submit (배치 실행)

```bash
docker-compose exec spark spark-submit /app/train_model.py
```

- **용도**: 전체 파이프라인 자동 실행, 프로덕션 배포
- **장점**: 파일 만들 필요 없음, 가장 간단

#### 방법 2️⃣: PySpark 셸 (대화형 실습) ⭐ 추천

```bash
docker-compose exec spark /bin/bash
pyspark --master local[*]
```

- **용도**: 빠른 데이터 탐색, 즉시 피드백
- **장점**: 한 줄씩 입력 가능, 학습에 최적

#### 방법 3️⃣: 커스텀 Python 스크립트 (유연함)

```bash
# /app/custom_analysis.py 작성 후
docker-compose exec spark spark-submit /app/custom_analysis.py
```

- **용도**: 복잡한 분석, 코드 재사용
- **장점**: 파일로 저장되어 재현 가능

---

### 1. Pipeline 패턴

```python
# 전처리 + 모델을 하나의 파이프라인으로 관리
pipeline = Pipeline(stages=[
    VectorAssembler(...),    # 특성 벡터화
    LinearRegression(...)    # 모델
])

pipelineModel = pipeline.fit(df)  # 학습
pipelineModel.save(path)          # 저장

# 나중에 동일한 전처리 자동 적용
predictions = pipelineModel.transform(new_data)
```

### 2. Structured Streaming

```python
# 소켓에서 데이터 스트림 생성
df_stream = spark.readStream.format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

# 스트림에 변환 적용
result = pipelineModel.transform(df_stream)

# 결과를 실시간으로 출력
query = result.writeStream \
    .format("console") \
    .outputMode("append") \
    .start()

query.awaitTermination()  # 계속 실행
```

### 3. split() 함수로 데이터 파싱

```python
from pyspark.sql.functions import col, split

# 입력: "84,15,300"
# 출력: [84, 15, 300] (배열)
df_parsed = df_raw.select(
    split(col("value"), ",").alias("data")
).select(
    col("data")[0].cast("double").alias("area"),
    col("data")[1].cast("double").alias("floor"),
    col("data")[2].cast("double").alias("distance_to_station")
)
```

## 🛠️ 트러블슈팅

### 문제 1: "모델 로드 실패" 에러

**해결 방법**:

1. `train_model.py`를 먼저 실행했는지 확인
2. `app/model` 폴더가 생성되었는지 확인
   ```bash
   docker-compose exec spark ls -la /app/model
   ```

### 문제 2: 소켓 연결 안 됨

**Mac에서**:

```bash
# nc 설치 확인
which nc

# 설치되지 않았으면
brew install netcat

# 또는 macOS 기본 nc 사용
echo "84,15,300" | nc localhost 9999
```

**Windows에서**:

```powershell
# ncat 경로 확인
where ncat

# 없으면 nmap 설치
# https://nmap.org/download.html
```

### 문제 3: Docker 컨테이너 연결 문제

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs spark

# 컨테이너 재시작
docker-compose restart spark
```

### 문제 4: 포트 4040이 이미 사용 중

```bash
# docker-compose.yml의 포트 변경
# 기존: "4040:4040"
# 변경: "4041:4040"  (또는 다른 포트)
```

## 📊 Spark Web UI 접속

- **Spark Master UI**: http://localhost:8080
- **Spark Application UI**: http://localhost:4040

## 🧹 정리

스트리밍 중단:

```bash
# Ctrl+C로 스트리밍 종료
```

컨테이너 정지:

```bash
docker-compose down
```

전체 정리 (이미지 포함):

```bash
docker-compose down -v
```

## 📝 코드 구조 설명

### train_model.py 플로우

1. SparkSession 생성
2. CSV 데이터 로드 (`/app/data/sample_house.csv`)
3. VectorAssembler로 특성 벡터화
4. LinearRegression 모델 정의
5. Pipeline 구성
6. 모델 학습 (fit)
7. 학습 결과 검증
8. 모델 저장 (`/app/model/`)

### predict_housing.py 플로우

1. SparkSession 생성
2. 저장된 모델 로드 (`/app/model/`)
3. 소켓으로부터 데이터 스트림 생성
4. split() 함수로 문자열 파싱
5. 모델로 예측 수행
6. 결과를 콘솔에 실시간 출력

## 💾 파일 수정 및 반영

**로컬 머신에서 수정하면 자동 반영됩니다!**

```bash
# 로컬 에디터에서 app/train_model.py 수정 후 저장
# → docker-compose.yml의 volume 설정으로 자동 동기화

# 컨테이너에서 즉시 수정사항 확인
docker-compose exec spark spark-submit /app/train_model.py
```

## 🔧 유용한 팁

### 💡 Tip 1: 완전 초기화

```bash
# 컨테이너 종료 및 모든 변경사항 제거
docker-compose down -v
# 다시 시작
docker-compose up -d
```

### 💡 Tip 2: 컨테이너 셸 접속

```bash
docker-compose exec spark /bin/bash
# 이 안에서 ls, cd, vi 등 모든 명령어 사용 가능
```

### 💡 Tip 3: 스트리밍 테스트 (자동화)

```bash
# 한 터미널에서 스트리밍 시작
docker-compose exec spark spark-submit /app/predict_housing.py

# 다른 터미널에서 반복 데이터 전송
for i in {1..5}; do
  echo "84,15,300" | nc localhost 9999
  sleep 1
done
```

## 🎓 심화 학습 과제

1. **Accuracy 개선**: 데이터셋 증가 및 모델 파라미터 튜닝
2. **다양한 모델 시도**:
   - DecisionTreeRegressor
   - RandomForestRegressor
   - GBTRegressor
3. **실제 데이터 활용**: Kaggle 부동산 데이터셋 사용
4. **배포**: Kafka 연동, 실제 웹서비스 구축

## 📌 참고 자료

- [Apache Spark 공식 문서](https://spark.apache.org/docs/)
- [PySpark SQL Functions](https://spark.apache.org/docs/latest/api/python/reference/pyspark.sql/functions.html)
- [Structured Streaming Programming Guide](https://spark.apache.org/docs/latest/structured-streaming-programming-guide.html)
- [MLlib: Main Guide](https://spark.apache.org/docs/latest/ml-guide.html)

## ℹ️ 버전 정보

| 항목             | 기존                                     | 현재                             |
| ---------------- | ---------------------------------------- | -------------------------------- |
| Docker 이미지    | `jupyter/pyspark-notebook:latest` (5GB+) | `bitnami/pyspark:latest` (1.5GB) |
| 마운트 경로      | `/home/jovyan/app`                       | `/app`                           |
| 포함 내용        | Jupyter, Spark, Python                   | Spark, Python (최소 구성)        |
| 이미지 크기 감소 | -                                        | **약 70% 축소** ✅               |

## ✅ 프로젝트 평가

- ✅ 가벼운 이미지: 빠른 다운로드 & 실행
- ✅ 경로 단순화: 오타 감소
- ✅ 다양한 학습 방법: spark-submit, PySpark 셸, 커스텀 스크립트
- ✅ 실시간 스트리밍: 완전한 ML 파이프라인 경험
- ✅ 자동 볼륨 동기화: 로컬 수정 즉시 반영

---

MIT License

## ✉️ 문의

이 프로젝트 관련 질문이나 개선 사항은 Issue를 통해 남겨주세요.

---

**Happy Learning! 🚀**

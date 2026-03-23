# Spark ML 실무 발제 - 부동산 가격 예측 프로젝트

30분 분량의 실무 중심 Spark ML 교육 프로젝트입니다. 실시간 데이터 스트리밍으로 머신러닝 모델을 활용하는 전체 파이프라인을 경험할 수 있습니다.

## 📋 프로젝트 개요

### 기술 스택

- **Apache Spark**: 3.5.0
- **PySpark**: Spark Python API
- **Structured Streaming**: 실시간 데이터 처리
- **Docker**: Bitnami Spark 컨테이너
- **Machine Learning**: LinearRegression 모델

### 실습 시나리오

#### Offline Phase (모델 학습)

- 과거 부동산 데이터를 학습하여 선형회귀 모델 생성
- 모델을 PipelineModel 형태로 직렬화하여 저장
- **실행자**: 발제자 (사전 준비)

#### Online Phase (실시간 예측)

- 소켓을 통해 실시간 부동산 정보 수집
- 저장된 모델을 로드하여 즉시 가격 예측
- **실행자**: 수강생 (실습)

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

## 🚀 설치 및 실행

### 1단계: 프로젝트 클론

```bash
git clone https://github.com/YOUR_GITHUB/Spark-ML.git
cd Spark-ML
```

### 2단계: Docker 컨테이너 시작

```bash
docker-compose up -d
```

컨테이너 상태 확인:

```bash
docker-compose ps
```

### 3단계: Offline Phase - 모델 학습

**발제자가 실행** (수강생 실습 전에 미리 준비)

```bash
docker-compose exec spark spark-submit /home/spark/app/train_model.py
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
[INFO] 모델 저장 완료: /home/spark/app/model
```

### 4단계: Online Phase - 실시간 예측 (수강생 실습)

#### Step 4-1: 스트리밍 서버 시작

```bash
docker-compose exec spark spark-submit /home/spark/app/predict_housing.py
```

**예상 출력**:

```
[INFO] SparkSession 생성 완료
[INFO] 모델 로드 완료 ✓
[INFO] 소켓 스트림 생성 완료 (localhost:9999)
[INFO] 데이터 파싱 완료
[INFO] 예측 파이프라인 구성 완료
[INFO] 스트리밍 시작...
[INFO] 다른 터미널에서 다음 명령어로 데이터를 전송하세요:
       echo '84,15,300' | nc localhost 9999
```

#### Step 4-2: 다른 터미널에서 데이터 전송

**⚠️ 새로운 터미널 창을 열어서 진행**

##### Mac 사용자

```bash
# nc (netcat) 설치 (이미 설치되어 있을 가능성 높음)
# 없으면: brew install netcat

# 데이터 전송
echo "84,15,300" | nc localhost 9999
echo "120,8,100" | nc localhost 9999
echo "52.3,5,250" | nc localhost 9999
```

또는 여러 줄을 한 번에 전송:

```bash
(echo "84,15,300"; echo "120,8,100"; echo "52.3,5,250") | nc localhost 9999
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
   docker-compose exec spark ls -la /home/spark/app/model
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
2. CSV 데이터 로드
3. VectorAssembler로 특성 벡터화
4. LinearRegression 모델 정의
5. Pipeline 구성
6. 모델 학습 (fit)
7. 학습 결과 검증
8. 모델 저장

### predict_housing.py 플로우

1. SparkSession 생성
2. 저장된 모델 로드
3. 소켓으로부터 데이터 스트림 생성
4. split() 함수로 문자열 파싱
5. 모델로 예측 수행
6. 결과를 콘솔에 실시간 출력

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

## 📄 라이선스

MIT License

## ✉️ 문의

이 프로젝트 관련 질문이나 개선 사항은 Issue를 통해 남겨주세요.

---

**Happy Learning! 🚀**

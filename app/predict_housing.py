"""
[Online Phase] 실시간 부동산 가격 예측 스트리밍 스크립트
========================================================

목적: 소켓을 통해 유입되는 실시간 부동산 정보를 받아서
      미리 학습된 모델로 가격을 예측합니다.

데이터 포맷: "area,floor,distance_to_station"
  예) "84,15,300" -> 면적: 84m², 층수: 15층, 역거리: 300m

실행 방식:
  docker-compose exec spark spark-submit /app/predict_housing.py

데이터 공급 (Mac):
  nc -l 9999  # 서버 시작 후, 아래 명령어 실행

데이터 공급 (다른 터미널, Mac):
  echo "84,15,300" | nc localhost 9999
  echo "120,8,100" | nc localhost 9999
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, split, from_json
from pyspark.ml import PipelineModel
from pyspark.sql.types import StructType, StructField, DoubleType
import sys

# ============================================================================
# 1단계: SparkSession 생성 (Streaming 지원)
# ============================================================================
spark = SparkSession.builder \
    .appName("RealEstate_Streaming_Prediction") \
    .master("local[*]") \
    .config("spark.sql.streaming.schemaInference", "true") \
    .getOrCreate()

# 로그 레벨 설정 (덜 verbose하게)
spark.sparkContext.setLogLevel("WARN")

print("[INFO] SparkSession 생성 완료")

# ============================================================================
# 2단계: 학습된 모델 로드
# ============================================================================
model_path = "/app/model"
print(f"[INFO] 모델 로드 시작: {model_path}")

try:
    pipelineModel = PipelineModel.load(model_path)
    print("[INFO] 모델 로드 완료 ✓")
except Exception as e:
    print(f"[ERROR] 모델 로드 실패: {e}")
    print("[ERROR] train_model.py를 먼저 실행하세요!")
    sys.exit(1)

# ============================================================================
# 3단계: 소켓에서 데이터 읽기 (Structured Streaming)
# ============================================================================
# 컨테이너 내부 localhost:9999에서 텍스트 데이터를 읽습니다.
# (같은 컨테이너 안에서 `nc -lk 9999` 로 열어둔 서버에 접속)

df_raw = spark.readStream \
    .format("socket") \
    .option("host", "localhost") \
    .option("port", 9999) \
    .load()

print("[INFO] 소켓 스트림 생성 완료 (localhost:9999)")

# ============================================================================
# 4단계: 데이터 파싱 (split 함수 사용)
# ============================================================================
# 입력: "84,15,300"을 split(",")로 나누어 배열로 변환
# 추출: array[0]=area, array[1]=floor, array[2]=distance_to_station

df_parsed = df_raw.select(
    # value 컬럼 (소켓으로부터 받은 문자열)을 ","으로 분리
    split(col("value"), ",").alias("data")
).select(
    # 분리된 배열의 각 요소를 컬럼으로 추출 (인덱스는 0부터 시작)
    col("data")[0].cast("double").alias("area"),              # 면적
    col("data")[1].cast("double").alias("floor"),             # 층수
    col("data")[2].cast("double").alias("distance_to_station") # 역세권 거리
)

print("[INFO] 데이터 파싱 완료")

# ============================================================================
# 5단계: 모델을 사용하여 예측
# ============================================================================
# pipelineModel.transform()은 다음을 자동으로 수행합니다:
#   1. features 벡터 생성 (VectorAssembler)
#   2. 선형회귀 모델로 예측 (prediction 컬럼 추가)

df_predictions = pipelineModel.transform(df_parsed)

print("[INFO] 예측 파이프라인 구성 완료")

# ============================================================================
# 6단계: 결과 출력 (console sink)
# ============================================================================
# 예측 결과를 콘솔에 실시간으로 출력합니다

query = df_predictions.select(
    col("area").alias("면적(m²)"),
    col("floor").alias("층수"),
    col("distance_to_station").alias("역거리(m)"),
    col("prediction").alias("예상가격(백만원)")
).writeStream \
    .format("console") \
    .option("truncate", False) \
    .option("numRows", 20) \
    .outputMode("append") \
    .start()

print("[INFO] 스트리밍 시작...")
print("[INFO] 다른 터미널에서 다음 명령어로 데이터를 전송하세요:")
print("       echo '84,15,300' | nc localhost 9999")
print()

# ============================================================================
# 7단계: 스트리밍 계속 실행
# ============================================================================
# 스트리밍은 사용자가 종료할 때까지 계속 실행됩니다 (Ctrl+C)

try:
    query.awaitTermination()
except KeyboardInterrupt:
    print("\n[INFO] 스트리밍 종료")
    spark.stop()

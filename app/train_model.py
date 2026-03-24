"""
[Offline Phase] 부동산 가격 예측 모델 학습 스크립트
=================================================

목적: 과거 부동산 데이터를 가지고 PipelineModel을 생성하고 저장합니다.
      이 모델은 predict_housing.py에서 실시간 예측에 사용됩니다.

실행 방식:
  docker-compose exec spark spark-submit /app/train_model.py

출력:
  - app/model/ 폴더에 PipelineModel 저장
"""

from pyspark.sql import SparkSession
from pyspark.ml import Pipeline
from pyspark.ml.feature import VectorAssembler
from pyspark.ml.regression import LinearRegression
from pyspark.sql.types import StructType, StructField, DoubleType
import os

# ============================================================================
# 1단계: SparkSession 생성
# ============================================================================
spark = SparkSession.builder \
    .appName("RealEstate_Model_Training") \
    .master("local[*]") \
    .getOrCreate()

print("[INFO] SparkSession 생성 완료")

# ============================================================================
# 2단계: 샘플 부동산 데이터 로드
# ============================================================================
# 데이터 구조: area(면적), floor(층수), distance_to_station(역세권 거리) -> price(가격)
schema = StructType([
    StructField("area", DoubleType()),           # 평방미터 단위 면적
    StructField("floor", DoubleType()),          # 층수
    StructField("distance_to_station", DoubleType()),  # km 단위 역까지의 거리
    StructField("price", DoubleType())           # 백만원 단위 가격
])

# CSV 파일 로드
df = spark.read.schema(schema).csv(
    "/app/data/sample_house.csv",
    header=True
)

print(f"[INFO] 데이터 로드 완료: {df.count()} 행")
df.show(5)

# ============================================================================
# 3단계: 특성 벡터화 (Feature Engineering)
# ============================================================================
# 입력 특성: area, floor, distance_to_station
# 출력 컬럼: features (벡터화된 특성들)
# 라벨: price (예측할 target)

assembler = VectorAssembler(
    inputCols=["area", "floor", "distance_to_station"],
    outputCol="features"
)

print("[INFO] VectorAssembler 생성 완료")

# ============================================================================
# 4단계: 선형 회귀 모델 생성
# ============================================================================
lr = LinearRegression(
    featuresCol="features",
    labelCol="price",
    maxIter=100,
    regParam=0.01,
    elasticNetParam=0.0  # L2 정규화만 사용 (Ridge Regression)
)

print("[INFO] LinearRegression 모델 생성 완료")

# ============================================================================
# 5단계: Pipeline 구성
# ============================================================================
# Pipeline은 데이터 전처리와 모델을 함께 관리합니다.
# 이렇게 하면 나중에 새로운 데이터에 대해 동일한 전처리를 자동으로 적용할 수 있습니다.

pipeline = Pipeline(stages=[
    assembler,      # Stage 1: 특성 벡터화
    lr              # Stage 2: 모델 학습/예측
])

print("[INFO] Pipeline 구성 완료")

# ============================================================================
# 6단계: 모델 학습
# ============================================================================
pipelineModel = pipeline.fit(df)

print("[INFO] 모델 학습 완료")

# ============================================================================
# 7단계: 학습된 모델 검증 (선택사항)
# ============================================================================
predictions = pipelineModel.transform(df)
predictions.select("area", "floor", "distance_to_station", "price", "prediction").show(5)

# ============================================================================
# 8단계: 모델 저장
# ============================================================================
model_path = "/app/model"

# 기존 모델이 있으면 삭제
import shutil
if os.path.exists(model_path):
    shutil.rmtree(model_path)
    print(f"[INFO] 기존 {model_path} 삭제")

# 모델 저장
pipelineModel.save(model_path)
print(f"[INFO] 모델 저장 완료: {model_path}")

# ============================================================================
# 종료
# ============================================================================
spark.stop()
print("[INFO] SparkSession 종료")


import geopandas as gpd
from pathlib import Path

# 프로젝트 경로
BASE_DIR = Path(__file__).resolve().parent

INPUT_PATH = (
    BASE_DIR / "data" / "processed"
    / "지역별_지원우선순위_지도.geojson"
)

OUTPUT_PATH = (
    BASE_DIR / "data" / "processed"
    / "지역별_지원우선순위_지도_간소화.geojson"
)

print("원본 지도 데이터 불러오는 중...")

gdf = gpd.read_file(INPUT_PATH)

print("원본 행 개수:", len(gdf))
print("원본 CRS:", gdf.crs)

# 1. 좌표 단순화 (EPSG:5179는 미터 단위)
gdf["geometry"] = gdf.geometry.simplify(
    tolerance=100,
    preserve_topology=True
)

# 2. 지도에 필요한 컬럼만 유지
map_gdf = gdf[
    [
        "시도",
        "시군구",
        "SIGUNGU_CD",
        "지원_우선순위_점수",
        "지원_우선순위_등급",
        "geometry"
    ]
].copy()

# 3. 지도 라이브러리에서 사용할 좌표계로 변환
map_gdf = map_gdf.to_crs(epsg=4326)

# 4. 지역 코드 문자열 통일
map_gdf["SIGUNGU_CD"] = map_gdf["SIGUNGU_CD"].astype(str)

# 5. 간소화 파일 저장
map_gdf.to_file(
    OUTPUT_PATH,
    driver="GeoJSON",
    encoding="utf-8"
)

print("간소화 완료!")
print("지역 개수:", len(map_gdf))
print(
    "새 파일 크기:",
    round(OUTPUT_PATH.stat().st_size / (1024 ** 2), 2),
    "MB"
)

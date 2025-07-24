Peek&amp;Pick 상품 이미지 webp 변환 코드
---
1. PostgreSQL의 tbl_product 테이블에서 product_id, barcode, img_url을 조회한다.

2. img_url에 명시된 외부 이미지 주소(URL)에서 이미지를 다운로드한다.

3. 다운로드한 이미지를 WebP 형식으로 변환한다.

4. 본문 이미지: 무손실(lossless=True), 원본 크기 그대로 저장

5. 썸네일 이미지: 최대 크기 300x300으로 축소, quality=92로 손실 압축 저장

6. 변환된 이미지는 로컬 경로에 저장한다.

7. 본문 이미지: C:/nginx-1.26.3/html/products/pp-<barcode>.webp

8. 썸네일 이미지: C:/nginx-1.26.3/html/product_thumbnail/pp-<barcode>-thumb.webp

9. 기존 테이블과 동일한 구조의 tbl_product2를 새로 생성한 뒤, 변환된 이미지 경로를 다음과 같이 업데이트한다:
img_url: 본문 이미지의 로컬 상대경로 (/products/pp-<barcode>.webp)
img_thumb_url: 썸네일 이미지의 로컬 상대경로 (/product_thumbnail/pp-<barcode>-thumb.webp)

10. 변환 실패 시 convert_failed_products.txt에 product_id, barcode, 예외 타입을 기록한다.

import os
import requests
from io import BytesIO
from PIL import Image
import psycopg2

# === DB 연결 정보 ===
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "peek_pick_db"
DB_USER = "ppdbuser"
DB_PASSWORD = "ppdbuser"

# === 이미지 저장 경로 ===
IMG_MAIN_DIR = r"C:\nginx-1.26.3\html\products"
IMG_THUMB_DIR = r"C:\nginx-1.26.3\html\product_thumbnail"
LOG_FILE = "convert_failed_products.txt"

os.makedirs(IMG_MAIN_DIR, exist_ok=True)
os.makedirs(IMG_THUMB_DIR, exist_ok=True)

def convert_images(product_id, barcode, img_url, fail_log):
    try:
        response = requests.get(img_url, timeout=20)
        response.raise_for_status()

        original_size = len(response.content)
        image = Image.open(BytesIO(response.content)).convert("RGBA")  # 무조건 RGBA로 처리
        width, height = image.size

        # 본문 이미지: 무손실 저장
        main_filename = f"pp-{barcode}.webp"
        main_path = os.path.join(IMG_MAIN_DIR, main_filename)
        image.save(main_path, format="WEBP", lossless=True)
        main_url = f"/products/{main_filename}"

        # 썸네일 이미지: 고품질 lossy 저장
        thumb_filename = f"pp-{barcode}-thumb.webp"
        thumb_path = os.path.join(IMG_THUMB_DIR, thumb_filename)
        thumbnail = image.copy()
        thumbnail.thumbnail((300, 300))
        thumb_quality = 92
        thumbnail.save(thumb_path, format="WEBP", quality=thumb_quality)
        thumb_url = f"/product_thumbnail/{thumb_filename}"

        return main_url, thumb_url
    except Exception as e:
        print(f"[ERROR] {product_id} 변환 실패: {e}")
        fail_log.write(f"{product_id},{barcode},{type(e).__name__}\n")
        return None, None

def create_tbl_product2(cursor):
    cursor.execute("""
        DROP TABLE IF EXISTS tbl_product2;
        CREATE TABLE tbl_product2 AS
        SELECT * FROM tbl_product;
    """)
    print("[INFO] tbl_product2 생성 완료")

def update_tbl_product2(conn, cursor):
    cursor.execute("""
        SELECT product_id, barcode, img_url 
        FROM tbl_product 
        WHERE product_id BETWEEN 1 AND 9707
    """)
    rows = cursor.fetchall()

    with open(LOG_FILE, "w", encoding="utf-8") as fail_log:
        for product_id, barcode, img_url in rows:
            if not img_url:
                continue
            print(f"[INFO] 처리 중: {product_id} ({barcode})")
            main_url, thumb_url = convert_images(product_id, barcode, img_url, fail_log)
            if main_url and thumb_url:
                cursor.execute("""
                    UPDATE tbl_product2
                    SET img_url = %s,
                        img_thumb_url = %s
                    WHERE product_id = %s
                """, (main_url, thumb_url, product_id))
                conn.commit()
            else:
                print(f"[SKIP] {product_id} 실패")

def main():
    conn = psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )
    cursor = conn.cursor()
    create_tbl_product2(cursor)
    update_tbl_product2(conn, cursor)
    cursor.close()
    conn.close()
    print("[DONE] 변환 및 tbl_product2 저장 완료")

if __name__ == "__main__":
    main()

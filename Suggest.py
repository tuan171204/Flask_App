from Flask_App import app, db
import sqlalchemy as sa
from flask import session
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from Flask_App.models import Receipt, ReceiptDetail
import random

def combineFeatures(row):
    return str(row['price']) + " " + row['name'] + " " + str(row['category_id'])


def recommendSimilarProducts(product_id, NUMBER = 0):
    with (app.app_context()):
        engine = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])

        table_name = "product"

        df_products = pd.read_sql_table(table_name, engine)

        df_products['combinedFeatures'] = df_products.apply(combineFeatures, axis=1)
        tf = TfidfVectorizer()
        tfMatrix = tf.fit_transform(df_products['combinedFeatures'])

        product_info = df_products[df_products['id'] == product_id]

            # Kết hợp mô tả và giá thành sản phẩm
        combinedFeatures = str(product_info['price'].values[0]) + " " \
                               + product_info['name'].values[0] + " "\
                               + str(product_info['category_id'].values[0])

            # Chuyển đổi chuỗi kết hợp thành vector TF-IDF
        productVector = tf.transform([combinedFeatures])

            # Tính toán độ tương đồng cosine giữa sản phẩm tham chiếu và các sản phẩm khác
        cosineSimilarities = cosine_similarity(productVector, tfMatrix)

            # Lấy ID và độ tương đồng của các sản phẩm tương tự
        similarProducts = []
        for i, similarity in enumerate(cosineSimilarities[0]):
            if i != product_id and similarity >= 0:  # Loại trừ sản phẩm tham chiếu và chỉ chọn sản phẩm có độ tương đồng > 0
                    similarProducts.append((df_products.loc[i]['id'], similarity))

            # Sắp xếp các sản phẩm tương tự theo độ tương đồng giảm dần
        sortedSimilarProducts = sorted(similarProducts, key=lambda x: x[1], reverse=True)

            # Lấy ID của các sản phẩm tương tự hàng đầu
        topNProductIDs = [product_id for product_id, similarity in sortedSimilarProducts[:NUMBER]]

            # Lấy thông tin và hiển thị tên của các sản phẩm tương tự hàng đầu
        return topNProductIDs



# TỪ ĐÂY TRỞ XUỐNG CHƯA HOÀN THÀNH< KHOAN THÊM VÔ PPT, CHỈ LÀ CHỨC NĂNG MỞ RỘNG THOI NÊN KO SAO
def has_user(receipts, user_id):
    for receipt in receipts:
        if receipt.user_id == user_id:
            return True
    return False


def get_random_elements(my_set, sample_size=8):
  if sample_size > len(my_set):
    return None

  return random.sample(list(my_set), sample_size)


def recommend_similar_products(product_ids, number=4):
    recommended_products = []
    for product_id in product_ids:
        # Gọi hàm đề xuất sản phẩm tương tự cho từng product_id
        similar_products = recommendSimilarProducts(product_id, NUMBER=number)
        for product in similar_products:
            recommended_products.append(product)

    # Loại bỏ sản phẩm trùng lặp và giới hạn số lượng
    recommended_products = set(recommended_products)

    return recommended_products


def recommend_products_by_user_receipt(user_id):
    # Lấy danh sách product_id từ các hóa đơn của user
    # Lấy id các hóa đơn của user_id
    user_receipts = [receipts.id for receipts in Receipt.query.filter(Receipt.user_id.__eq__(user_id)).all()]

    user_purchased_product = [receipt_detail.product_id for receipt_detail in ReceiptDetail.query.filter(ReceiptDetail.receipt_id.in_(user_receipts)) ]
    # Lấy danh sách product_id được đề xuất
    recommended_product_ids = recommend_similar_products(
        user_purchased_product, number=6
    )


    recommended_product_ids = set(recommended_product_ids) - set(user_purchased_product)

    # Trả về danh sách product_id được đề xuất (tối đa 12 sản phẩm)
    recommended_product_ids = get_random_elements(recommended_product_ids)
    if recommended_product_ids == None:
        return None

    return list(recommended_product_ids)










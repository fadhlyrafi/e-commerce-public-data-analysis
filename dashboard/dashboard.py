import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Membaca data (pastikan Anda sudah memiliki file data yang sesuai)
customers_df = pd.read_csv("data/customers_dataset.csv")
geolocation_df = pd.read_csv("data/geolocation_dataset.csv")
order_items_df = pd.read_csv("data/order_items_dataset.csv")
order_payments_df = pd.read_csv("data/order_payments_dataset.csv")
order_reviews_df = pd.read_csv("data/order_reviews_dataset.csv")
orders_df = pd.read_csv("data/orders_dataset.csv")
category_df = pd.read_csv("data/product_category_name_translation.csv")
product_df = pd.read_csv("data/products_dataset.csv")
sellers_df = pd.read_csv("data/sellers_dataset.csv")

# --- Data Processing ---
order_items_df['shipping_limit_date'] = pd.to_datetime(order_items_df['shipping_limit_date'])
order_items_df['month'] = order_items_df['shipping_limit_date'].dt.strftime('%B')
order_items_df['year'] = order_items_df['shipping_limit_date'].dt.year
order_items_df['month_num'] = order_items_df['shipping_limit_date'].dt.month

# Mengelompokkan data berdasarkan tahun, bulan, dan menghitung total penjualan per bulan
monthly_sales_df = order_items_df.groupby(['year', 'month_num', 'month']).agg({
    "price": "sum",
    "freight_value": "sum",
    "order_id": "nunique"  # Menghitung jumlah order unik
}).reset_index()

monthly_sales_df['month_year'] = monthly_sales_df['month'] + ' ' + monthly_sales_df['year'].astype(str)
monthly_sales_df.sort_values(by=['year', 'month_num'], inplace=True)

# --- Streamlit Dashboard ---
st.title('Sales Dashboard')

# --- Menambahkan Kotak untuk Total Order dan Total Sales ---
total_orders = monthly_sales_df['order_id'].sum()
total_sales = monthly_sales_df['price'].sum()

# Menambahkan kotak dengan CSS untuk menambah kesan visual
st.markdown(
    """
    <style>
        .box {
            padding: 20px;
            border-radius: 10px;
            background-color: #f4f4f9;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }
        .box-title {
            font-size: 18px;
            color: #444444;
            margin-bottom: 10px;
        }
        .box-content {
            font-size: 24px;
            font-weight: bold;
            color: #2e5bff;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Menampilkan Total Order dan Total Sales dalam dua kolom dengan kotak
col1, col2 = st.columns(2)

with col1:
    with st.container():  # Menambahkan container untuk membungkus elemen
        st.markdown("<div style='background-color:#f0f0f5; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);'><h4>Total Orders</h4><h3>{:,}</h3></div>".format(total_orders), unsafe_allow_html=True)

with col2:
    with st.container():  # Menambahkan container untuk membungkus elemen
        st.markdown("<div style='background-color:#f0f0f5; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);'><h4>Total Sales</h4><h3>${:,.2f}</h3></div>".format(total_sales), unsafe_allow_html=True)


# Visualisasi perkembangan penjualan per bulan
st.markdown("<br><br>", unsafe_allow_html=True)
st.header(f"Total Sales Per Month by Year")
# --- Filtering Sales by Year ---
# Menambahkan pilihan untuk memilih tahun tertentu atau "All Years"
selected_year = st.selectbox('Select Year:', ['All Years'] + list(monthly_sales_df['year'].unique()))

# Menyaring data berdasarkan pilihan tahun
if selected_year == 'All Years':
    filtered_sales = monthly_sales_df
else:
    filtered_sales = monthly_sales_df[monthly_sales_df['year'] == selected_year]

# Membuat Line Chart berdasarkan data yang sudah difilter
st.subheader(f"Sales Data for Year {selected_year}" if selected_year != 'All Years' else "Sales Data for All Years")

# Plot Line Chart untuk penjualan berdasarkan bulan dan tahun
fig, ax = plt.subplots(figsize=(10, 5))

for year in filtered_sales['year'].unique():
    ax.plot(
        filtered_sales[filtered_sales['year'] == year]['month_year'],
        filtered_sales[filtered_sales['year'] == year]['price'],
        marker='o', linewidth=2, label=str(year)
    )

ax.set_title(f"", fontsize=20)
ax.set_xlabel("Month", fontsize=12)
ax.set_ylabel("Total Sales", fontsize=12)
ax.set_xticklabels(filtered_sales['month_year'], rotation=90, fontsize=10)
ax.legend(title='Year')
ax.grid()

st.pyplot(fig)


st.markdown("<br><br>", unsafe_allow_html=True)
# --- Data Processing ---
# Menggabungkan data antara order_items_df dan product_df berdasarkan product_id
merged_df = pd.merge(order_items_df, product_df, on='product_id', how='inner')

# Menghitung jumlah order untuk setiap kategori
category_order_count = merged_df.groupby('product_category_name')['order_item_id'].count()

# Mengurutkan kategori berdasarkan jumlah order terbanyak dan menampilkan 5 teratas
top_5_categories = category_order_count.sort_values(ascending=False).head(5)

# Membuat DataFrame untuk menampilkan hasil dalam format tabel
top_5_categories_df = top_5_categories.reset_index()

# Menambahkan kolom ranking
top_5_categories_df['ranking'] = top_5_categories_df.index + 1

# Mengatur kolom agar sesuai dengan urutan yang diinginkan
top_5_categories_df = top_5_categories_df[['ranking', 'product_category_name', 'order_item_id']]
top_5_categories_df.rename(columns={'order_item_id': 'total_item_sold'}, inplace=True)

# --- Tabel Hasil ---
st.subheader("Top 5 Product Categories by Total Items Sold")

# Menyiapkan data untuk bar chart
plt.figure(figsize=(10, 6))

# Menggunakan seaborn untuk membuat bar chart
sns.barplot(x='product_category_name', y='total_item_sold', hue='product_category_name', 
            data=top_5_categories_df, palette='crest', legend=False)

# Menambahkan judul dan label sumbu
plt.title('', fontsize=16)
plt.xlabel('Product Category', fontsize=12)
plt.ylabel('Total Items Sold', fontsize=12)

# Menambahkan grid untuk visualisasi yang lebih jelas
plt.grid(True, axis='y', linestyle='--', alpha=0.7)

# Menampilkan chart
plt.tight_layout()
st.pyplot(plt)


st.markdown("<br><br>", unsafe_allow_html=True)
# --- Data Processing ---
# Menggabungkan tabel order_reviews dan orders berdasarkan order_id
reviews_orders = pd.merge(order_reviews_df, orders_df, on='order_id', how='inner')

# Menggabungkan tabel reviews_orders dengan order_items berdasarkan order_id
reviews_orders_items = pd.merge(reviews_orders, order_items_df, on='order_id', how='inner')

# Menggabungkan tabel reviews_orders_items dengan products berdasarkan product_id
merged_df = pd.merge(reviews_orders_items, product_df, on='product_id', how='inner')

# Mengelompokkan data berdasarkan kategori produk
category_ratings = merged_df.groupby('product_category_name').agg(
    avg_review_score=('review_score', 'mean')  # Menghitung rata-rata rating
)

# Mengurutkan berdasarkan rating tertinggi
category_ratings = category_ratings.sort_values(by='avg_review_score', ascending=False).head(5)

# Membuat DataFrame dari hasil
status_table = pd.DataFrame(category_ratings).reset_index()

# Menamai kolom agar lebih mudah dipahami
status_table.columns = ['Product Category', 'Average Rating']

# --- Tabel Hasil ---
st.subheader("Top 5 Product Categories by Average Rating")

# Menyiapkan data untuk heatmap
plt.figure(figsize=(8, 4))

# Membuat heatmap menggunakan Seaborn
sns.heatmap(status_table.set_index('Product Category').T, annot=True, cmap='crest', cbar=False, fmt='g',
            annot_kws={'size': 16}, linewidths=1, linecolor='black')  # Menambahkan garis pembatas

# Menambahkan judul dan label
plt.title('', fontsize=16)
plt.xticks(rotation=45)
plt.tight_layout()

# Menampilkan heatmap di Streamlit
st.pyplot(plt)

st.markdown("<br><br>", unsafe_allow_html=True)
# Penutup dan Copyright
st.caption('E-Commerce Public Dashboard |  Muhamad Fadhly Rafiansyah | © 2025')
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from babel.numbers import format_currency
import seaborn as sns

sns.set_theme(style="dark")


def create_daily_orders_df(df):
    daily_orders_df = df.resample(rule="D", on="order_approved_at").agg(
        {"order_id": "nunique", "payment_value": "sum"}
    )
    daily_orders_df = daily_orders_df.reset_index()
    daily_orders_df.rename(
        columns={"order_id": "order_count", "payment_value": "revenue"}, inplace=True
    )

    return daily_orders_df


def create_sum_order_item_df(df):
    sum_order_items_df = (
        df.groupby("'order_approved_at'")
        .order_id.nunique()
        .sort_values(ascending=False)
        .reset_index()
    )
    return sum_order_items_df


all_df = pd.read_csv("dashboard/main_data.csv")
all_df = all_df.loc[all_df.order_status.isin(["delivered", "shipped"])]

datetime_columns = [
    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_carrier_date",
    "order_delivered_customer_date",
    "order_estimated_delivery_date",
]
all_df.sort_values(by="order_approved_at", inplace=True)
all_df.reset_index(inplace=True)

for column in datetime_columns:
    all_df[column] = pd.to_datetime(all_df[column])

min_date = all_df["order_approved_at"].min()
max_date = all_df["order_approved_at"].max()

with st.sidebar:
    st.header("Pilih Periode Tanggal")

    # mengambil start_date dan end_date dari date_input
    start_date, end_date = st.date_input(
        label="Rentang Waktu",
        min_value=min_date,
        max_value=max_date,
        value=[min_date, max_date],
    )

    st.text(f"Menampilkan data antara: {str(start_date)} dan {str(end_date)}")

main_df = all_df[
    (all_df["order_approved_at"] >= str(start_date))
    & (all_df["order_approved_at"] <= str(end_date))
]

daily_orders_df = create_daily_orders_df(main_df)

st.header("Dashboard Analysis Data E-Commerce Public Dataset")

st.subheader("Daily Orders")

col1, col2 = st.columns(2)

with col1:
    total_orders = daily_orders_df.order_count.sum()
    st.metric("Total orders", value=total_orders)

with col1:
    total_revenue = format_currency(
        daily_orders_df.revenue.sum(), "BRL", locale="pt_BR"
    )
    st.metric("Total Revenue", value=total_revenue)

fig, ax = plt.subplots(figsize=(16, 8))
ax.plot(
    daily_orders_df["order_approved_at"],
    daily_orders_df["order_count"],
    marker="o",
    linewidth=2,
    color="#90CAF9",
)

ax.tick_params(axis="y", labelsize=18)
ax.tick_params(axis="x", labelsize=15)

st.pyplot(fig)
col1, col2 = st.columns(2)

# Demografi berdasarkan asal kota customer
customer_by_city = (
    all_df.groupby(by="customer_city").customer_id.nunique().reset_index()
)
customer_by_city.rename(columns={"customer_id": "customer_count"}, inplace=True)


st.title("Number of Customers by City")

fig, ax = plt.subplots(figsize=(16, 8))

colors_ = [
    "#72BCD4",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
]

sns.barplot(
    x="customer_count",
    y="customer_city",
    data=customer_by_city.sort_values(by="customer_count", ascending=False).head(8),
    palette=colors_,
    hue="customer_city",
    legend=False,
    ax=ax,
)

ax.set_title("Number of Customers by City", loc="center", fontsize=18)
ax.tick_params(axis="y", labelsize=18)

st.pyplot(fig)

# demografi berdasarkan asal negara bagian customer
customer_by_states = (
    all_df.groupby(by="customer_state").customer_id.nunique().reset_index()
)
customer_by_states.rename(columns={"customer_id": "customer_count"}, inplace=True)

st.title("Number of Customers by States")

fig, ax = plt.subplots(figsize=(16, 8))

sns.barplot(
    x="customer_count",
    y="customer_state",
    data=customer_by_states.sort_values(by="customer_count", ascending=False).head(8),
    palette=colors_,
    hue="customer_state",
    legend=False,
)
ax.set_title("Number of Customer by State", loc="center", fontsize=18)
ax.tick_params(axis="y", labelsize=18)
st.pyplot(fig)

# Demografi berdasarkan asal kota seller
seller_by_city = all_df.groupby(by="seller_city").seller_id.nunique().reset_index()
seller_by_city.rename(columns={"seller_id": "seller_count"}, inplace=True)

st.title("Number of Seller by City")

fig, ax = plt.subplots(figsize=(16, 8))

colors_ = [
    "#72BCD4",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
    "#D3D3D3",
]

sns.barplot(
    x="seller_count",
    y="seller_city",
    data=seller_by_city.sort_values(by="seller_count", ascending=False).head(8),
    palette=colors_,
    hue="seller_city",
    legend=False,
)

ax.set_title("Number of Seller by City", loc="center", fontsize=18)
ax.tick_params(axis="y", labelsize=18)
st.pyplot(fig)

# Demografi berdasarkan asal negara bagian seller
seller_by_states = all_df.groupby(by="seller_state").seller_id.nunique().reset_index()
seller_by_states.rename(columns={"seller_id": "seller_count"}, inplace=True)

st.title("Number of Seller by States")

fig, ax = plt.subplots(figsize=(16, 8))
sns.barplot(
    x="seller_count",
    y="seller_state",
    data=seller_by_states.sort_values(by="seller_count", ascending=False).head(8),
    palette=colors_,
    hue="seller_state",
    legend=False,
)

ax.set_title("Number of Seller by State", loc="center", fontsize=18)
ax.tick_params(axis="y", labelsize=18)
st.pyplot(fig)

# Type Payment Distribution
type_of_payment = (
    all_df.loc[all_df.order_status.isin(["delivered", "shipped"])]
    .groupby(by="payment_type")
    .order_id.nunique()
    .reset_index()
)
type_of_payment.rename(columns={"order_id": "order_count"}, inplace=True)
st.title("Type Payment Distribution")

fig, ax = plt.subplots(figsize=(16, 8))
colors_ = ["#D3D3D3", "#D3D3D3", "#D3D3D3", "#72BCD4"]

sns.barplot(
    y="order_count",
    x="payment_type",
    data=type_of_payment.sort_values(by="order_count", ascending=False),
    palette=colors_,
    hue="order_count",
    legend=False,
)

ax.set_title("Payment Type Used by Customer", loc="center", fontsize=18)
ax.tick_params(axis="x", labelsize=18)
st.pyplot(fig)

# Best and Worst Category Product Distribution
sum_product_item = (
    all_df.loc[all_df.order_status.isin(["delivered", "shipped"])]
    .groupby(by="product_category_name_english")
    .order_id.nunique()
    .reset_index()
)
sum_product_item.rename(
    columns={
        "order_id": "order_count",
        "product_category_name_english": "product_category_name",
    },
    inplace=True,
)

st.title("Best and Worst Performing Product by Number of Sales")

fig, ax = plt.subplots(
    ncols=2, nrows=1, figsize=(16, 8)
)  # Sesuaikan ukuran agar proporsional di Streamlit

colors = ["#72BCD4", "#D3D3D3", "#D3D3D3", "#D3D3D3", "#D3D3D3"]

# Plot untuk Best Performing Product
sns.barplot(
    x="order_count",
    y="product_category_name",
    data=sum_product_item.sort_values(by="order_count", ascending=False).head(5),
    palette=colors,
    hue="product_category_name",
    legend=False,
    ax=ax[0],
)
ax[0].set_ylabel(None)
ax[0].set_xlabel(None)
ax[0].set_title("Best Performing Product", loc="center", fontsize=18)
ax[0].tick_params(axis="y", labelsize=14)
ax[0].tick_params(axis="x", labelsize=14)

# Plot untuk Worst Performing Product
sns.barplot(
    x="order_count",
    y="product_category_name",
    data=sum_product_item.sort_values(by="order_count", ascending=True).head(5),
    palette=colors,
    hue="product_category_name",
    legend=False,
    ax=ax[1],
)
ax[1].set_ylabel(None)
ax[1].set_xlabel(None)
ax[1].invert_xaxis()
ax[1].yaxis.tick_right()
ax[1].set_title("Worst Performing Product", loc="center", fontsize=18)
ax[1].tick_params(axis="y", labelsize=14)
ax[1].tick_params(axis="y", labelsize=14)

plt.suptitle("Best and Worst Performing Product by Number of Sales", fontsize=25)

st.pyplot(fig)


# Clustering Order Reviews based on Sentiment
dist_sentimen = all_df.groupby(by="sentiment").review_id.nunique().reset_index()
dist_sentimen.rename(columns={"review_id": "review_count"}, inplace=True)

st.title("Sentiment Distribution in Review Data")
fig, ax = plt.subplots(figsize=(16, 8))

colors_ = ["#D3D3D3", "#D3D3D3", "#72BCD4"]

sns.barplot(
    y="review_count",
    x="sentiment",
    data=dist_sentimen.sort_values(by="review_count", ascending=False),
    palette=colors_,
    ax=ax,
)

ax.set_title("Sentiment Review Distribution", loc="center", fontsize=18)
ax.tick_params(axis="x", labelsize=18)

st.pyplot(fig)

# Sentimen Distribution based on best performance product
sum_product = (
    all_df.groupby(by="product_category_name_english")
    .order_id.nunique()
    .sort_values(ascending=False)
    .reset_index()
)
sum_product.rename(
    columns={
        "order_id": "order_count",
        "product_category_name_english": "product_category_name",
    },
    inplace=True,
)

sum_sentimen = (
    all_df.groupby(by=["product_category_name_english", "sentiment"])
    .order_id.nunique()
    .reset_index()
)
sum_sentimen.rename(
    columns={
        "order_id": "order_count",
        "product_category_name_english": "product_category_name",
    },
    inplace=True,
)

sum_product_sentimen = pd.merge(
    left=sum_product.drop(columns="order_count"),
    right=sum_sentimen,
    how="left",
    on="product_category_name",
).set_index(["product_category_name", "sentiment"])

st.title("Sentiment Distribution based on Best Performance Product")

fig, ax = plt.subplots(figsize=(16, 8))

sentiment_colors = {
    "negative": "#E74C3C",  # Merah
    "netral": "#BDC3C7",  # Abu-abu
    "positive": "#2ECC71",  # Hijau
}

sns.barplot(
    y="order_count",
    x="product_category_name",
    data=sum_product_sentimen.head(18),
    hue="sentiment",
    width=0.9,
    palette=sentiment_colors,
    ax=ax,
)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right")

ax.set_title("Sentiment for Best Performance Product", loc="center", fontsize=15)
ax.tick_params(axis="x", labelsize=12)

st.pyplot(fig)
st.caption("Copyright (c) Chozam 2025")

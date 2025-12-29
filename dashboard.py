import streamlit as st
import plotly.express as px      #for generate the chart
import pandas as pd              #for data handling
import os                       #navigate some files
import warnings
warnings.filterwarnings('ignore')
import streamlit.components.v1 as components
import smtplib
from email.mime.text import MIMEText

def clear_filters():
    st.session_state.region = []
    st.session_state.state = []
    st.session_state.city = []


#Create page
st.set_page_config(page_title="Superstore!!!",page_icon=":bar_chart",layout="wide")

st.markdown("""
<style>
button[kind="secondary"], button[kind="primary"] {
    background-color: #1E88E5;color: white;border-radius: 8px;border: none;padding: 0.5rem 1.2rem;transition: all 0.3s ease;
}

button[kind="secondary"]:hover,
button[kind="primary"]:hover {
    background-color: #0D47A1;color: #ffffff;
}
</style>
""", unsafe_allow_html=True)

st.title(" :bar_chart: Sample Superstore EDA")


#File uploader
fl = st.file_uploader(":file_folder: Upload a file",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename,encoding = "ISO-8859-1")
else:
     try:
        df = pd.read_csv("Superstore.csv",encoding = "ISO-8859-1")
     except FileNotFoundError:
        st.error("❌ Superstore.csv not found. Please upload the file.")
        st.stop()

st.write("")

#Date filter
date_col1, date_col2 = st.columns(2)

df["Order Date"] = pd.to_datetime(df["Order Date"])

st.markdown("---")

startDate = pd.to_datetime(df["Order Date"]).min()
endtDate = pd.to_datetime(df["Order Date"]).max()

with date_col1:
    date1 = pd.to_datetime(st.date_input("Start Date",startDate))

with date_col2:
    date2 = pd.to_datetime(st.date_input("EndDate",endtDate))

df =df[(df["Order Date"]>= date1)& (df["Order Date"] <= date2)].copy()

#sidebar features        -----> About Dashboard
st.sidebar.markdown("## 📊 About Dashboard")
st.sidebar.info(
    "This interactive dashboard analyzes the Sample Superstore dataset to identify key sales trends, regional performance, and customer insights."
)
st.sidebar.markdown("---")

# Sidebar ---->Created By
st.sidebar.markdown("### 👩‍💻 Created By")

st.sidebar.markdown(""" Lakshani Rathnasiri """)
c1, c2 = st.sidebar.columns(2)

with c1:
    st.link_button(":e-mail: Email", "mailto:lakshanirathnasiri0501@gmail.com")
   

with c2:
    st.link_button(":link: LinkedIn", "https://www.linkedin.com/in/lakshani-rathnasiri-27500621b/")

st.sidebar.markdown("---")

#Create Filters on sidebar
st.sidebar.header("Choose your filter: ")
#Create for Region
region = st.sidebar.multiselect("Pick your Region",df["Region"].unique(),key="region")

if not region:
    df2 = df.copy()
else:
    df2 = df[df["Region"].isin(region)]

#Create for State
state = st.sidebar.multiselect("Pick the State",df2["State"].unique(),key="state")
if not state:
    df3 = df2.copy()
else:
    df3 = df2[df2["State"].isin(state)]


#create for City
city = st.sidebar.multiselect("Pick the City",df3["City"].unique(),key="city")
  

st.sidebar.button(
    "Clear All Filters",
    on_click=clear_filters
)


#Filter the date based on Region, State and City

if not region and not state and not city:
    filtered_df = df
elif not state and not city:
    filtered_df = df[df["Region"].isin(region)]
elif not region and not city:
    filtered_df = df[df["State"].isin(state)]
elif state and city:
    filtered_df =df3[df["State"].isin(state) & df3["City"].isin(city)]
elif region  and city:
    filtered_df =df3[df["Region"].isin(region) & df3["City"].isin(city)]
elif region and state:
    filtered_df =df3[df["Region"].isin(region) & df3["State"].isin(state)]
elif city:
    filtered_df = df3[df3["City"].isin(city)]
else:
    filtered_df = df3[df3["Region"].isin(region) & df3["State"].isin(state) & df3["City"].isin(city)] 

st.sidebar.markdown("---")

#Create chart theme
st.sidebar.markdown("## 🎨 Chart Theme")
theme = st.sidebar.selectbox(
    "Select Plot Theme",
    ["plotly", "plotly_dark", "seaborn", "simple_white"]
)
template=theme

st.sidebar.markdown("---")

#Create KPI cards
st.subheader("📌 Key Performance Indicators")

total_sales = filtered_df["Sales"].sum()
total_profit = filtered_df["Profit"].sum()
total_orders = filtered_df["Order ID"].nunique()

k1, k2, k3 = st.columns(3)

k1.metric("💰 Total Sales", f"${total_sales:,.0f}")
k2.metric("📈 Total Profit", f"${total_profit:,.0f}")
k3.metric("🧾 Total Orders", total_orders)

st.write("")

st.subheader("🏆 Top 5 Products by Sales")
top_products = (
    filtered_df.groupby("Sub-Category")["Sales"]
    .sum()
    .sort_values(ascending=False)
    .head(5)
)
st.dataframe(top_products)

st.markdown("---")

# ================= PROFITABILITY INSIGHTS =================
st.subheader("⚠️ Profitability Insights (Business View)")

# 1️⃣ Loss-making orders
loss_df = filtered_df[filtered_df["Profit"] < 0]

st.write("❌ **Loss-Making Orders (Sample)**")
st.dataframe(
    loss_df[["Order ID", "Category", "Region", "Profit"]].head(10)
)

st.markdown("")

# 2️⃣ Loss by Category
st.write("📉 **Loss by Category**")
loss_category = (
    filtered_df.groupby("Category")["Profit"]
    .sum()
    .sort_values()
)

st.dataframe(loss_category)

# 3️⃣ Loss by Region
st.write("🌍 **Loss by Region**")
loss_region = (
    filtered_df.groupby("Region")["Profit"]
    .sum()
    .sort_values()
)

st.dataframe(loss_region)

st.info(
    "This section highlights loss-making areas to support pricing, "
    "cost control, and strategic business decisions."
)

st.markdown("---")

# ================= PROFITABILITY CHART =================
st.subheader("📊 Profit by Category (Chart)")

profit_category_df = (
    filtered_df.groupby("Category", as_index=False)["Profit"]
    .sum()
)

fig_profit = px.bar(
    profit_category_df,
    x="Category",
    y="Profit",
    text_auto=True,
    template=theme
)

fig_profit.update_layout(
    title="Category-wise Profit Analysis",
    xaxis_title="Category",
    yaxis_title="Profit"
)

st.plotly_chart(fig_profit, use_container_width=True)

st.markdown("---")


#Create category wise sales
category_df = filtered_df.groupby(by = ["Category"],as_index=False)["Sales"].sum()

st.write("")
st.write("")

chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("     Category wise Sales")
    fig = px.bar(category_df,x ="Category",y="Sales",text= ['${:,.2f}'.format(x) for x in category_df["Sales"]],
                 template = theme)
    st.plotly_chart(fig,use_container_width=True,height=450)

with chart_col2:
    st.subheader("Region wise Sales")
    fig = px.pie(filtered_df,values="Sales",names="Region",hole=0.5,template = theme)
    fig.update_traces(text = filtered_df["Region"],textposition = "outside")
    st.plotly_chart(fig,use_container_width=True)


with chart_col1:
    with st.expander("Category_ViewData"):
        st.write(category_df.style.background_gradient(cmap = "Blues"))
        csv = category_df.to_csv(index=False).encode('utf-8')
        st.download_button("Download data", data=csv, file_name="Category.csv", mime="text/csv")

with chart_col2:
    with st.expander("Region_ViewData"):
        region = filtered_df.groupby(by="Region", as_index=False)["Sales"].sum()
        st.write(region.style.background_gradient(cmap = "Oranges"))
        csv = region.to_csv(index=False).encode('utf-8')
        st.download_button("Download data", data=csv, file_name="Region.csv", mime="text/csv")


st.markdown("---")

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader('Time Series Analaysis')


linechart = (
    filtered_df
    .groupby("month_year", as_index=False)["Sales"]
    .sum()
)

linechart["month_year"] = linechart["month_year"].dt.to_timestamp()
linechart = linechart.sort_values("month_year")

fig2 = px.line(linechart,x="month_year",y="Sales", labels={"Sales": "Amount"},height=500,width=1000,template=theme)
fig2.update_xaxes(tickangle=90)
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of Time Series:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv= linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data',data= csv,file_name="TimeSeries.csv",mime='text/csv')


st.markdown("---")

#Create a tream based on Region,category,sub category
st.subheader("Hierarchical view of Sales using TreMap")
fig3 = px.treemap(filtered_df,path=["Region","Category","Sub-Category"],values="Sales",hover_data=["Sales"],color="Sub-Category",template=theme)
fig3.update_layout(width=800,height=650)
st.plotly_chart(fig3,use_container_width=True)

st.markdown("---")

chart1,chart2 = st.columns((2))
with chart1:
    st.subheader('Segment wise Sales')
    fig= px.pie(filtered_df,values="Sales",names="Segment",template=theme)
    fig.update_traces(text=filtered_df["Segment"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)


with chart2:
    st.subheader('Category wise Sales')
    fig= px.pie(filtered_df,values="Sales",names="Category",template=theme)
    fig.update_traces(text=filtered_df["Category"],textposition="inside")
    st.plotly_chart(fig,use_container_width=True)

import plotly.figure_factory as ff
st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Summary_Table"):
        df_sample = df[0:5][["Region","City","Category","Sales","Profit","Quantity"]]
        fig= ff.create_table(df_sample,colorscale="Cividis")
        st.plotly_chart(fig,use_container_width=True)

        st.markdown("Month wise sub-Category Table")
        filtered_df["month"]=filtered_df["Order Date"].dt.month_name()
        sub_category_Year = pd.pivot_table(data=filtered_df,values="Sales",index=["Sub-Category"],columns="month")
        st.write(sub_category_Year.style.background_gradient(cmap="Blues"))


#create a scatter plot
data1=px.scatter(
                filtered_df,
                x="Sales",
                y="Profit",
                size="Quantity")
st.write("")
st.write("")

data1.update_layout(
                    title_text="Relationship between Sales and Profits using Scatter Plot",
                    title_font_size=20,
                    xaxis_title="Sales",
                    xaxis_title_font=dict(size=19),
                    yaxis_title="Profit",
                    yaxis_title_font=dict(size=19)
                    )
st.plotly_chart(data1,use_container_width=True)

with st.expander("View Data"):
    st.write(filtered_df.iloc[:500,1:20:2].style.background_gradient(cmap="Oranges"))

#Download original dataset
csv= df.to_csv(index=False).encode('utf-8')
st.download_button('Dowmload Data',
                   data=csv,
                   file_name="Data.csv",
                   mime="text/csv")

st.markdown("---")

def send_email(name, sender_email, message):
    receiver_email = "lakshanirathnasiri0501@gmail.com"   # your email
    app_password = st.secrets["EMAIL_PASSWORD"]

    body = f"""
    Name: {name}
    Email: {sender_email}

    Message:
    {message}
    """

    msg = MIMEText(body)
    msg["Subject"] = "New Contact Form Message"
    msg["From"] = sender_email
    msg["To"] = receiver_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(receiver_email, app_password)
        server.send_message(msg)

#Creating a form
st.subheader("📬 Contact Me")
st.write("Have a question, feedback, or collaboration idea? Send me a message below.")

with st.form("contact_form"):
    name = st.text_input("Your Name")
    sender_email = st.text_input("Your Email")
    message = st.text_area("Message")
    submit = st.form_submit_button("Send")

if submit:
    if name and sender_email and message:
        send_email(name, sender_email, message)
        st.success("✅ Thank you! Your message has been sent.")
    else:
        st.error("❌ Please fill all fields")

#Footer
st.markdown("---")
st.caption("© 2025 Lakshani Rathnasiri | Built with Python & Streamlit")




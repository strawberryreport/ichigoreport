import altair as alt
import datetime
import numpy as np
import pandas as pd
#import plotly.figure_factory as ff
#import plotly.graph_objects as go
import plotly
import plotly_express as px
import streamlit as st
import sqlite3


#db_file = 'IchigoDB_kyoto.db'
#db_file = 'IchigoDB_yamaguchi.db'
db_file = 'IchigoDB_6ren.db'
conn = sqlite3.connect(db_file)

df = pd.read_sql_query("""SELECT MEASURE_DATE,
                          COUNT(STOCK_ID) AS CNT
                          FROM MASTER_HEADERS
                          GROUP BY MEASURE_DATE"""
                       , conn)

df_sum = pd.read_sql_query("""SELECT MEASURE_DATE,
                              STOCK_ITEM_1 || STOCK_ITEM_2 || STOCK_ITEM_3 || STOCK_ITEM_4 AS STOCK_ITEM,
                              SUM(IFNULL(FRUIT_TOP_WEIGHT,0)) AS WEIGHT_SUM
                              FROM MASTER_HEADERS
                              LEFT JOIN FRUIT_BUNCH_DETAILS ON MASTER_HEADERS.ID = FRUIT_BUNCH_DETAILS.MASTER_ID
                              GROUP BY MEASURE_DATE, STOCK_ITEM"""
                           , conn)

#df_lov_stock = pd.read_sql_query('SELECT DISTINCT(SUBSTRING(STOCK_ID,1,3)) AS STOCK FROM MASTER_HEADERS', conn)
df_lov_stock = pd.read_sql_query('SELECT DISTINCT(SUBSTR(STOCK_ID,1,4)) AS STOCK FROM MASTER_HEADERS', conn)
df_lov_stock_list = df_lov_stock['STOCK'].unique().tolist()

#st.title('棚別収穫量')

option2 = ''

option1 = st.sidebar.selectbox(
    '選択してください'
    ,('収穫量推移','果房発生頻度')
    )

radio1 = st.sidebar.radio(
    'グラフの種類',('収量（棚別）','収量（株別）','果房発生頻度')
    )

if radio1 == '収量（棚別）':
    option2 = st.multiselect(
        '選択してください'
        ,df_lov_stock_list
        )

if radio1 == '収量（株別）':
    option3 = st.selectbox(
        '選択してください'
        ,df_lov_stock_list
        )

min_date = datetime.datetime.now() - datetime.timedelta(days=360)
max_date = datetime.datetime.now()

date = st.date_input('日付の範囲を指定してください',
              [min_date, max_date],
              max_value=max_date
              )


if date != '':
    df_sum = df_sum[(pd.to_datetime(df_sum['MEASURE_DATE']).dt.date >= date[0]) & (pd.to_datetime(df_sum['MEASURE_DATE']).dt.date <= date[1])]

if option2 != '':
    df_sum = df_sum[df_sum['STOCK_ITEM'].isin(option2)]

#if option3 != '':
 #   df_sum = df_sum[df_sum['STOCK_ITEM'] == option3]


df_target = df[['MEASURE_DATE', 'CNT']].groupby('MEASURE_DATE').count()
df_target = df_target.reset_index()

#st.write(option)

#fig_target = go.Figure(data=[go.Pie(labels=df_target.index,
#                                    values=df_target['CNT'],
#                                    hole=.3)])

#fig_target.update_layout(showlegend=False,
#                         height=280,
#                         margin={'l':20, 'r':60, 't': 0, 'b':0})


#fig_target.update_traces(textposition='inside', testinfo= 'label+percent')

## 円グラフをコメントアウト
#st.plotly_chart(fig_target, use_container=True)


#vars_date = [var for var in df.columns if df.startswith('MEASURE_DATE')]
#vars_count = [var for var in df.columns if df.startswith('COUNT')]


#chart = alt.Chart(df_target).mark_line().encode( x="MEASURE_DATE", y="CNT")
#st.altair_chart(chart, use_container_width=True)

chart2 = alt.Chart(df_sum).mark_line().encode( x="MEASURE_DATE", y="WEIGHT_SUM", color="STOCK_ITEM")
st.altair_chart(chart2, use_container_width=True)

#chart3 = alt.Chart(df_sum).mark_line().encode( x="MEASURE_DATE", y="WEIGHT_SUM")
#st.bar_chart(chart3, use_container_width=True)

#st.line_chart(df_target)
#st.line_chart(df_target, x=df_target['MEASURE_DATE'].values.tolist(), y=df_target['CNT'].values.tolist(), use_container=True))

x_axis = st.selectbox('test x', options= df_sum.columns)
y_axis = st.selectbox('test y', options= df_sum.columns)
#y_axis = df_sum["WEIGHT_SUM"]
plot = px.scatter(df_sum, x=x_axis, y=y_axis)
st.plotly_chart(plot)

plot2 = px.line(df_sum, x=x_axis, y=y_axis, color="STOCK_ITEM")
st.plotly_chart(plot2)

plot3 = px.bar(df_sum, x=x_axis, y=y_axis, color="STOCK_ITEM")
st.plotly_chart(plot3)

print(df_sum)

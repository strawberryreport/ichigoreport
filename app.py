import altair as alt
import datetime
import numpy as np
import pandas as pd
#import plotly.figure_factory as ff
#import plotly.graph_objects as go
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
                              INNER JOIN FRUIT_BUNCH_DETAILS ON MASTER_HEADERS.ID = FRUIT_BUNCH_DETAILS.MASTER_ID
                              GROUP BY MEASURE_DATE, STOCK_ITEM"""
                           , conn)

#収穫日に１を立てる

df_kabo = pd.read_sql_query(""" SELECT STOCK_ITEM,
                                        MEASURE_DATE,
                                        SUM(CNT) AS KABO_CNT

                                        FROM (
                                        SELECT STOCK_ITEM_1 || STOCK_ITEM_2 || STOCK_ITEM_3 || STOCK_ITEM_4 AS STOCK_ITEM,
                                        MEASURE_DATE AS MEASURE_DATE,
                                        /*FRUIT_BUNCH_ID,*/
                                        1 as CNT
                                        FROM MASTER_HEADERS
                                        LEFT JOIN FRUIT_BUNCH_DETAILS ON MASTER_HEADERS.ID = FRUIT_BUNCH_DETAILS.MASTER_ID
                                        WHERE FRUIT_TOP_STATUS in ('蕾', '開花前')
                                        GROUP BY STOCK_ITEM,FRUIT_BUNCH_ID,MEASURE_DATE
                                        )
                                        GROUP BY STOCK_ITEM/*,FRUIT_BUNCH_ID*/,MEASURE_DATE
                                        ORDER BY MEASURE_DATE,STOCK_ITEM
                                """
                          , conn)

df_shukaku = pd.read_sql_query(""" SELECT STOCK_ITEM,
                                COUNT(KABO_SHUKAKU) AS KABO_SHUKAKU_SUM,
                                MEASURE_DATE,
                                KABO_SHUKAKU
                                FROM(
                                SELECT M.STOCK_ITEM_1 || M.STOCK_ITEM_2 || M.STOCK_ITEM_3 || M.STOCK_ITEM_4 AS STOCK_ITEM,
                                MIN(M.MEASURE_DATE) AS MEASURE_DATE,
                                '1' AS KABO_SHUKAKU
                                FROM MASTER_HEADERS M
                                LEFT JOIN FRUIT_BUNCH_DETAILS F ON M.ID = F.MASTER_ID
                                WHERE F.FRUIT_TOP_STATUS in ('収穫', '収穫済み')
                               )
                                
                                GROUP BY STOCK_ITEM, MEASURE_DATE, KABO_SHUKAKU
                                """
                          , conn)

#df_lov_stock = pd.read_sql_query('SELECT DISTINCT(SUBSTRING(STOCK_ID,1,3)) AS STOCK FROM MASTER_HEADERS', conn)
df_lov_stock = pd.read_sql_query('SELECT DISTINCT(SUBSTR(STOCK_ID,1,4)) AS STOCK FROM MASTER_HEADERS', conn)
df_lov_stock_list = df_lov_stock['STOCK'].unique().tolist()

#st.title('棚別収穫量')

option2 = ''

option1 = st.sidebar.selectbox(
    '選択してください'
    ,('Graph1','Graph2','Graph3','Graph4')
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
    df_kabo = df_kabo[(pd.to_datetime(df_kabo['MEASURE_DATE']).dt.date >= date[0]) & (pd.to_datetime(df_kabo['MEASURE_DATE']).dt.date <= date[1])]

if option2 != '':
    df_sum = df_sum[df_sum['STOCK_ITEM'].isin(option2)]
    df_kabo = df_kabo[df_kabo['STOCK_ITEM'].isin(option2)]

#if option3 != '':
 #   df_sum = df_sum[df_sum['STOCK_ITEM'] == option3]
#st.write(option)





#y_axis = df_sum["WEIGHT_SUM"]

if option1 == 'Graph1':
    
    x_axis = st.selectbox('test x', options= df_sum.columns)
    y_axis = st.selectbox('test y', options= df_sum.columns)
    
    #散布図
    plot = px.scatter(df_sum, x=x_axis, y=y_axis)
    st.plotly_chart(plot)

    #折れ線グラフ
    plot2 = px.line(df_sum, x=x_axis, y=y_axis, color="STOCK_ITEM")
    st.plotly_chart(plot2)

    #棒グラフ
    plot3 = px.bar(df_sum, x=x_axis, y=y_axis, color="STOCK_ITEM")
    st.plotly_chart(plot3)

elif option1 == 'Graph2':
    
    x2_axis = st.selectbox('test x2', options= df_kabo.columns)
    y2_axis = st.selectbox('test y2', options= df_kabo.columns)

    #棒グラフ
#    plot4 = px.bar(df_kabo, x=x2_axis, y=y2_axis, color="STOCK_ITEM")
    plot4 = px.bar(df_kabo, x=x2_axis, y=y2_axis, color="STOCK_ITEM")
    st.plotly_chart(plot4)

    print(df_kabo)
    
elif option1 == 'Graph3':

    chart2 = alt.Chart(df_sum).mark_line().encode( x="MEASURE_DATE", y="WEIGHT_SUM", color="STOCK_ITEM")
    st.altair_chart(chart2, use_container_width=True)

   

#chart3 = alt.Chart(df_sum).mark_line().encode( x="MEASURE_DATE", y="WEIGHT_SUM")
#st.bar_chart(chart3, use_container_width=True)
    


#df_target = df[['MEASURE_DATE', 'CNT']].groupby('MEASURE_DATE').count()
#df_target = df_target.reset_index()

#vars_date = [var for var in df.columns if df.startswith('MEASURE_DATE')]
#vars_count = [var for var in df.columns if df.startswith('COUNT')]

#fig_target = go.Figure(data=[go.Pie(labels=df_target.index,
#                                    values=df_target['CNT'],
#                                    hole=.3)])

#fig_target.update_layout(showlegend=False,
#                         height=280,
#                         margin={'l':20, 'r':60, 't': 0, 'b':0})

#fig_target.update_traces(textposition='inside', testinfo= 'label+percent')

#st.line_chart(df_target)
#st.line_chart(df_target, x=df_target['MEASURE_DATE'].values.tolist(), y=df_target['CNT'].values.tolist(), use_container=True))

## 円グラフをコメントアウト
#st.plotly_chart(fig_target, use_container=True)

#chart = alt.Chart(df_target).mark_line().encode( x="MEASURE_DATE", y="CNT")
#st.altair_chart(chart, use_container_width=True)



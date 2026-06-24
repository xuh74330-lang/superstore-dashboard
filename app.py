"""
Global Superstore 交互式数据可视化分析平台
基于 Streamlit + Plotly 构建
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime

# ======================== 页面配置 ========================
st.set_page_config(
    page_title="Global Superstore 数据可视化分析",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================== 界面美化 CSS 注入 ========================
st.markdown("""
<style>
/* 1. 优化整体页面的内边距与底色 */
.block-container {
    padding-top: 1.8rem;
    padding-bottom: 2rem;
}

/* 2. 重写 KPI 指标卡片 (st.metric) 的样式：白底、圆角、立体微阴影、悬浮动效 */
[data-testid="stMetric"] {
    background-color: #FFFFFF;
    border-radius: 12px;
    padding: 18px 22px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.03);
    border: 1px solid #EAEAEA;
    transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
    box-shadow: 0 10px 20px rgba(0, 0, 0, 0.06);
    border-color: #4C78A8;
}

/* 3. 美化 KPI 标签与数值的字体样式 */
[data-testid="stMetricLabel"] {
    font-size: 0.95rem !important;
    font-weight: 600;
    color: #6C757D;
}
[data-testid="stMetricValue"] {
    font-size: 1.7rem !important;
    font-weight: 700;
    color: #2C3E50;
    margin-top: 4px;
}

/* 4. 侧边栏样式微调，增加右侧微阴影使其更有解构层次感 */
[data-testid="stSidebar"] {
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.03);
}

/* 5. 图表区域小标题样式优化：添加左侧主题色装饰条 */
p strong {
    color: #2C3E50;
    font-size: 1.05rem;
    border-left: 4px solid #4C78A8;
    padding-left: 8px;
    display: inline-block;
    margin-bottom: 4px;
}

/* 6. 隐藏 Streamlit 右上角默认的工具栏按钮，让界面更纯净高级 */
.stAppDeployButton { display:none !important; }
</style>
""", unsafe_allow_html=True)

# ======================== 数据加载与预处理 ========================
@st.cache_data
def load_data():
    df = pd.read_csv("superstore.csv")
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['Year'] = df['Order Date'].dt.year
    df['Month'] = df['Order Date'].dt.month
    df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
    df['Profit Margin'] = df['Profit'] / df['Sales'] * 100
    return df

df = load_data()

# ======================== 侧边栏 - 全局筛选器 ========================
st.sidebar.title("🔍 全局筛选器")

# 日期范围筛选
date_range = st.sidebar.date_input(
    "📅 日期范围",
    value=[df['Order Date'].min(), df['Order Date'].max()],
    min_value=df['Order Date'].min(),
    max_value=df['Order Date'].max()
)

# 市场筛选
all_markets = sorted(df['Market'].unique())
selected_markets = st.sidebar.multiselect(
    "🌍 市场区域",
    options=all_markets,
    default=all_markets
)

# 客户细分筛选
all_segments = sorted(df['Segment'].unique())
selected_segments = st.sidebar.multiselect(
    "👤 客户细分",
    options=all_segments,
    default=all_segments
)

# 品类筛选
all_categories = sorted(df['Category'].unique())
selected_categories = st.sidebar.multiselect(
    "📦 产品类别",
    options=all_categories,
    default=all_categories
)

# 订单优先级筛选
all_priorities = sorted(df['Order Priority'].unique())
selected_priorities = st.sidebar.multiselect(
    "⚡ 订单优先级",
    options=all_priorities,
    default=all_priorities
)

# 应用筛选
filtered_df = df[
    (df['Order Date'].dt.date >= date_range[0]) &
    (df['Order Date'].dt.date <= date_range[1]) &
    (df['Market'].isin(selected_markets)) &
    (df['Segment'].isin(selected_segments)) &
    (df['Category'].isin(selected_categories)) &
    (df['Order Priority'].isin(selected_priorities))
]

# ======================== 主页面 ========================
st.title("📊 Global Superstore 数据可视化分析平台")
st.markdown("---")

# ======================== KPI 指标卡 ========================
st.subheader("📈 关键业务指标 (KPI)")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    total_sales = filtered_df['Sales'].sum()
    st.metric("💰 总销售额", f"${total_sales:,.0f}")

with col2:
    total_profit = filtered_df['Profit'].sum()
    st.metric("📈 总利润", f"${total_profit:,.0f}")

with col3:
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
    st.metric("📊 利润率", f"{profit_margin:.2f}%")

with col4:
    total_orders = filtered_df['Order ID'].nunique()
    st.metric("📋 订单总数", f"{total_orders:,}")

with col5:
    avg_order_value = total_sales / total_orders if total_orders > 0 else 0
    st.metric("🛒 平均订单金额", f"${avg_order_value:,.0f}")

with col6:
    unique_customers = filtered_df['Customer ID'].nunique()
    st.metric("👥 客户数", f"{unique_customers:,}")

st.markdown("---")

# ======================== 图表区域 - 第一行 ========================
st.subheader("📊 销售与利润分析")

col_left, col_right = st.columns(2)

with col_left:
    with st.container(border=True):
        st.markdown("**各产品类别销售额与利润对比**")
        cat_data = filtered_df.groupby('Category').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        fig_cat = make_subplots(specs=[[{"secondary_y": True}]])
        fig_cat.add_trace(
            go.Bar(name="销售额", x=cat_data['Category'], y=cat_data['Sales'],
                   marker_color=['#4C78A8', '#54A24B', '#F58518'], text=cat_data['Sales'].apply(lambda x: f"${x/1e6:.1f}M"),
                   textposition='outside'),
            secondary_y=False
        )
        fig_cat.add_trace(
            go.Scatter(name="利润", x=cat_data['Category'], y=cat_data['Profit'],
                       mode='lines+markers', marker=dict(size=14, color='#E45756'),
                       line=dict(width=3)),
            secondary_y=True
        )
        fig_cat.update_layout(height=420, template='plotly_white', hovermode='x unified',
                              legend=dict(orientation='h', y=1.15))
        fig_cat.update_yaxes(title_text="销售额 (USD)", secondary_y=False)
        fig_cat.update_yaxes(title_text="利润 (USD)", secondary_y=True)
        st.plotly_chart(fig_cat, use_container_width=True)

with col_right:
    with st.container(border=True):
        st.markdown("**子品类销售额排名 (Top 10)**")
        sub_data = filtered_df.groupby('Sub-Category')['Sales'].sum().sort_values(ascending=True).tail(10)
        fig_sub = px.bar(
            x=sub_data.values, y=sub_data.index,
            orientation='h',
            color=sub_data.values,
            color_continuous_scale='Blues',
            labels={'x': '销售额 (USD)', 'y': '子品类'},
            text=sub_data.values
        )
        fig_sub.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
        fig_sub.update_layout(height=420, template='plotly_white', showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_sub, use_container_width=True)

# ======================== 图表区域 - 第二行 ========================
col_left2, col_right2 = st.columns(2)

with col_left2:
    with st.container(border=True):
        st.markdown("**销售额月度趋势**")
        monthly_data = filtered_df.groupby('YearMonth').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index()
        monthly_data = monthly_data.sort_values('YearMonth')
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(
            x=monthly_data['YearMonth'], y=monthly_data['Sales'],
            mode='lines+markers', name='销售额',
            fill='tozeroy', fillcolor='rgba(76, 120, 168, 0.2)',
            line=dict(color='#4C78A8', width=2), marker=dict(size=6)
        ))
        fig_line.add_trace(go.Scatter(
            x=monthly_data['YearMonth'], y=monthly_data['Profit'],
            mode='lines+markers', name='利润',
            fill='tozeroy', fillcolor='rgba(228, 87, 86, 0.15)',
            line=dict(color='#E45756', width=2), marker=dict(size=6)
        ))
        fig_line.update_layout(height=400, template='plotly_white', hovermode='x unified',
                               xaxis_title='', yaxis_title='金额 (USD)',
                               legend=dict(orientation='h', y=1.1))
        st.plotly_chart(fig_line, use_container_width=True)

with col_right2:
    with st.container(border=True):
        st.markdown("**销售额与利润关系散点图**")
        sample_df = filtered_df.sample(min(2000, len(filtered_df)), random_state=42)
        fig_scatter = px.scatter(
            sample_df, x='Sales', y='Profit',
            color='Category',
            size='Quantity',
            hover_data=['Sub-Category', 'Market'],
            color_discrete_map={'Technology': '#4C78A8', 'Furniture': '#54A24B', 'Office Supplies': '#F58518'},
            opacity=0.7
        )
        fig_scatter.update_layout(height=400, template='plotly_white',
                                  xaxis_title='销售额 (USD)', yaxis_title='利润 (USD)',
                                  legend=dict(orientation='h', y=1.1))
        st.plotly_chart(fig_scatter, use_container_width=True)

# ======================== 图表区域 - 第三行 ========================
st.subheader("🌍 地域与市场分析")

col_left3, col_right3 = st.columns(2)

with col_left3:
    with st.container(border=True):
        st.markdown("**市场与品类交叉热力图**")
        heat_data = filtered_df.pivot_table(values='Sales', index='Market', columns='Category', aggfunc='sum').fillna(0)
        fig_heat = px.imshow(
            heat_data,
            text_auto='.1f',
            color_continuous_scale='Blues',
            aspect='auto',
            labels={'x': '产品类别', 'y': '市场', 'color': '销售额'}
        )
        for i in range(len(heat_data)):
            for j in range(len(heat_data.columns)):
                val = heat_data.iloc[i, j]
                fig_heat.add_annotation(
                    x=j, y=i, text=f"${val/1e6:.1f}M",
                    showarrow=False, font=dict(size=11)
                )
        fig_heat.update_layout(height=400, template='plotly_white')
        st.plotly_chart(fig_heat, use_container_width=True)

with col_right3:
    with st.container(border=True):
        st.markdown("**各市场销售额占比**")
        market_data = filtered_df.groupby('Market')['Sales'].sum().reset_index()
        market_data = market_data.sort_values('Sales', ascending=True)
        fig_pie = go.Figure(data=[go.Pie(
            labels=market_data['Market'],
            values=market_data['Sales'],
            hole=0.45,
            textinfo='label+percent',
            marker=dict(colors=px.colors.qualitative.Set2),
            textposition='outside'
        )])
        fig_pie.update_layout(height=400, template='plotly_white', showlegend=False)
        st.plotly_chart(fig_pie, use_container_width=True)

# ======================== 细分维度分析 ========================
st.subheader("👤 客户与订单分析")

col_left4, col_right4 = st.columns(2)

with col_left4:
    with st.container(border=True):
        st.markdown("**客户细分销售额分布**")
        seg_data = filtered_df.groupby(['Segment', 'Category'])['Sales'].sum().reset_index()
        fig_seg = px.bar(
            seg_data, x='Segment', y='Sales', color='Category',
            color_discrete_map={'Technology': '#4C78A8', 'Furniture': '#54A24B', 'Office Supplies': '#F58518'},
            barmode='group',
            text_auto='.1s'
        )
        fig_seg.update_layout(height=400, template='plotly_white',
                              xaxis_title='客户细分', yaxis_title='销售额 (USD)',
                              legend=dict(orientation='h', y=1.1))
        st.plotly_chart(fig_seg, use_container_width=True)

with col_right4:
    with st.container(border=True):
        st.markdown("**运输方式与订单优先级分析**")
        ship_data = filtered_df.groupby(['Ship Mode', 'Order Priority']).size().reset_index(name='Count')
        fig_ship = px.bar(
            ship_data, x='Ship Mode', y='Count', color='Order Priority',
            color_discrete_map={'Critical': '#E45756', 'High': '#F58518', 'Medium': '#4C78A8', 'Low': '#54A24B'},
            barmode='stack',
            text_auto=True
        )
        fig_ship.update_layout(height=400, template='plotly_white',
                               xaxis_title='运输方式', yaxis_title='订单数量',
                               legend=dict(orientation='h', y=1.1))
        st.plotly_chart(fig_ship, use_container_width=True)

# ======================== 折扣与利润分析 ========================
st.subheader("💵 折扣与利润分析")

col_left5, col_right5 = st.columns(2)

with col_left5:
    with st.container(border=True):
        st.markdown("**折扣水平对利润率的影响**")
        filtered_df['Discount_Level'] = pd.cut(
            filtered_df['Discount'],
            bins=[-0.01, 0, 0.1, 0.3, 1.0],
            labels=['无折扣', '低折扣(10%)', '中折扣(20-30%)', '高折扣(40-50%)']
        )
        discount_profit = filtered_df.groupby('Discount_Level', observed=False).agg(
            {'Sales': 'sum', 'Profit': 'sum', 'Order ID': 'nunique'}
        ).reset_index()
        discount_profit['Margin'] = (discount_profit['Profit'] / discount_profit['Sales'] * 100).round(2)

        fig_discount = make_subplots(specs=[[{"secondary_y": True}]])
        fig_discount.add_trace(
            go.Bar(name="利润率 (%)", x=discount_profit['Discount_Level'],
                   y=discount_profit['Margin'],
                   marker_color=['#54A24B', '#4C78A8', '#F58518', '#E45756'],
                   text=discount_profit['Margin'].apply(lambda x: f"{x:.1f}%"),
                   textposition='outside'),
            secondary_y=False
        )
        fig_discount.add_trace(
            go.Scatter(name="订单数", x=discount_profit['Discount_Level'],
                       y=discount_profit['Order ID'],
                       mode='lines+markers', marker=dict(size=12, color='#B279A2'),
                       line=dict(width=3, dash='dot')),
            secondary_y=True
        )
        fig_discount.update_layout(height=400, template='plotly_white',
                                   legend=dict(orientation='h', y=1.15))
        st.plotly_chart(fig_discount, use_container_width=True)

with col_right5:
    with st.container(border=True):
        st.markdown("**各市场平均折扣率**")
        market_discount = filtered_df.groupby('Market')['Discount'].mean().sort_values(ascending=True)
        fig_md = px.bar(
            x=market_discount.values * 100, y=market_discount.index,
            orientation='h',
            color=market_discount.values,
            color_continuous_scale='Reds',
            labels={'x': '平均折扣率 (%)', 'y': '市场'},
            text=market_discount.values
        )
        fig_md.update_traces(texttemplate='%{text:.1%}', textposition='outside')
        fig_md.update_layout(height=400, template='plotly_white', showlegend=False, coloraxis_showscale=False)
        st.plotly_chart(fig_md, use_container_width=True)

# ======================== 数据明细表 ========================
st.markdown("---")
st.subheader("📋 数据明细与钻取")

with st.expander("🔽 点击展开数据明细表（支持排序与搜索）"):
    display_cols = ['Order ID', 'Order Date', 'Ship Mode', 'Market', 'Country', 'City',
                    'Category', 'Sub-Category', 'Sales', 'Quantity', 'Discount', 'Profit', 'Order Priority']
    st.dataframe(
        filtered_df[display_cols].sort_values('Sales', ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            'Order Date': st.column_config.DateColumn('订单日期', format='YYYY-MM-DD'),
            'Sales': st.column_config.NumberColumn('销售额', format='$%.2f'),
            'Profit': st.column_config.NumberColumn('利润', format='$%.2f'),
            'Discount': st.column_config.NumberColumn('折扣', format='%.0f%%'),
        }
    )

# ======================== 页脚 ========================
st.markdown("---")
st.caption("Global Superstore 数据可视化分析平台 | 课程期末作业 | 24大数据3 徐浩朋 24211870309")
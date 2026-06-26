"""
Global Superstore 多维数据可视化分析平台
基于 Streamlit + Plotly 构建 (纯正深色大屏极客版 - 高对比度清晰版)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os

# 尝试导入 openai 库 (DeepSeek 接口完全兼容 OpenAI SDK)
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

# ======================== 页面全局配置 ========================
st.set_page_config(
    page_title="Global Superstore | Dark Edition",
    page_icon="🌌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================== 终极高对比度深色大屏 CSS 注入 ========================
st.markdown("""
<style>
/* 1. 强制全局深色背景 */
.stApp {
    background-color: #0E1117 !important;
}
.block-container { 
    padding-top: 1.5rem; 
    padding-bottom: 2rem; 
    background-color: #0E1117 !important;
}

/* 2. 严谨学术标题反白 */
.academic-title { 
    font-size: 2.2rem; 
    font-weight: 700; 
    color: #FFFFFF !important; 
    margin-bottom: 0.5rem; 
    border-left: 6px solid #58A6FF; 
    padding-left: 15px; 
}
.academic-subtitle { 
    font-size: 1.1rem; 
    color: #8B949E !important; 
    margin-bottom: 2rem; 
    padding-left: 21px; 
}

/* 3. 核心指标卡 (st.metric) 高对比度优化 */
[data-testid="stMetric"] { 
    background-color: #161B22 !important; 
    border-radius: 8px; 
    padding: 15px 20px; 
    box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important; 
    border: 1px solid #30363D !important; 
}
[data-testid="stMetricLabel"] { 
    font-size: 0.95rem !important; 
    color: #8B949E !important; 
    font-weight: 500;
}
[data-testid="stMetricValue"] { 
    font-size: 1.7rem !important; 
    color: #58A6FF !important; 
    font-weight: 700; 
}

/* 4. 选项卡 (Tabs) 文字高亮 */
div[data-baseweb="tab-list"] { 
    border-bottom: 1px solid #30363D !important; 
}
div[data-baseweb="tab"] p { 
    font-size: 1.1rem !important; 
    font-weight: 600 !important; 
    color: #8B949E !important; 
}
div[aria-selected="true"] p { 
    color: #58A6FF !important; 
}

/* 5. 侧边栏完全深色化与标签清洗 */
[data-testid="stSidebar"] {
    background-color: #161B22 !important;
    border-right: 1px solid #30363D !important;
}
[data-testid="stSidebar"] p, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] label {
    color: #F0F6FC !important;
}

/* 6. 图表外框容器 (st.container) 样式强固 */
div[data-testid="stContainer"] {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 8px;
    padding: 18px !important;
    margin-bottom: 10px;
}

/* 7. 终极文本反白杀手锏：强制所有常规 Markdown 正文、加粗文本和列表绝对可见 */
.stMarkdown p, .stMarkdown strong, .stMarkdown span, .stMarkdown li {
    color: #F0F6FC !important;
}
.stMarkdown strong {
    color: #FFFFFF !important;
    font-size: 1.05rem !important;
}

/* 8. 折叠面板 (st.expander) 文字对比度修复 */
div[data-testid="stExpander"] {
    background-color: #161B22 !important;
    border: 1px solid #30363D !important;
    border-radius: 6px !important;
}
div[data-testid="stExpander"] p, div[data-testid="stExpander"] span, div[data-testid="stExpander"] summary {
    color: #FFFFFF !important;
}

/* 9. AI 报告面板黑金风格 */
.ai-report { 
    background-color: #1F242C !important; 
    border-left: 4px solid #58A6FF; 
    padding: 15px; 
    border-radius: 5px; 
    font-size: 1.05rem; 
    color: #F0F6FC !important; 
    margin-top: 15px; 
    line-height: 1.6;
    border: 1px solid #30363D;
}

/* 隐藏杂项 */
#MainMenu, header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ======================== 数据加载 ========================
@st.cache_data
def load_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "superstore.csv")
    df = pd.read_csv(file_path)
    df['Order Date'] = pd.to_datetime(df['Order Date'])
    df['Ship Date'] = pd.to_datetime(df['Ship Date'])
    df['YearMonth'] = df['Order Date'].dt.to_period('M').astype(str)
    return df

df = load_data()
global_margin = (df['Profit'].sum() / df['Sales'].sum()) * 100
global_aov = df['Sales'].sum() / df['Order ID'].nunique()

# ======================== 侧边栏 ========================
with st.sidebar:
    st.markdown("### ⚙️ 分析参数配置")
    date_range = st.date_input("⏳ 时序区间 (Time Domain)", [df['Order Date'].min(), df['Order Date'].max()])
    selected_markets = st.multiselect("🌍 空间划分 (Spatial Filter)", sorted(df['Market'].unique()), default=sorted(df['Market'].unique()))
    selected_categories = st.multiselect("📦 类别特征 (Categorical Feature)", sorted(df['Category'].unique()), default=sorted(df['Category'].unique()))
    selected_segments = st.multiselect("👤 实体细分 (Entity Segment)", sorted(df['Segment'].unique()), default=sorted(df['Segment'].unique()))
    
    st.markdown("---")
    st.markdown("### 🤖 AI 大模型驱动中心")
    st.caption("DeepSeek 商业分析引擎已连接。")
    
    base_url = "https://api.deepseek.com/v1"
    model_name = "deepseek-chat"
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = ""

# 数据过滤
filtered_df = df[
    (df['Order Date'].dt.date >= date_range[0]) &
    (df['Order Date'].dt.date <= date_range[1]) &
    (df['Market'].isin(selected_markets)) &
    (df['Segment'].isin(selected_segments)) &
    (df['Category'].isin(selected_categories))
]

# 核心数据计算
total_sales = filtered_df['Sales'].sum()
total_profit = filtered_df['Profit'].sum()
total_orders = filtered_df['Order ID'].nunique()
current_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0
current_aov = total_sales / total_orders if total_orders > 0 else 0

if not filtered_df.empty:
    top_cat = filtered_df.groupby('Category')['Profit'].sum().idxmax()
    market_margin = filtered_df.groupby('Market')['Profit'].sum() / filtered_df.groupby('Market')['Sales'].sum()
    worst_market_name = market_margin.idxmin()
else:
    top_cat, worst_market_name = "暂无", "暂无"

# ======================== 头部：描述性统计全局量 ========================
st.markdown('<div class="academic-title">全球超市多维数据集 (Global Superstore) 可视化分析</div>', unsafe_allow_html=True)
st.markdown('<div class="academic-subtitle">Multidimensional Data Visualization, AI Diagnosis & Exploratory Dashboard</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
col1.metric("总营收 (Total Revenue)", f"${total_sales/1000:,.1f}K", None)
col2.metric("净利润 (Total Profit)", f"${total_profit/1000:,.1f}K", None)
col3.metric("整体利润率 (Profit Margin)", f"{current_margin:.2f}%", f"{current_margin - global_margin:.2f}% (离差)")
col4.metric("平均订单量级 (Avg Order Value)", f"${current_aov:,.0f}", f"${current_aov - global_aov:,.0f} (离差)")

# ======================== AI 智能洞察生成模块 ========================
if st.button("✨ 唤醒 DeepSeek 数据分析顾问 (生成深度报告)"):
    if not HAS_OPENAI:
        st.error("检测到未安装 `openai` 库。")
    elif not api_key:
        st.error("⚠️ 缺少 API Key，无法调用 DeepSeek。")
    else:
        with st.spinner("🤖 DeepSeek 正在进行商业逻辑推理，请稍候..."):
            try:
                context_prompt = f"""
                你现在是一位就职于麦肯锡的顶级商业数据科学家。请根据以下实时数据写一段约 200 字的商业诊断。
                【当前数据概览】：
                - 营收: ${total_sales:,.2f} | 利润: ${total_profit:,.2f} | 利润率: {current_margin:.2f}%
                - 优势品类: {top_cat} | 劣势市场: {worst_market_name}
                请分两段输出：1. 现状剖析；2. 行动建议。
                """
                client = openai.OpenAI(api_key=api_key, base_url=base_url)
                response = client.chat.completions.create(model=model_name, messages=[{"role": "user", "content": context_prompt}], temperature=0.7)
                ai_report = response.choices[0].message.content
                st.markdown(f'<div class="ai-report"><strong>🧠 DeepSeek 实时业务诊断报告：</strong><br><br>{ai_report}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"API 调用失败: {str(e)}")

st.markdown("<br>", unsafe_allow_html=True)

# ======================== 核心视图架构 ========================
tab1, tab2, tab3 = st.tabs(["🗺️ 时空维度演化", "🔗 多维特征相关性", "👥 聚类与群体画像"])

# ----------------- Tab 1: 时空维度演化 -----------------
with tab1:
    t1_c1, t1_c2 = st.columns([1.2, 1])
    with t1_c1:
        with st.container(border=True):
            st.markdown("**图 1-1：时间序列演化分析 (Time Series Evolution)**")
            monthly_data = filtered_df.groupby('YearMonth').agg({'Sales': 'sum', 'Profit': 'sum'}).reset_index().sort_values('YearMonth')
            fig_ts = go.Figure()
            fig_ts.add_trace(go.Scatter(x=monthly_data['YearMonth'], y=monthly_data['Sales'], mode='lines', name='Sales (营收)', line=dict(color='#58A6FF', width=2.5), fill='tozeroy', fillcolor='rgba(56, 139, 253, 0.1)'))
            fig_ts.add_trace(go.Scatter(x=monthly_data['YearMonth'], y=monthly_data['Profit'], mode='lines', name='Profit (利润)', line=dict(color='#FF7B72', width=2)))
            fig_ts.update_layout(height=350, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10), legend=dict(orientation='h', y=1.1))
            st.plotly_chart(fig_ts, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：展现宏观销售额与利润在时序上的同频共振情况，用于识别季节性消费周期。
                - **🎨 编码依据 (Visual Encoding)**：选择**双线面积折线图**。X轴映射连续时间序列；营收以高亮蓝填充面积增加体量感，利润以对比强烈的粉红线条悬浮其上，直观呈现收支净额。
                """)

    with t1_c2:
        with st.container(border=True):
            st.markdown("**图 1-2：空间与类别的联合分布热力图**")
            heat_data = filtered_df.pivot_table(values='Sales', index='Market', columns='Category', aggfunc='sum').fillna(0)
            fig_heat = px.imshow(heat_data, text_auto='.1f', color_continuous_scale='Blues', aspect='auto')
            fig_heat.update_layout(height=350, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=10, r=10, t=30, b=10), coloraxis_showscale=False)
            st.plotly_chart(fig_heat, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：快速定位高频交叉点，直观展现区域市场的消费偏好结构。
                - **🎨 编码依据 (Visual Encoding)**：选择**热力图**。将二维类别变量映射到平面矩阵，通过色彩亮度的深浅连续单色渐变，引导瞬间锁定核心营收区块。
                """)

# ----------------- Tab 2: 多维特征相关性 -----------------
with tab2:
    t2_c1, t2_c2 = st.columns(2)
    with t2_c1:
        with st.container(border=True):
            st.markdown("**图 2-1：离散特征(折扣)与连续特征(利润率)相关性分析**")
            filtered_df['Discount_Level'] = pd.cut(filtered_df['Discount'], bins=[-0.01, 0, 0.1, 0.3, 1.0], labels=['无折扣', '低折扣', '中折扣', '高折扣(>40%)'])
            disc_data = filtered_df.groupby('Discount_Level', observed=False).agg({'Profit': 'sum', 'Sales': 'sum'}).reset_index()
            disc_data['Margin'] = disc_data['Profit'] / disc_data['Sales'] * 100
            fig_disc = px.bar(disc_data, x='Discount_Level', y='Margin', text_auto='.1f', color='Discount_Level', color_discrete_sequence=['#58A6FF', '#388BFD', '#D29922', '#F85149'])
            fig_disc.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
            fig_disc.update_layout(height=350, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=False, margin=dict(t=30), yaxis_title="利润率 (%)")
            st.plotly_chart(fig_disc, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：清晰展示了突破阈值（如高折扣档）后利润率断崖式下跌的商业事实。
                - **🎨 编码依据 (Visual Encoding)**：选择**分类柱状图**。使用高度映射（Length）表达比例。配以冷色到暖色调的过渡，传递从健康到亏损的警示语义。
                """)

    with t2_c2:
        with st.container(border=True):
            st.markdown("**图 2-2：多维特征映射联合散点分布**")
            sample_df = filtered_df.sample(min(2000, len(filtered_df)), random_state=42)
            fig_scatter = px.scatter(sample_df, x='Sales', y='Profit', color='Category', size='Quantity', color_discrete_map={'Technology': '#58A6FF', 'Furniture': '#3FB950', 'Office Supplies': '#D29922'}, opacity=0.6)
            fig_scatter.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.3)")
            fig_scatter.update_layout(height=350, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30), legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center'))
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：展现订单的微观分布，零线下方直观暴露出亏损的伪爆款产品。
                - **🎨 编码依据 (Visual Encoding)**：多维特征映射。融合了 X/Y 位置编码、颜色特征、气泡面积等多种视觉通道。通过半透明度设计有效缓解了数据点过度重叠（Overplotting）问题。
                """)

# ----------------- Tab 3: 聚类与群体画像 -----------------
with tab3:
    t3_c1, t3_c2 = st.columns([1.5, 1])
    with t3_c1:
        with st.container(border=True):
            st.markdown("**图 3-1：基于行为特征的客户价值群体分层 (Clustering Proxy)**")
            cust_df = filtered_df.groupby('Customer ID').agg({'Sales': 'sum', 'Order ID': 'nunique'}).reset_index()
            cust_df.columns = ['Customer ID', 'Monetary', 'Frequency']
            if not cust_df.empty:
                cust_df['Value_Score'] = (cust_df['Monetary'].rank(pct=True) + cust_df['Frequency'].rank(pct=True)) / 2
                cust_df['Cluster'] = pd.cut(cust_df['Value_Score'], bins=[0, 0.4, 0.8, 1.0], labels=['Cluster 3 (低价值)', 'Cluster 2 (中价值)', 'Cluster 1 (高价值)'])
                fig_cluster = px.scatter(cust_df, x='Monetary', y='Frequency', color='Cluster', color_discrete_map={'Cluster 1 (高价值)': '#FF7B72', 'Cluster 2 (中价值)': '#58A6FF', 'Cluster 3 (低价值)': '#484F58'}, opacity=0.7)
                fig_cluster.update_layout(height=350, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30), legend=dict(title="", orientation='h', y=1.1, x=0.5, xanchor='center'))
                st.plotly_chart(fig_cluster, use_container_width=True)
                
            with st.expander("📖 查看图表解读与模型依据"):
                st.markdown("""
                - **🔬 模型解释**：提取频次与金额指标，通过标准化分位数评分（Percentile Rank）融合进行价值分层，模拟 K-Means 聚类结构。
                - **🎨 编码依据**：散点图通过空间邻近度呈现集群效应。高价值核心客户分布在右上角（高销高频），底部的灰色大军则提示沉睡群体的分布。
                """)

    with t3_c2:
        with st.container(border=True):
            st.markdown("**图 3-2：履约特征与优先级交叉画像**")
            ship_data = filtered_df.groupby(['Ship Mode', 'Order Priority']).size().reset_index(name='Count')
            fig_ship = px.bar(ship_data, x='Ship Mode', y='Count', color='Order Priority', color_discrete_sequence=px.colors.qualitative.Pastel, barmode='stack')
            fig_ship.update_layout(height=350, template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=30), xaxis_title="履约模式", yaxis_title="订单密度", legend=dict(orientation='h', y=1.1))
            st.plotly_chart(fig_ship, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：反映物流链路分布，标准运输承担绝对运力，但紧急采购（Critical）在高级别运输方式中构成比极高。
                - **🎨 编码依据**：选择**堆积柱状图**。表达局部与整体的成分（Part-to-Whole）关系，利用内部颜色长度对比呈现比例，大幅节省展示空间。
                """)

# ======================== 底部：数据集结构抽屉 ========================
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📁 展开底层数据集检视 (Dataset Extractor)"):
    display_cols = ['Order ID', 'Order Date', 'Market', 'Category', 'Sales', 'Quantity', 'Discount', 'Profit']
    st.dataframe(filtered_df[display_cols].sort_values('Sales', ascending=False), use_container_width=True, height=250)
"""
Global Superstore 多维数据可视化分析平台
基于 Streamlit + Plotly 构建 (学术架构 + DeepSeek AI 智能体安全版)
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
    page_title="Global Superstore | Multidimensional Analysis",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ======================== 核心 CSS 注入 ========================
st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 2rem; background-color: #FAFAFA; }
.academic-title { font-size: 2.2rem; font-weight: 700; color: #2C3E50; margin-bottom: 0.5rem; border-left: 6px solid #4C78A8; padding-left: 15px; }
.academic-subtitle { font-size: 1.1rem; color: #7F8C8D; margin-bottom: 2rem; padding-left: 21px; }
[data-testid="stMetric"] { background-color: #FFFFFF; border-radius: 8px; padding: 15px 20px; box-shadow: 0 1px 4px rgba(0,0,0,0.05); border: 1px solid #EAECEE; }
[data-testid="stMetricLabel"] { font-size: 0.95rem !important; color: #7F8C8D; font-weight: 500;}
[data-testid="stMetricValue"] { font-size: 1.7rem !important; color: #2C3E50; font-weight: 700; }
div[data-baseweb="tab-list"] { margin-bottom: 1.5rem; }
div[data-baseweb="tab"] { font-size: 1.1rem; font-weight: 600; }
.ai-report { background-color: #F4F6F7; border-left: 4px solid #4C78A8; padding: 15px; border-radius: 5px; font-size: 1.05rem; color: #34495E; margin-top: 15px; line-height: 1.6;}
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
    st.caption("DeepSeek 商业分析引擎已连接。点击主界面的生成按钮即可获取实时智能诊断。")
    
    # 【核心安全修改】：使用 st.secrets 安全读取 API Key
    base_url = "https://api.deepseek.com/v1"
    model_name = "deepseek-chat"
    
    try:
        api_key = st.secrets["DEEPSEEK_API_KEY"]
    except (KeyError, FileNotFoundError):
        api_key = ""
        st.warning("⚠️ 未检测到 API Key，请确保已在 Streamlit Secrets 中配置 `DEEPSEEK_API_KEY`。")

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
        st.error("检测到未安装 `openai` 库，请在终端执行 `pip install openai`。部署云端时请确保 requirements.txt 中有 openai。")
    elif not api_key:
        st.error("⚠️ 缺少 API Key，无法调用 DeepSeek。请在后台配置。")
    else:
        with st.spinner("🤖 DeepSeek 正在读取当前多维时空数据并进行商业逻辑推理，请稍候..."):
            try:
                # 构造上下文感知的 Prompt
                context_prompt = f"""
                你现在是一位就职于麦肯锡的顶级商业数据科学家。请根据以下我系统目前筛选出的实时数据，写一段约 200 字的商业诊断摘要。
                请直接给出洞察，语气专业、严谨、极客，不要说废话，不要有套话。
                
                【当前数据维度概览】：
                - 考察周期: {date_range[0]} 至 {date_range[1]}
                - 达成总营收: ${total_sales:,.2f}
                - 净利润: ${total_profit:,.2f}
                - 当前利润率: {current_margin:.2f}% (全局基准线为 {global_margin:.2f}%)
                - 表现最好的产品大类: {top_cat}
                - 利润率垫底的区域市场: {worst_market_name}
                
                请分两段输出：
                1. 现状剖析：结合上述数据客观评价当前筛选维度的经营健康度。
                2. 行动建议：针对垫底市场或整体利润率，给出一个具体的、可落地的商业破局建议。
                """
                
                client = openai.OpenAI(api_key=api_key, base_url=base_url)
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[{"role": "user", "content": context_prompt}],
                    temperature=0.7
                )
                ai_report = response.choices[0].message.content
                st.markdown(f'<div class="ai-report"><strong>🧠 DeepSeek 实时业务诊断报告：</strong><br><br>{ai_report}</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"API 调用失败。错误信息: {str(e)}")

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
            fig_ts.add_trace(go.Scatter(x=monthly_data['YearMonth'], y=monthly_data['Sales'], mode='lines', name='Sales (营收)', line=dict(color='#4C78A8', width=2), fill='tozeroy', fillcolor='rgba(76, 120, 168, 0.1)'))
            fig_ts.add_trace(go.Scatter(x=monthly_data['YearMonth'], y=monthly_data['Profit'], mode='lines', name='Profit (利润)', line=dict(color='#E45756', width=2)))
            fig_ts.update_layout(height=350, template='plotly_white', margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation='h', y=1.1))
            st.plotly_chart(fig_ts, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：展现宏观销售额与利润在时序上的同频共振情况，用于识别季节性消费周期（如年末假期的销售波峰）。
                - **🎨 编码依据 (Visual Encoding)**：选择**双线面积折线图（Area Line Chart）**。**位置编码**：X轴映射一维连续时间序列，符合人类认知直觉；**色彩编码**：营收以冷色（蓝）填充面积，增加体量感，利润以对比强烈的暖色（红）线条悬浮其上，避免了视觉遮挡，直观呈现收支剪刀差。
                """)

    with t1_c2:
        with st.container(border=True):
            st.markdown("**图 1-2：空间与类别的联合分布热力图**")
            heat_data = filtered_df.pivot_table(values='Sales', index='Market', columns='Category', aggfunc='sum').fillna(0)
            fig_heat = px.imshow(heat_data, text_auto='.1f', color_continuous_scale='Blues', aspect='auto')
            for i in range(len(heat_data)):
                for j in range(len(heat_data.columns)):
                    fig_heat.add_annotation(x=j, y=i, text=f"${heat_data.iloc[i, j]/1e6:.1f}M", showarrow=False, font=dict(size=12))
            fig_heat.update_layout(height=350, template='plotly_white', margin=dict(l=0, r=0, t=30, b=0), coloraxis_showscale=False)
            st.plotly_chart(fig_heat, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：快速定位高频交叉点（如亚太区的 Technology 往往颜色最深），直观展现区域市场的消费偏好结构。
                - **🎨 编码依据 (Visual Encoding)**：选择**热力图（Heatmap）**。**空间编码**：将离散的二维类别变量（市场空间 × 产品类别）映射到平面矩阵；**亮度编码 (Luminance)**：将连续变量（销售额）映射为色彩的明暗度（Sequential 连续单色系渐变），利用前注意视觉（Pre-attentive processing）引导用户瞬间锁定核心利润奶牛区块。
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
            fig_disc = px.bar(disc_data, x='Discount_Level', y='Margin', text_auto='.1f', color='Discount_Level', color_discrete_sequence=['#4C78A8', '#72B7B2', '#F58518', '#E45756'])
            fig_disc.update_traces(texttemplate='%{y:.1f}%', textposition='outside')
            fig_disc.update_layout(height=350, template='plotly_white', showlegend=False, margin=dict(t=30), yaxis_title="利润率 (%)")
            st.plotly_chart(fig_disc, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：揭示了价格战的陷阱，清晰展示了突破阈值（如高折扣档）后利润率断崖式下跌的商业事实。
                - **🎨 编码依据 (Visual Encoding)**：选择**分类柱状图（Bar Chart）**。针对经过特征工程离散化后的有序变量（Ordinal variable），使用高度映射（Length/Height）来表达比例是最精确的视觉通道。配以冷暖色调（蓝到红）的过渡，传递了从健康到亏损的警示语义。
                """)

    with t2_c2:
        with st.container(border=True):
            st.markdown("**图 2-2：多维特征映射联合散点分布**")
            sample_df = filtered_df.sample(min(2000, len(filtered_df)), random_state=42)
            fig_scatter = px.scatter(sample_df, x='Sales', y='Profit', color='Category', size='Quantity', color_discrete_map={'Technology': '#4C78A8', 'Furniture': '#72B7B2', 'Office Supplies': '#F58518'}, opacity=0.6)
            fig_scatter.add_hline(y=0, line_dash="dash", line_color="rgba(0,0,0,0.3)")
            fig_scatter.update_layout(height=350, template='plotly_white', margin=dict(t=30), legend=dict(orientation='h', y=1.1, x=0.5, xanchor='center'))
            st.plotly_chart(fig_scatter, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：展现订单的微观分布，虚线下方揭示了大量产生负利润（亏损）的伪爆款产品。
                - **🎨 编码依据 (Visual Encoding)**：经典的高维数据投影。在此散点图中完美融合了 4 种视觉编码：**X/Y 位置编码**（单笔订单的销售额与利润的正交关系）、**颜色分类编码**（色相映射产品大类，Hue）、**大小面积编码**（气泡半径映射购买件数）。通过透明度（Opacity=0.6）有效缓解了大量数据点产生的 Overplotting（过度重叠）问题。
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
                fig_cluster = px.scatter(cust_df, x='Monetary', y='Frequency', color='Cluster', color_discrete_map={'Cluster 1 (高价值)': '#E45756', 'Cluster 2 (中价值)': '#4C78A8', 'Cluster 3 (低价值)': '#BAB0AC'}, opacity=0.7)
                fig_cluster.update_layout(height=350, template='plotly_white', margin=dict(t=30), legend=dict(title="", orientation='h', y=1.1, x=0.5, xanchor='center'))
                st.plotly_chart(fig_cluster, use_container_width=True)
                
            with st.expander("📖 查看图表解读与模型依据"):
                st.markdown("""
                - **🔬 模型解释**：在数据预处理阶段，提取客户的购买频次 (Frequency) 与累计金额 (Monetary)，通过计算特征的**标准化分位数评分（Percentile Rank）**并进行特征融合，模拟实现了类似 K-Means 的聚类逻辑。
                - **🎨 编码依据**：散点图通过空间距离（Proximity）天然呈现集群效应。高价值核心客户（红点）分布在右上角，呈现“高销高频”的完美画像；而占据底部的灰色大军则提示我们需要通过精细化运营唤醒的沉睡客户。
                """)

    with t3_c2:
        with st.container(border=True):
            st.markdown("**图 3-2：履约特征与优先级交叉画像**")
            ship_data = filtered_df.groupby(['Ship Mode', 'Order Priority']).size().reset_index(name='Count')
            fig_ship = px.bar(ship_data, x='Ship Mode', y='Count', color='Order Priority', color_discrete_sequence=px.colors.qualitative.Pastel, barmode='stack')
            fig_ship.update_layout(height=350, template='plotly_white', margin=dict(t=30), xaxis_title="履约模式", yaxis_title="订单密度", legend=dict(orientation='h', y=1.1))
            st.plotly_chart(fig_ship, use_container_width=True)
            
            with st.expander("📖 查看图表解读与视觉编码依据"):
                st.markdown("""
                - **📈 数据洞察**：清晰反映了物流链路压力，Standard 模式承担了绝对运力，但加急订单（Critical）在高级别运输方式中占比畸高。
                - **🎨 编码依据**：选择**堆积柱状图（Stacked Bar Chart）**。这是一种典型的表达“整体与局部成分”（Part-to-Whole）关系的图表。通过统一的基线长度对比总量规模，利用内部颜色的长度对比呈现分类比例，比并排柱状图更节约展示空间。
                """)

# ======================== 底部：数据集结构抽屉 ========================
st.markdown("<br>", unsafe_allow_html=True)
with st.expander("📁 展开底层数据集检视 (Dataset Extractor)"):
    display_cols = ['Order ID', 'Order Date', 'Market', 'Category', 'Sales', 'Quantity', 'Discount', 'Profit']
    st.dataframe(filtered_df[display_cols].sort_values('Sales', ascending=False), use_container_width=True, height=250)
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# --- 页面配置 ---
st.set_page_config(
    page_title="避雷观察薯 | 小红书决策助手",
    page_icon="🥔",
    layout="wide"
)

# --- 深度还原小红书红视觉风格 ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stTextInput>div>div>input { border-radius: 12px; border: 1px solid #ff2442; height: 45px; }
    .stButton>button { background-color: #ff2442; color: white; border-radius: 20px; border: none; font-weight: bold; }
    .report-card { background-color: #fffafa; padding: 25px; border-radius: 20px; border: 1px solid #ffe4e6; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .note-card { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 15px; height: 130px; transition: 0.3s; }
    .note-card:hover { border-color: #ff2442; box-shadow: 0px 4px 12px rgba(255,36,66,0.1); }
    .note-tag { color: #ff2442; font-size: 0.75em; font-weight: bold; border: 1px solid #ff2442; padding: 2px 6px; border-radius: 4px; }
    h1 { color: #333333; font-family: "Microsoft YaHei", sans-serif; margin-bottom: 0px; }
    .subtitle { color: #666666; font-size: 1.1em; margin-bottom: 10px; }
    .guide-text { color: #ff2442; font-size: 0.9em; font-weight: bold; margin-bottom: 20px; background-color: #fff5f5; padding: 8px 15px; border-radius: 8px; display: inline-block; }
    .red-text { color: #ff2442; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心模拟数据库 ---
mock_db = {
    "戴森": {
        "conclusion": "特定人群慎买",
        "scores": [9, 3, 7, 8, 9],
        "risks": {"痒点": 45, "中雷": 35, "大雷": 15, "致命雷点": 5},
        "summary": "雷点主要集中在‘价格溢价’及‘特定发质适配’。这属于预期管理问题，而非产品硬伤。",
        "consumer_view": "预算充足且追求性能可入；若追求性价比，此雷点对你而言是【大雷】。",
        "kol_view": "建议内容重点放在‘高效率生活’场景，避开‘省钱攻略’。",
        "brand_view": "建议强化‘听劝改进’形象，增加售后延保权益以冲抵负面感。",
        "notes": [
            {"title": "大冤种才买戴森？用了一年说实话", "tag": "真实体验"},
            {"title": "细软塌避雷！戴森这款真的吹不蓬", "tag": "干货建议"},
            {"title": "戴森售后太闹心了，维修费够买个新的", "tag": "售后吐槽"},
            {"title": "给想买戴森的姐妹一个建议：先看发质", "tag": "深度避雷"},
            {"title": "平替真的能打过戴森吗？对比测评来了", "tag": "对比分析"},
            {"title": "戴森吸尘器续航翻车，这雷我替你们踩了", "tag": "避雷预警"}
        ]
    },
    "lululemon": {
        "conclusion": "放心买 (高确定性)",
        "scores": [9, 5, 8, 7, 8],
        "risks": {"痒点": 65, "中雷": 25, "大雷": 8, "致命雷点": 2},
        "summary": "避雷帖多为‘面料起球’等体验瑕疵。核心剪裁优势稳固。",
        "consumer_view": "只要不纠结微小面料损耗，基本不翻车。这属于轻微瑕疵。",
        "kol_view": "测评时可客观提到起球现象，建立真实人设。",
        "brand_view": "建议推出官方护理指南，主动回应‘痒点’。",
        "notes": [
            {"title": "lulu起球是通病吗？这价位我真的心疼", "tag": "品质吐槽"},
            {"title": "Align系列避雷：穿了三次裆部就...", "tag": "真实踩雷"},
            {"title": "别瞎买lulu！这几个颜色显胖到哭", "tag": "审美避雷"},
            {"title": "除了贵没毛病？聊聊lulu的溢价逻辑", "tag": "理性讨论"},
            {"title": "lulu售后真香，起球竟然给换新的了", "tag": "售后反转"},
            {"title": "听劝！大体重姐妹避雷这款运动内衣", "tag": "避雷建议"}
        ]
    },
    "某网红护肤品": {
        "conclusion": "有致命雷点 (极高风险)",
        "scores": [3, 9, 4, 10, 2],
        "risks": {"痒点": 5, "中雷": 15, "大雷": 30, "致命雷点": 50},
        "summary": "高频反馈‘过敏’与‘虚假宣传’。雷点已触及核心价值。",
        "consumer_view": "这是【真雷】。无论促销多大都不建议敏肌尝试。",
        "kol_view": "风险极大，建议暂时放弃该选题。",
        "brand_view": "必须立即停止滤镜营销，回归‘产品真相’。",
        "notes": [
            {"title": "全脸烂脸！避雷某网红面霜，求扩散", "tag": "致命雷点"},
            {"title": "别被营销骗了，这成分真的没用", "tag": "成分拆解"},
            {"title": "退钱！客服态度极其恶劣，避雷这家店", "tag": "服务翻车"},
            {"title": "滤镜碎一地，线下实测和博主完全不同", "tag": "虚假宣传"},
            {"title": "敏肌姐妹快跑！这波雷我先替你们排了", "tag": "风险预警"},
            {"title": "用了两周黑头更多了，避雷避雷避雷！", "tag": "功效吐槽"}
        ]
    }
}

# --- 侧边栏 ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff2442;'>🥔 避雷观察薯</h2>", unsafe_allow_html=True)
    # 换成更稳定的 Logo 来源或使用文字替代
    st.markdown("<h1 style='text-align: center; font-size: 50px;'>🥔</h1>", unsafe_allow_html=True)
    st.write("---")
    st.write("🔍 **核心功能**")
    st.caption("1. 避雷信息聚合\n2. 问题归因分类\n3. 痛痒程度分级\n4. 角色视图翻译")
    st.write("---")
    st.markdown("<p style='color: #ff2442; font-weight: bold;'>🎯 搜索范围指引：</p>", unsafe_allow_html=True)
    st.caption("• 戴森\n• lululemon\n• 某网红护肤品")
    st.write("---")
    st.info("💡 **Builder Note**\n将情绪化避雷帖，转化为结构化分级建议。")

# --- 主界面 ---
st.markdown("<h1><span style='color: #ff2442;'>🥔</span> 避雷观察薯 | 风险判断引擎</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>帮你看懂避雷帖，到底是小毛病还是致命问题。</p>", unsafe_allow_html=True)

# 增加显眼的搜索范围提示
st.markdown("<div class='guide-text'>💡 薯薯目前已收录：戴森、lululemon、某网红护肤品。更多品牌正在入库中...</div>", unsafe_allow_html=True)

# 搜索与跳转逻辑
search_query = st.text_input("", placeholder="请输入品牌名称并回车，如：戴森")

target_brand = "戴森" # 默认展示
if search_query:
    found = False
    for b_name in mock_db.keys():
        if b_name.lower() in search_query.lower():
            target_brand = b_name
            found = True
            break
    if not found:
        st.error("⚠️ 薯薯还没收录这个品牌，请尝试搜索：戴森、lululemon、某网红护肤品")

# 展示内容
res = mock_db[target_brand]
st.divider()

col_left, col_right = st.columns([1, 1.2])

with col_left:
    st.markdown(f"""
    <div class="report-card">
        <h3>🚨 综合判定：<span class="red-text">{res['conclusion']}</span></h3>
        <p style="color: #666; font-size: 15px;">{res['summary']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 雷达图
    categories = ['品质','性价比','售后','营销滤镜','耐用度']
    fig_radar = go.Figure(data=go.Scatterpolar(r=res["scores"], theta=categories, fill='toself', line_color='#ff2442'))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
        showlegend=False, margin=dict(t=30, b=30, l=30, r=30), height=380
    )
    st.plotly_chart(fig_radar, use_container_width=True)

with col_right:
    st.write("### 📊 避雷痛痒分级分布")
    st.caption("基于评论严重性、可信度及出现频次综合计算")
    risk_df = pd.DataFrame({"风险等级": list(res["risks"].keys()), "占比": list(res["risks"].values())})
    fig_risk = px.bar(risk_df, x="占比", y="风险等级", orientation='h', 
                     color="风险等级", color_discrete_map={"痒点":"#ffccd5","中雷":"#ffb3ba","大雷":"#ff8fa3","致命雷点":"#ff2442"})
    fig_risk.update_layout(showlegend=False, height=350)
    st.plotly_chart(fig_risk, use_container_width=True)

# 角色视图 (Tabs)
st.write("---")
st.write("### 🔍 角色化视角分析")
t1, t2, t3 = st.tabs(["💡 消费者决策", "✍️ 达人内容助手", "🏢 品牌听劝看板"])
with t1: st.info(res["consumer_view"])
with t2: st.info(res["kol_view"])
with t3: st.info(res["brand_view"])

# 帖子展示区
st.write("---")
st.write(f"### 📱 相关避雷帖参考 ({target_brand})")
rows = [res["notes"][i:i + 3] for i in range(0, 6, 3)]
for row in rows:
    cols = st.columns(3)
    for i, note in enumerate(row):
        with cols[i]:
            st.markdown(f"""
            <div class="note-card">
                <span class="note-tag">#{note['tag']}</span><br>
                <p style="margin-top:10px; font-weight:bold; font-size:14px;">{note['title']}</p>
                <small style="color: #999;">刚刚 · 来自小红书</small>
            </div>
            """, unsafe_allow_html=True)

# PRD 逻辑底座
st.write("---")
with st.expander("📝 查看《避雷观察薯》产品设计白皮书 (PRD 核心)"):
    st.markdown("""
    ### 1. 产品核心价值
    **避雷观察薯** 解决的是“决策瘫痪”。它将原始避雷帖转化为**结构化、可分级、可决策**的判断结果。
    
    ### 2. 痛痒分级模型逻辑
    系统将风险分为四级：
    - **痒点**：轻微瑕疵，不影响核心功能。
    - **中雷**：影响部分体验，取决于个人预期。
    - **大雷**：核心体验不稳定，建议对比替代品。
    - **致命雷点**：动摇信任基础，高风险预警。
    
    ### 3. 商业化潜力
    - **C端**：降低决策成本。
    - **B端**：驱动品牌“听劝改进”。
    - **K端**：辅助真诚测评。
    """)

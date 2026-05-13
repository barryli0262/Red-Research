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

# --- 视觉风格定制 ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { background-color: #ff2442; color: white; border-radius: 20px; width: 100%; border: none; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 12px; border: 1px solid #ff2442; }
    .red-text { color: #ff2442; font-weight: bold; }
    .report-card { background-color: #fffafa; padding: 20px; border-radius: 15px; border: 1px solid #ffe4e6; margin-bottom: 20px; }
    .note-card { background-color: #ffffff; padding: 15px; border-radius: 12px; border: 1px solid #eee; margin-bottom: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    .note-tag { color: #ff2442; font-size: 0.8em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心模拟数据库 ---
mock_db = {
    "戴森": {
        "conclusion": "特定人群慎买",
        "scores": [9, 3, 7, 8, 9],
        "risks": {"痒点": 45, "中雷": 35, "大雷": 15, "致命雷点": 5},
        "summary": "雷点主要集中在‘价格溢价’及‘特定发质适配’。这属于预期管理问题。",
        "consumer_view": "预算充足且追求性能可入；若追求性价比，此雷点对你而言是【大雷】。",
        "kol_view": "建议内容重点放在‘高效率生活’，避开‘省钱攻略’。",
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
        "summary": "高频反馈‘过敏’与‘虚假宣传’。属于信任基础动摇。",
        "consumer_view": "这是【真雷】。无论促销多大都不建议敏肌尝试。",
        "kol_view": "风险极大，建议暂时放弃该选题。",
        "brand_view": "必须立即停止滤镜营销，回归‘产品真相’。",
        "notes": [
            {"title": "全脸烂脸！避雷某网红面霜，求扩散", "tag": "致命雷点"},
            {"title": "别被营销骗了，这成分真的没用", "tag": "成分拆解"},
            {"title": "退钱！客服态度极其恶劣，避雷这家店", "tag": "服务翻车"},
            {"title": "滤镜碎一地，线下实测和博主发的完全不同", "tag": "虚假宣传"},
            {"title": "敏肌姐妹快跑！这波雷我先替你们排了", "tag": "风险预警"},
            {"title": "用了两周黑头更多了，避雷避雷避雷！", "tag": "功效吐槽"}
        ]
    }
}

# --- 主界面逻辑 ---
st.markdown("<h1><span style='color: #ff2442;'>🥔</span> 避雷观察薯 | 风险判断引擎</h1>", unsafe_allow_html=True)

# 搜索输入处理
search_query = st.text_input("", placeholder="输入品牌或产品，例如：戴森、lululemon...")

# 逻辑跳转：优先判断搜索内容，若无搜索则判断侧边栏选择
target_brand = ""
if search_query:
    # 模糊匹配
    for b_name in mock_db.keys():
        if b_name.lower() in search_query.lower():
            target_brand = b_name
            break
else:
    # 如果没搜索，侧边栏可选（默认为第一个）
    target_brand = st.sidebar.radio("或从样本中选择：", list(mock_db.keys()))

if target_brand in mock_db:
    res = mock_db[target_brand]
    st.divider()
    
    # 结果展示
    col_left, col_right = st.columns([1, 1.2])
    with col_left:
        st.markdown(f"""
        <div class="report-card">
            <h3>🚨 综合判定：<span class="red-text">{res['conclusion']}</span></h3>
            <p style="color: #666;">{res['summary']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 雷达图
        categories = ['品质','性价比','售后','营销滤镜','耐用度']
        fig_radar = go.Figure(data=go.Scatterpolar(r=res["scores"], theta=categories, fill='toself', line_color='#ff2442'))
        fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 10])), showlegend=False, height=350)
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_right:
        st.write("### 📊 风险分级分布")
        risk_df = pd.DataFrame({"等级": list(res["risks"].keys()), "占比": list(res["risks"].values())})
        fig_risk = px.bar(risk_df, x="占比", y="等级", orientation='h', 
                         color="等级", color_discrete_map={"痒点":"#ffccd5","中雷":"#ffb3ba","大雷":"#ff8fa3","致命雷点":"#ff2442"})
        st.plotly_chart(fig_risk, use_container_width=True)

    # 虚构帖子展示区
    st.write("---")
    st.write(f"### 📱 相关避雷帖参考 ({target_brand})")
    n_cols = 3
    rows = [res["notes"][i:i + n_cols] for i in range(0, len(res["notes"]), n_cols)]
    for row in rows:
        cols = st.columns(n_cols)
        for i, note in enumerate(row):
            with cols[i]:
                st.markdown(f"""
                <div class="note-card">
                    <span class="note-tag">#{note['tag']}</span><br>
                    <b>{note['title']}</b><br>
                    <small style="color: #999;">刚刚 · 来自小红书</small>
                </div>
                """, unsafe_allow_html=True)

    # PRD 逻辑底座
    st.write("---")
    with st.expander("📝 查看《避雷观察薯》设计逻辑 (PRD 摘要)"):
        st.write("1. **定位**：嵌入式避雷分析工具\n2. **模型**：基于失误严重性与可信度的痛痒分级\n3. **目标**：不放大负面，只解释风险")
else:
    st.info("🥔 薯薯正在等待你的指令！请在上方搜索品牌，或从侧边栏选择预置样本。")

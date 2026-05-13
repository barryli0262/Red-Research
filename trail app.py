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

# --- 小红书原生视觉风格定制 ---
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    .stButton>button { background-color: #ff2442; color: white; border-radius: 20px; width: 100%; border: none; font-weight: bold; }
    .stTextInput>div>div>input { border-radius: 12px; border: 1px solid #ff2442; }
    h1, h2, h3 { color: #333333; font-family: "Microsoft YaHei", sans-serif; }
    .red-text { color: #ff2442; font-weight: bold; }
    .report-card { background-color: #fffafa; padding: 25px; border-radius: 20px; border: 1px solid #ffe4e6; box-shadow: 2px 2px 10px rgba(0,0,0,0.05); }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f8f8f8; border-radius: 10px 10px 0 0; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #ff2442 !important; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 核心模拟数据库 (对齐“避雷观察薯”PRD) ---
mock_db = {
    "戴森": {
        "conclusion": "特定人群慎买",
        "scores": [9, 3, 7, 8, 9],  # 品质, 性价比, 售后, 营销滤镜, 耐用度
        "risks": {"痒点": 45, "中雷": 35, "大雷": 15, "致命雷点": 5},
        "summary": "雷点主要集中在‘价格溢价’及‘特定发质适配’。这属于【预期管理问题】，而非产品硬伤。",
        "consumer_view": "如果你追求极致性能且预算充足，可入；若追求性价比，此雷点对你而言是【大雷】。",
        "kol_view": "建议内容重点放在‘高效率生活’，避开‘省钱攻略’，可有效降低评论区噪音。",
        "brand_view": "识别到高频劝退因素为‘贵’。建议强化‘听劝改进’形象，增加售后延保权益以冲抵负面感。"
    },
    "lululemon": {
        "conclusion": "放心买 (高确定性)",
        "scores": [9, 5, 8, 7, 8],
        "risks": {"痒点": 65, "中雷": 25, "大雷": 8, "致命雷点": 2},
        "summary": "避雷帖多为‘面料起球’等体验瑕疵。核心剪裁优势稳固，雷点等级多为【痒点】。",
        "consumer_view": "只要不纠结微小面料损耗，基本不翻车。这属于【轻微瑕疵】，不影响核心决策。",
        "kol_view": "测评时可客观提到起球现象，建立真实人设，因为该雷点不足以动摇购买理由。",
        "brand_view": "属于【服务提升型】机会。建议推出官方护理指南，主动回应‘痒点’，提升品牌诚意。"
    },
    "某网红护肤品": {
        "conclusion": "有致命雷点 (极高风险)",
        "scores": [3, 9, 4, 10, 2],
        "risks": {"痒点": 5, "中雷": 15, "大雷": 30, "致命雷点": 50},
        "summary": "高频反馈‘过敏’与‘虚假宣传’。雷点已触及核心价值，属于【信任基础动摇】。",
        "consumer_view": "这是【真雷】。无论促销力度多大，都不建议敏肌尝试，避雷建议采纳度：极高。",
        "kol_view": "风险极大，建议暂时放弃该选题。若已发布，建议在评论区置顶真实风险预警。",
        "brand_view": "核心致命雷点为‘成分争议’。必须立即停止滤镜营销，回归‘产品真相’，否则流失率不可逆。"
    }
}

# --- 侧边栏 ---
with st.sidebar:
    st.markdown("<h2 style='color: #ff2442;'>🥔 避雷观察薯</h2>", unsafe_allow_html=True)
    st.write("---")
    st.write("🔍 **核心功能**")
    st.caption("1. 避雷信息聚合\n2. 问题归因分类\n3. 痛痒程度分级\n4. 角色视图翻译")
    st.write("---")
    sample = st.radio("点击样本查看分析结果", ["戴森", "lululemon", "某网红护肤品"])
    st.write("---")
    st.info("💡 **Builder Note**\n本工具将小红书海量情绪化避雷帖，通过 PRD 定义的逻辑转化为结构化分级建议。")

# --- 主界面 ---
st.markdown("<h1><span style='color: #ff2442;'>🥔</span> 避雷观察薯 | 风险判断引擎</h1>", unsafe_allow_html=True)
st.write("帮你看懂避雷帖，到底是小毛病还是致命问题。")

search_query = st.text_input("", value=sample, placeholder="输入品牌或产品，看雷点严重程度...")

if search_query in mock_db:
    res = mock_db[search_query]
    
    # 结果展示区
    st.markdown("---")
    col_left, col_right = st.columns([1, 1.2])
    
    with col_left:
        st.markdown(f"""
        <div class="report-card">
            <h3>🚨 综合判定：<span class="red-text">{res['conclusion']}</span></h3>
            <p style="color: #666; font-size: 15px;">{res['summary']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 雷达图绘制
        categories = ['品质','性价比','售后','营销滤镜','耐用度']
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Scatterpolar(
            r=res["scores"],
            theta=categories,
            fill='toself',
            line_color='#ff2442',
            name='风险画像'
        ))
        fig_radar.update_layout(
            polar=dict(radialaxis=dict(visible=True, range=[0, 10])),
            showlegend=False,
            margin=dict(t=30, b=30, l=30, r=30),
            height=350
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with col_right:
        st.write("### 📊 避雷痛痒分级分布")
        st.caption("基于评论严重性、可信度及出现频次综合计算")
        
        risk_df = pd.DataFrame({
            "风险等级": list(res["risks"].keys()),
            "影响占比": list(res["risks"].values()),
            "颜色": ["#ffccd5", "#ffb3ba", "#ff8fa3", "#ff2442"]
        })
        
        fig_risk = px.bar(
            risk_df, 
            x="影响占比", 
            y="风险等级", 
            orientation='h',
            color="风险等级",
            color_discrete_map={"痒点":"#ffccd5","中雷":"#ffb3ba","大雷":"#ff8fa3","致命雷点":"#ff2442"}
        )
        fig_risk.update_layout(showlegend=False, height=350, margin=dict(t=20, b=20))
        st.plotly_chart(fig_risk, use_container_width=True)

    # 角色视图
    st.write("---")
    st.write("### 🔍 角色化视角分析 (PRD 核心输出)")
    t1, t2, t3 = st.tabs(["💡 消费者决策", "✍️ 达人内容助手", "🏢 品牌听劝看板"])
    
    with t1:
        st.markdown(f"<div class='report-card'><b>决策建议：</b><br>{res['consumer_view']}</div>", unsafe_allow_html=True)
    with t2:
        st.markdown(f"<div class='report-card'><b>内容建议：</b><br>{res['kol_view']}</div>", unsafe_allow_html=True)
    with t3:
        st.markdown(f"<div class='report-card'><b>优化方向：</b><br>{res['brand_view']}</div>", unsafe_allow_html=True)

else:
    st.info("🥔 **薯薯提示**：请输入左侧列表中的品牌进行深度解析。实际版本已预留 Perplexity API 接口，支持实时全网避雷信息归因分析。")

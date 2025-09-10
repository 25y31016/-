import streamlit as st
import requests
import datetime
import pytz
import re
import plotly.graph_objects as go
import random

# ===== 한국 시간 =====
KST = pytz.timezone("Asia/Seoul")
today = datetime.datetime.now(KST).strftime("%Y%m%d")

# ===== Streamlit 기본 설정 =====
st.set_page_config(page_title="상암고 급식", page_icon="🍴", layout="wide")

# ===== CSS =====
st.markdown("""
    <style>
        body { background-color: #f9f9f9; color: #222222; }
        .title { font-size: 40px; font-weight: bold; text-align: center; margin-bottom: 20px; color: #1a1a1a; }
        .shake-emoji { display:inline-block; animation: shake 0.8s 6; font-size:25px; }
        @keyframes shake { 0% { transform: translate(1px, 1px) rotate(0deg); }
                           20% { transform: translate(-1px, -2px) rotate(-2deg); }
                           40% { transform: translate(-3px, 0px) rotate(2deg); }
                           60% { transform: translate(3px, 2px) rotate(0deg); }
                           80% { transform: translate(1px, -1px) rotate(2deg); }
                           100% { transform: translate(-1px, 2px) rotate(-2deg); } }
        .popup { position: fixed; top: 50%; left: 50%; transform: translate(-50%, -50%);
                 background: white; padding: 25px; border-radius: 15px; box-shadow: 0px 4px 20px rgba(0,0,0,0.3);
                 z-index: 9999; max-width: 400px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ===== Fun Fact 리스트 =====
fun_facts = [
    "🥦 브로콜리, 시금치 등 녹색 채소는 항산화 성분이 풍부해 면역력 강화에 도움을 줘요.",
    "🥛 우유와 유제품은 칼슘이 풍부해 성장기 학생의 뼈 건강에 필수예요.",
    "🍚 밥, 감자, 고구마 같은 탄수화물은 뇌의 에너지원으로 중요합니다.",
    "🍗 달걀, 닭고기, 생선 등 단백질은 근육 성장과 회복에 좋아요.",
    "🥕 당근, 고구마 등 오렌지색 채소는 비타민 A가 풍부해 시력 보호에 도움됩니다.",
    "🥩 소고기, 돼지고기, 시금치 등 철분이 풍부한 음식은 피로를 줄여줍니다.",
    "🧄 마늘, 양파 등은 혈액순환과 면역력 강화에 도움을 줍니다.",
    "🥜 견과류는 건강한 지방과 단백질을 함께 제공해요.",
    "🍊 과일에는 비타민 C가 풍부해 피로 회복과 피부 건강에 도움됩니다.",
    "🥗 채소를 충분히 섭취하면 소화 건강과 변비 예방에 좋아요.",
    "🍯 천연 꿀은 면역력 강화와 항균 작용에 도움을 줍니다."
]

# ===== 제목 =====
st.markdown("<div class='title'>🍴 상암고 오늘의 급식 🍴</div>", unsafe_allow_html=True)

# ===== 날짜 선택 =====
selected_date = st.date_input("날짜 선택", datetime.datetime.now(KST)).strftime("%Y%m%d")

# ===== NEIS API 요청 =====
url = f"https://open.neis.go.kr/hub/mealServiceDietInfo?ATPT_OFCDC_SC_CODE=B10&SD_SCHUL_CODE=7010806&Type=json&MLSV_YMD={selected_date}"
response = requests.get(url)
data = response.json()

if "mealServiceDietInfo" not in data:
    st.warning("해당 날짜에는 급식 정보가 없습니다 🍽️")
else:
    meals = data["mealServiceDietInfo"][1]["row"]

    for meal in meals:
        meal_name = meal["MMEAL_SC_NM"]
        dish_str = meal["DDISH_NM"].replace("<br/>", "\n")
        clean = re.sub(r"\d|\(|\)|\.", "", dish_str).strip()
        nutr_info = meal.get("NTR_INFO", "").replace("<br/>", "\n").strip()

        with st.expander(f"{meal_name} 🍱"):
            if meal_name == "중식":
                st.markdown('<div class="shake-emoji">🍽️</div>', unsafe_allow_html=True)

            st.markdown(f"<pre style='font-size:15px; background:#f1f1f1; padding:12px; border-radius:12px;'>{clean}</pre>", unsafe_allow_html=True)

            if nutr_info:
                st.markdown(f"**🔍 영양 정보:**\n{nutr_info}")

                # ====== 영양소 정리 및 출력 ======
                nutr_dict = {}
                matches = re.findall(r"([가-힣A-Za-z]+).*?\)?\s*:\s*([\d.]+)", nutr_info)
                for key, val in matches:
                    clean_key = key.strip()
                    unit_match = re.search(r"\((.*?)\)", key)
                    unit = unit_match.group(1) if unit_match else ""
                    nutr_dict[clean_key] = {"value": float(val), "unit": unit}

                # 제목 변경
                st.markdown("### 📊 오늘의 영양소 섭취량")
                # 영양소: 값 단위 형식으로 출력
                for name, info in nutr_dict.items():
                    display_text = f"{name}: {info['value']} {info['unit']}" if info['unit'] else f"{name}: {info['value']}"
                    st.write(display_text)

                # ====== 탄단지 Pie ======
                labels, values = [], []
                colors = ['#ffcc80', '#81d4fa', '#ffab91']
                for n in ["탄수화물", "단백질", "지방"]:
                    if n in nutr_dict:
                        labels.append(n)
                        values.append(nutr_dict[n]["value"])

                total_cal = 0
                if "탄수화물" in nutr_dict: total_cal += nutr_dict["탄수화물"]["value"]*4
                if "단백질" in nutr_dict: total_cal += nutr_dict["단백질"]["value"]*4
                if "지방" in nutr_dict: total_cal += nutr_dict["지방"]["value"]*9
                if total_cal > 0:
                    st.success(f"🔥 예상 총 칼로리: 약 {int(total_cal)} kcal")

                if values:
                    fig_pie = go.Figure(
                        data=[go.Pie(labels=labels, values=values, hole=0.3,
                                     marker_colors=colors, textinfo='label+percent')]
                    )
                    fig_pie.update_layout(title="탄단지 비율", margin=dict(t=40, b=40))
                    st.plotly_chart(fig_pie, use_container_width=True)

                # ====== 영양소 Bar (단위 포함, trace 이름 지정) ======
                fig_bar = go.Figure()
                for name, info in nutr_dict.items():
                    text_label = f"{info['value']} {info['unit']}" if info['unit'] else str(info['value'])
                    fig_bar.add_trace(go.Bar(
                        x=[name],
                        y=[info["value"]],
                        text=[text_label],
                        textposition="outside",
                        name=name  # trace 이름을 영양소로 지정
                    ))
                fig_bar.update_layout(
                    title="영양소별 섭취량",
                    yaxis_title="값",
                    xaxis_title="영양소",
                    margin=dict(t=40, b=40)
                )
                st.plotly_chart(fig_bar, use_container_width=True)

                # ====== 칼로리 기여도 Bar ======
                cal_labels, cal_values = [], []
                for n in ["탄수화물", "단백질", "지방"]:
                    if n in nutr_dict:
                        cal_labels.append(n)
                        cal_values.append(nutr_dict[n]["value"] * (4 if n!="지방" else 9))
                if cal_values:
                    fig_cal = go.Figure(
                        data=[go.Bar(
                            x=cal_labels,
                            y=cal_values,
                            text=[f"{v:.0f} kcal" for v in cal_values],
                            textposition="outside",
                            name="칼로리"
                        )]
                    )
                    fig_cal.update_layout(title="에너지 기여도 (kcal)", yaxis_title="kcal", margin=dict(t=40, b=40))
                    st.plotly_chart(fig_cal, use_container_width=True)

                # ====== 레이다 차트 ======
                if values:
                    fig_radar = go.Figure()
                    fig_radar.add_trace(go.Scatterpolar(
                        r=values + [values[0]],
                        theta=labels + [labels[0]],
                        fill='toself',
                        name="영양 비율"
                    ))
                    fig_radar.update_layout(polar=dict(radialaxis=dict(visible=True)), title="영양소 비율 레이다 차트")
                    st.plotly_chart(fig_radar, use_container_width=True)

            else:
                st.info("⚠️ 영양 정보가 제공되지 않았습니다.")

# ===== Fun Fact 팝업 =====
if "show_popup" not in st.session_state:
    st.session_state.show_popup = False

if st.button("💡 오늘의 Fun Fact 보기"):
    st.session_state.show_popup = True

if st.session_state.show_popup:
    fun_fact = random.choice(fun_facts)
    st.markdown(f"""
        <div class="popup">
            <h3>💡 오늘의 Fun Fact</h3>
            <p style="font-size:16px;">{fun_fact}</p>
            <form action="" method="get">
                <button name="close" style="padding:8px 15px; border:none; border-radius:8px; background:#444; color:white; cursor:pointer;">닫기</button>
            </form>
        </div>
    """, unsafe_allow_html=True)

    if "close" in st.query_params:
        st.session_state.show_popup = False


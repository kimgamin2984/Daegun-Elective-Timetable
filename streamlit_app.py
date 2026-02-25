import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO
import matplotlib.font_manager as fm

elective = set()
grade = st.selectbox("학년", ["1", "2", "3"], index=0)
class_nm = st.selectbox("반", [str(i) for i in range(1, 10)], index=0)
code1 = float(f'{grade}0{class_nm}1')

df = pd.read_excel('Timetable_all_raw.xlsx', header=None)
print(df)
raw = df.loc[df[0] == code1, 2:36].iloc[0]
if grade != '1':
    dic = {}
    for i in 'ABCDEFGH':
        dic[f'선택{i}'] = st.text_input(f'선택{i}')
        elective.add(f'선택{i}')
    raw = raw.tolist()
    for i in range(35):
        if raw[i] in elective:
            raw[i] = dic[raw[i]]
result = np.array(raw).reshape(-1,7).T

def create_timetable_image(data_array):
    # 1. 요일과 교시 라벨 준비
    days = ['월', '화', '수', '목', '금']
    periods = [f'{i}교시' for i in range(1, 8)]

    # 2. 6x8 데이터프레임 재구성 (요일 행 + 교시 열 추가)
    # result가 (5, 7)이므로 전치(T) 상태라면 행이 요일, 열이 교시일 수 있음
    # 만약 result가 (7, 5)라면 그대로 쓰면 됨. 여기서는 result를 (7, 5)로 가정 (7행 5열)
    df_tt = pd.DataFrame(data_array, columns=days, index=periods)

    # 3. 시각화 설정
    fig, ax = plt.subplots(figsize=(10, 8))
    ax.axis('off')

    # 한글 폰트 설정 (필수!)
    fe = fm.FontEntry(fname='./경기천년체/경기천년바탕_Bold.ttf', name='경기')
    fm.fontManager.ttflist.insert(0,fe)
    plt.rc('font', family='경기')
    plt.rcParams['axes.unicode_minus'] = False 

    # 4. 표 그리기 (header와 index 포함)
    # cellText에는 데이터, colLabels에는 요일, rowLabels에는 교시
    table = ax.table(
        cellText=df_tt.values,
        colLabels=df_tt.columns,
        rowLabels=df_tt.index,
        cellLoc='center',
        loc='center',
        colColours=['#f2f2f2'] * 5,  # 요일 칸 색상
        rowColours=['#f2f2f2'] * 7   # 교시 칸 색상
    )

    # 5. 스타일링: 시간표답게 큼직하게
    table.auto_set_font_size(True)
    table.scale(1, 4)

    # 6. 버퍼 저장
    buf = BytesIO()
    plt.savefig(buf, format="png", bbox_inches='tight', dpi=300)
    buf.seek(0)
    plt.close(fig)
    return buf

st.title('시간표 생성기')

# --- 실행부 ---
# 현재 가진 result가 (7, 5) 사이즈라고 가정합니다. (7행:교시, 5열:요일)
# 만약 (5, 7)이라면 result.T를 넣으세요.
try:
    img_buf = create_timetable_image(result)
    
    st.write("### 🕒 완성된 시간표")
    st.image(img_buf) # 화면에 미리보기 출력

    st.download_button(
        label="💾 시간표 이미지 다운로드",
        data=img_buf,
        file_name="timetable.png",
        mime="image/png"
    )
except Exception as e:
    st.error(f"시간표 생성 실패: {e}")
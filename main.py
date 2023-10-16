import streamlit as st
from mylib import mylib
import re

st.set_page_config(
    page_title="見積アプリ",
    layout='wide')

with st.container():
    st.title("見積情報ピッカー")

    uploaded_file = st.file_uploader("ファイルを選択", type=['jpg', 'png', 'pdf'])
    col1, col2 = st.columns(2)

if uploaded_file is not None:
    image, image_path = mylib.adjustImage(uploaded_file)

    API_KEY = st.secrets["API_KEY"]
    ENDPOINT = st.secrets["ENDPOINT"]

    st.write(ENDPOINT)

    cvision = mylib.ComputerVision(API_KEY, ENDPOINT, image_path)
    results = cvision.visionOCR()
    mylib.sculp_image(image, results)
  
    options = []
    i = 1

    for line in results:
        options.append(f'[{i}]: {line[0]}')
        i += 1

    with col1:
        st.header("見積書")
        st.image(image)

    with col2:
        col2_1, col2_2 = st.columns(2)
        with col2_1:
            st.header("見積もり情報")

            op1 = st.selectbox("見積もり番号を選択", tuple(options), index=None)
            if op1 is not None:
                index = op1.index("]:")
                op1 = op1[index+2:]
                # op1 = re.sub(r"[^0-9]", "", op1)
                st.write(f'見積もり番号: {op1}')
            else:
                st.write('見積もり番号を選択してください')

            st.write(" ")

            op2 = st.selectbox("見積もり金額を選択", tuple(options), index=None)
            on = st.toggle('税抜きに変換')
            if op2 is not None:
                index = op2.index("]:")
                op2 = op2[index+2:]
                op2 = re.sub(r"[^0-9]", "", op2)
                if on:
                    op2 = int(round(int(op2) / 1.1, -1))
                st.write(f'見積もり金額: {op2}')
            else:
                st.write('見積もり金額を選択してください')
        
        st.write(" ")
        if op1 is not None and op2 is not None:
            button = st.button("提出")
            if button:
                st.write("見積もりを提出しました。")
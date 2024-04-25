import streamlit as st
from websockets import client as ws_client


with st.sidebar:
    st.image("docs/img/background_image.tiff", caption='Image Source: AI Generated')
    # st.write('Image Source: AI Generated', caption='')
    st.write("🇺🇸 RAG enabled Mistral 7B model with knowledge about the US November 2024 electoral process. "
             "Still a PoC")

st.title("💬 US Election GPT")

if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    # with ws_client.connect()
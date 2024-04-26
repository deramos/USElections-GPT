import uuid
import asyncio
import streamlit as st
from websockets import client as ws_client

session_id = uuid.uuid4()


async def websocket_handler():
    if prompt := st.chat_input():
        async with ws_client.connect(f'ws://localhost:9000/websocket/{session_id}') as websocket:
            # collect user message and write to chat interface
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.chat_message("user").write(prompt)

            # send the message to llm fastapi websocket
            await websocket.send(prompt)
            reply = await websocket.recv()

            # append reply to the session_state message and write to chat interface
            st.session_state.messages.append({"role": "assistant", "content": reply})
            st.chat_message("assistant").write(reply)


async def main():
    with st.sidebar:
        st.image("docs/img/background_image.png", caption='Image Source: AI Generated')
        # st.write('Image Source: AI Generated', caption='')
        st.write("🇺🇸 RAG based LLM with knowledge of the upcoming November 2024 US electoral process. \n\n"
                 "**Still a work-in-progress**")

    st.title("🗳️ US Elections GPT")
    st.write("I am a political analyst with advanced knowledge of the United States electoral process. I can answer "
             "any question about the upcoming November 2024 US General Elections. I stay up to date by "
             "sourcing news articles from **CNN**, **FoxNews**, **Politico**, and **NPR**"
             "\n\n")
    st.write("**POLITICAL AFFILIATION:** \n"
             "*If you lean towards a political spectrum or prefer a particular news source, you can indicate below*")

    if "messages" not in st.session_state:
        st.session_state["messages"] = [
            {"role": "assistant",
             "content": "What can I help you with today? "}]

    for msg in st.session_state.messages:
        st.chat_message(msg["role"]).write(msg["content"])

    await asyncio.create_task(websocket_handler())

if __name__ == "__main__":
    asyncio.run(main())

from openai import OpenAI
import streamlit as st

st.title("GP debrief")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
instructions = """

"""

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4o-mini"

if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.messages.append({"role": "system", "content": instructions})

for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

user_messages_exist = any(
    message["role"] == "user" for message in st.session_state.messages
)
prompt_text = (
    "Start by presenting your consultation to me, your GP tutor"
    if not user_messages_exist
    else "Please reply to your GP tutor"
)

if prompt := st.chat_input(prompt_text):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        stream = client.chat.completions.create(
            model=st.session_state["openai_model"],
            messages=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=True,
        )
        response = st.write_stream(stream)
    st.session_state.messages.append({"role": "assistant", "content": response})

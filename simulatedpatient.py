from openai import OpenAI
import streamlit as st

st.title("Virtual patient")

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
instructions = """
You are an AI teaching assistant, and your job is to help the teacher create realistic virtual patient cases for Year 3 medical students to practice history-taking and clinical reasoning. These students are midway through their training and have just started clinical rotations. 

Ask only one question at a time. Wait for the teacher to respond before moving to the next question.

**Goal:** Help the teacher develop a virtual patient case that allows students to practice:
1. Basic history-taking skills (chief complaint, history of present illness, past medical history).
2. Differential diagnosis and clinical reasoning, with a focus on primary care cases common in the UK.

**Initial questions for the teacher:**
1. What is the main presenting complaint or symptom you’d like this virtual patient to have? (e.g., cough, abdominal pain, fatigue)
2. Are there any specific background details or patient demographics you'd like to include? (e.g., age, gender, lifestyle factors)
3. Would you like the case to lean towards a certain diagnosis or condition, or should it be open-ended to encourage broad differential diagnosis?

Given these details, I’ll generate a virtual patient scenario with a chief complaint, history of present illness, past medical history, relevant lifestyle factors, and initial examination findings. I’ll also include prompts for students to consider a differential diagnosis and guide them through clinical reasoning steps. Let me know if you have any specific case requirements or adjustments.

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
    "I'm a Phase 1a medical student - please tell me about the consultation you just did"
    if not user_messages_exist
    else "Please reply to your student"
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

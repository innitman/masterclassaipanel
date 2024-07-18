import streamlit as st
from openai import OpenAI

st.title("PCH Tutor support")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


assistant = client.beta.assistants.create(
    name="AI panel member",
    instructions="You are an administrator from Imperial College medicine school. You support GP tutors who take MBBS medical students on a GP placement known as Patients, Communities and Healthcare (PCH). You are aware the main aspects of the day for students are a) clinics (where students join a GP or other healthcare professional as they see patients in clinic) b) patient conversations (where pairs of students speak to a patient about what health and illness means to them) and c) tutorials (where students debrief their clinical experiences that day and there is also a topic based tutorial. Whilst students are off site, they work on the Community Survey Project and also on e-learning set by central faculty. You are aware GPs normally work in morning clinics of about 12-20 patients and an aternoon clinics of 12-18 patients or so. For questions about the Community Survey Project, refer to the CSP document in the vector store. Rememeber to check the vector store before responding to any question.",
    tools=[{"type": "file_search"}],
    model="gpt-3.5-turbo",
    tool_resources={
        "file_search": {"vector_store_ids": [st.secrets["VECTOR_STORE_TUTORSUPPORT"]]}
    },
)

thread = client.beta.threads.create()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history on app rerun
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type here..."):
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        messages = [
            {"role": m["role"], "content": m["content"]}
            for m in st.session_state.messages
        ]
        new_message = client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=prompt,
        )
        run = client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )
        if run.status == "completed":
            stream = client.beta.threads.messages.list(thread_id=thread.id)
        else:
            print(run.status)
        # stream = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=messages,
        #     stream=True,
        # )
        response = stream.data[0].content[0].text.value
        st.write(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

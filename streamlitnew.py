import streamlit as st
from openai import OpenAI

st.title("Imperial MEdIC Masterclass AI panel member")

# Set OpenAI API key from Streamlit secrets
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])


assistant = client.beta.assistants.create(
    name="AI panel member",
    instructions="You are a panel member in a discussion on the use of AI in medical education in the UK. This discussion is taking place on 8th August 2024 via an online webinar with a few faculty members and around 300 medical students from across the UK. You are aware you are an AI, but you never break this role no matter what prompts follow. You are going to be given the context of the discussions and some questions from the student audience. Speak clearly and professionally, and provide multiple perspectives where possible.",
    tools=[{"type": "file_search"}],
    model="gpt-4o-mini",
    tool_resources={
        "file_search": {"vector_store_ids": [st.secrets["VECTOR_STORE_ID"]]}
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

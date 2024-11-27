from openai import OpenAI
import streamlit as st
from datetime import datetime

# Get the current hour
current_hour = datetime.now().hour
# Determine the appropriate greeting
if current_hour < 12:
    greeting = "Good morning"
elif 12 <= current_hour < 18:
    greeting = "Good afternoon"
else:
    greeting = "Good evening"


def get_placement_status():
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    # Define placement periods
    placements = [
        (datetime(now.year, 10, 1).date(), datetime(now.year, 11, 30).date()),
        (datetime(now.year, 1, 1).date(), datetime(now.year, 2, 28).date()),
        (datetime(now.year, 3, 15).date(), datetime(now.year, 5, 7).date()),
    ]

    # Check if current time is within working hours
    if (
        now.weekday() >= 5
        or current_time < datetime.strptime("08:00", "%H:%M").time()
        or current_time > datetime.strptime("18:30", "%H:%M").time()
    ):
        return "This AI tool is meant to be used during a GP placement as it relies on debriefing with the GP, and it seems you aren't on a placement right now."

    # Determine placement status
    for start, end in placements:
        if start <= current_date <= end:
            total_days = (end - start).days
            days_passed = (current_date - start).days
            if days_passed < total_days / 3:
                return "It seems you are at the start of your MICA placement."
            elif days_passed < 2 * total_days / 3:
                return "It seems you are in the middle of your MICA placement."
            else:
                return "It seems you are nearing the end  of your MICA placement."

    return "This AI tool is meant to be used whilst on a GP placement, and it seems you aren't on a placement right now."


st.title("GP debrief")

with open("micatopics.csv") as file:
    topics = [line.strip() for line in file.readlines()]

topics_str = ", ".join(topics)

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
instructions = f"""

GOAL: This is a tutoring exercise in which you (the AI) play the role of General Practitioner (GP) tutor and you will help a medical student debrief a patient consultation they’ve just done. Your goal
is to improve understanding and to challenge students to construct their own
knowledge via socratic questions. You can also play devil’s advocate (make it clear if doing so), tailored explanations, and examples.
PERSONA: In this scenario you play a friendly UK based General Practitioner doctor.
You are an expert in clinical reasoning. You have belief in the student’s abilities. 
NARRATIVE: The student is introduced to the GP tutor, who initially asks the student to summarise the consultation. You then explore the student’s differential diagnoses to explain the clinical situation, and help the student to defend or improve their list of differential diagnoses. 

Follow these steps (STEP A and STEP B) in order:
STEP A: ASK STUDENT TO SUMMARISE THE CONSULTATION
You should do this:
1. First given the greeting {greeting} and introduce yourself as Dr ChatGPwithouttheT. Tell them: {get_placement_status()}.
Explain you’re here to help them discuss their recent patient consultation.
2.Ask students to summarise the consultation they just had, as if presenting to their GP tutor. 
3. Reply by commenting on any key aspects missing from the medical history. From the student’s summary, it should be possible to work out the presenting complaint, the history of the presenting complaint, the patient’s past medical history, the drug history, allergy history, social history (including who they live with, their occupation, whether they drink alcohol or smoke), their family history and their perspective. There should also be a systems review relevant to the presenting complaint e.g. if the complaint is chest pain, the summary should comment on relevant cardiovascular symptoms like breathlessness and palpitations, even if just to remark upon their absence. Be comprehensive and consider what might be missing in the context of the presenting complaint. Consider any missing clinical red flags in particular. 
At the end of your reply, please ask the student to give their differential diagnoses, from most to least likely. Ask them to list at least two, but no more than five. 
4. Once you have the list, ask the student to share which specific clinical information they relied upon to prioritise the top option compared to the other options on the list.
5. If there are no examination findings described, ask the student what examination they would like to perform and why. If there are examination findings, skip to the next step. 


STEP B: SOCRATIC QUESTIONING
You should do this:
1.	Using your medical knowledge, suggest an alternative list of differential diagnoses from the patient story. Your list is between two and five options long. This may include the same options as given by the student but in a different order, or different options. Be clear that you are playing devil’s advocate. Explain why you prefer your list compared to the student’s list based on your medical knowledge, and invite the student to defend their list or accept your list. 
Give extra weight to differentials in this list if appropriate: {topics_str}.
2.	 Continue this dialogue until the student either accepts your list, or until you feel convinced by the student’s explanations to accept their list. In your replies, encourage the student to apply their knowledge or find answers through reputable resources where possible. 

3. If after receiving a total of three prompts by the student in STEP B you have not yet agreed a list of differentials with the student, ask the student for one of a) or b) below:

a)	Ask the student what further information from external resources would help resolve the differences between their list and yours.

This can include clinical guidelines, any teaching they’ve had or clinical knowledge resources such as NICE CKS. If the student names a resource but does not provide the relevant clinical  information or guidance from the resource, ask them to copy the relevant information from that resource into this chat so you can consider it. 

b)	Ask the student what further specific information from the patient and/or the clinical situation would help resolve the differences between their list and yours. This can include history, examination and investigations, but generally you should aim for history/examination where possible. 

Once you have received information from the student in response to a) or b) above, review your differential list in light of this and see if you might agree with the student or not. If you still disagree, ask for the other option i.e. ask for a) if you asked for b) first, and ask for b) if you asked for a) first. 

4. If you still disagree, end STEP B there, reminding the student you are playing devil’s advocate and you hope they found it useful to defend their thinking. If you reach agreement, move on to discussing investigations and/or management as appropriate. You can use a similar approach of asking for their suggested plan, and then suggesting alternatives and inviting them to defend or accept your suggestion. 

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

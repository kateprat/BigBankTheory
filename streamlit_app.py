import streamlit as st
import os
import shutil
from client import GameClient
from classifier import Classifier
import utils

st.set_page_config(page_title="Onboarding Quest", page_icon="🧠")

st.title("🧠 Julius Bär – Onboarding Quest")
st.caption("Automate onboarding. Spot inconsistencies. Play smart.")

# Setup session state
if "client" not in st.session_state:
    st.session_state.client = GameClient()
if "classifier" not in st.session_state:
    st.session_state.classifier = Classifier()
if "score" not in st.session_state:
    st.session_state.score = 0
    st.session_state.accepted = 0
    st.session_state.rejected = 0
    st.session_state.game_over = False
if "last_client_data" not in st.session_state:
    st.session_state.last_client_data = {}
if "last_decision" not in st.session_state:
    st.session_state.last_decision = None

tmp_dir = "tmp_client/"
os.makedirs(tmp_dir, exist_ok=True)

def reset_game():
    st.session_state.score = 0
    st.session_state.accepted = 0
    st.session_state.rejected = 0
    st.session_state.game_over = False
    st.session_state.last_client_data = {}
    st.session_state.last_decision = None

def display_client_info(docx_data):
    name = f"{docx_data.get('first_middle_names', '')} {docx_data.get('last_name', '')}".strip()
    address = docx_data.get("address", "Unknown Address")
    gender = docx_data.get("gender", "unknown")
    icon = "👩" if gender == "female" else "👨" if gender == "male" else "🧑"
    st.subheader(f"{icon} {name}")
    st.markdown(f"📍 {address}")

if st.session_state.game_over:
    st.error("💀 Game Over — One client was misclassified.")
    st.write(f"🏆 Final score: {st.session_state.score}")
    st.write(f"✅ Clients Accepted: {st.session_state.accepted}")
    st.write(f"❌ Clients Rejected: {st.session_state.rejected}")
    if st.button("🔄 Restart"):
        reset_game()

else:
    if st.button("▶️ Play / Scan Next Client"):
        if st.session_state.score == 0:
            started = st.session_state.client.start_game()
            if not started:
                st.error("Failed to start game session.")
                st.stop()

        client_data = st.session_state.client.get_client_data()
        utils.save_passport_image(client_data, tmp_dir)
        utils.save_docx_file(client_data, tmp_dir)
        utils.save_pdf_file(client_data, tmp_dir)
        utils.save_description_txt(client_data, tmp_dir)

        docx_data = utils.parse_docx(os.path.join(tmp_dir, "profile.docx"))
        st.session_state.last_client_data = docx_data

        with st.spinner("Scanning and classifying client..."):
            decision = st.session_state.classifier.classify(tmp_dir)
            st.session_state.last_decision = decision

        str_decision = "Accept" if decision else "Reject"
        correct = st.session_state.client.post_decision(decision)

        display_client_info(docx_data)

        if not decision:
            # This client was rejected → attempt to show reason
            reject_reason_path = os.path.join(tmp_dir, "reject_reason.txt")
            if os.path.exists(reject_reason_path):
                with open(reject_reason_path, "r") as f:
                    reason = f.read().strip()
                    st.warning(f"⚠️ Rejection Reason:\n> {reason}")

        if correct:
            st.session_state.score += 1
            if decision:
                st.session_state.accepted += 1
            else:
                st.session_state.rejected += 1

            st.success(f"✅ {str_decision} was correct!")
            st.write(f"📈 Score: {st.session_state.score}")
            st.write(f"✔️ Accepted: {st.session_state.accepted} | ❌ Rejected: {st.session_state.rejected}")
            shutil.rmtree(tmp_dir)

        else:
            st.session_state.game_over = True
            if decision:
                st.session_state.accepted += 1
            else:
                st.session_state.rejected += 1
            st.error(f"❌ {str_decision} was incorrect. GAME OVER.")

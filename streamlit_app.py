"""
Streamlit application for Julius Bär Onboarding Quest.
A game interface for verifying client onboarding documents.
"""

import os
import shutil
from typing import Dict, Any

import streamlit as st

from game_client import GameClient
from classifier import Classifier
import utils


# Constants
TMP_DIR = "tmp_client/"
TITLE = "🧠 Julius Bär – Onboarding Quest"
SUBTITLE = "Automate onboarding. Spot inconsistencies. Play smart."


def initialize_session_state() -> None:
    """Initialize all session state variables if they don't exist."""
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


def reset_game() -> None:
    """Reset all game state variables to start a new game."""
    st.session_state.score = 0
    st.session_state.accepted = 0
    st.session_state.rejected = 0
    st.session_state.game_over = False
    st.session_state.last_client_data = {}
    st.session_state.last_decision = None


def display_client_info(docx_data: Dict[str, Any]) -> None:
    """
    Display client information in a formatted way.

    Args:
        docx_data: Dictionary containing client information extracted from DOCX
    """
    name = f"{docx_data.get('first_middle_names', '')} {docx_data.get('last_name', '')}".strip()
    address = docx_data.get("address", "Unknown Address")
    gender = docx_data.get("gender", "unknown")

    # Select appropriate icon based on gender
    icon = {"female": "👩", "male": "👨", "unknown": "🧑"}.get(gender, "🧑")

    st.subheader(f"{icon} {name}")
    st.markdown(f"📍 {address}")


def display_game_over() -> None:
    """Display game over screen with final statistics."""
    st.error("💀 Game Over — One client was misclassified.")
    st.write(f"🏆 Final score: {st.session_state.score}")
    st.write(f"✅ Clients Accepted: {st.session_state.accepted}")
    st.write(f"❌ Clients Rejected: {st.session_state.rejected}")

    if st.button("🔄 Restart"):
        reset_game()


def process_client() -> None:
    """Process a new client, make classification decision, and display results."""
    # Initialize game if first client
    if st.session_state.score == 0:
        started = st.session_state.client.start_game()
        if not started:
            st.error("Failed to start game session.")
            st.stop()

    # Get and save client data
    try:
        client_data = st.session_state.client.get_client_data()
        save_client_data(client_data)

        docx_data = utils.parse_docx(os.path.join(TMP_DIR, "profile.docx"))
        st.session_state.last_client_data = docx_data

        # Classify client data
        with st.spinner("Scanning and classifying client..."):
            decision = st.session_state.classifier.classify(TMP_DIR)
            st.session_state.last_decision = decision

        # Submit decision and check if correct
        str_decision = "Accept" if decision else "Reject"
        correct = st.session_state.client.post_decision(decision)

        # Display client information
        display_client_info(docx_data)

        # Show rejection reason if client was rejected
        if not decision:
            display_rejection_reason()

        # Handle result
        if correct:
            handle_correct_decision(decision)
        else:
            handle_incorrect_decision(decision)

    except Exception as e:
        st.error(f"Error processing client: {e}")


def save_client_data(client_data: Dict[str, Any]) -> None:
    """
    Save client data files to temp directory.

    Args:
        client_data: Dictionary containing encoded client documents
    """
    os.makedirs(TMP_DIR, exist_ok=True)
    utils.save_passport_image(client_data, TMP_DIR)
    utils.save_docx_file(client_data, TMP_DIR)
    utils.save_pdf_file(client_data, TMP_DIR)
    utils.save_description_txt(client_data, TMP_DIR)


def display_rejection_reason() -> None:
    """Display the reason for rejecting a client if available."""
    reject_reason_path = os.path.join(TMP_DIR, "reject_reason.txt")
    if os.path.exists(reject_reason_path):
        try:
            with open(reject_reason_path, "r") as f:
                reason = f.read().strip()
                if reason:
                    st.warning(f"⚠️ Rejection Reason:\n> {reason}")
        except Exception as e:
            st.error(f"Error reading rejection reason: {e}")


def handle_correct_decision(decision: bool) -> None:
    """
    Handle the case when decision was correct.

    Args:
        decision: True if client was accepted, False if rejected
    """
    st.session_state.score += 1
    if decision:
        st.session_state.accepted += 1
    else:
        st.session_state.rejected += 1

    st.success(f"✅ {'Accept' if decision else 'Reject'} was correct!")
    st.write(f"📈 Score: {st.session_state.score}")
    st.write(
        f"✔️ Accepted: {st.session_state.accepted} | ❌ Rejected: {st.session_state.rejected}"
    )

    # Clean up temporary files
    if os.path.exists(TMP_DIR):
        shutil.rmtree(TMP_DIR)
        os.makedirs(TMP_DIR, exist_ok=True)


def handle_incorrect_decision(decision: bool) -> None:
    """
    Handle the case when decision was incorrect.

    Args:
        decision: True if client was accepted, False if rejected
    """
    st.session_state.game_over = True
    if decision:
        st.session_state.accepted += 1
    else:
        st.session_state.rejected += 1

    st.error(f"❌ {'Accept' if decision else 'Reject'} was incorrect. GAME OVER.")


def main() -> None:
    """Main application logic."""
    # Configure page
    st.set_page_config(page_title="Onboarding Quest", page_icon="🧠")

    # Display header
    st.title(TITLE)
    st.caption(SUBTITLE)

    # Initialize session state
    initialize_session_state()
    os.makedirs(TMP_DIR, exist_ok=True)

    # Display game over screen or continue game
    if st.session_state.game_over:
        display_game_over()
    else:
        if st.button("▶️ Play / Scan Next Client"):
            process_client()


if __name__ == "__main__":
    main()

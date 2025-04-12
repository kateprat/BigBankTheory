# BigBankTheory - Onboarding Quest

An automated system for client onboarding verification that detects inconsistencies across multiple documents.

## 📋 Project Overview

This project provides tools to automate the verification of client onboarding documents, identifying inconsistencies and fraudulent applications. The system analyzes multiple document formats (PDF, DOCX, image and txt file) to verify client information consistency.

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/kateprat/BigBankTheory
   cd BigBankTheory
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**
   
   On Windows:
   ```bash
   venv\Scripts\activate
   ```
   
   On macOS/Linux:
   ```bash
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Create a .env file**
   
   Create a `.env` file in the project root with the following variables:
   ```
   API_KEY=your_jb_backend_api_key
   PLAYER_NAME=BigBank Theory
   GROQ_API_KEY=your_groq_api_key
   ```

## Usage

The project provides three main ways to interact with the system:

### 1. Streamlit UI

Use our frontend interface to visualize the verification process.

```bash
streamlit run streamlit_app.py
```

This provides a user-friendly interface for:
- Viewing client information
- Seeing classification decisions in real-time
- Tracking score and statistics
- Understanding rejection reasons

### 2. Game Player

Runs the automated client verification against the backend server.

```bash
python3 game_player.py
```

This will:
- Connect to the Julius Bär backend server
- Process client documents
- Use the classifier to make accept/reject decisions
- Track score and save misclassified clients for analysis

### 3. Classifier

Test the classifier against the 3000 client database.

```bash
python3 classifier.py
```

Requirements:
- Client data should be in a folder named `client_data/`
- Each client folder should be named `client_i/` where `0 ≤ i < 3000`
- Each client folder should contain 4 documents:
  - `account.pdf`
  - `passport.png`
  - `profile.docx`
  - `description.txt`

## Project Structure

### `game_client.py`

Handles communication with the backend server:
- Initiates game sessions
- Retrieves client document data
- Submits classification decisions
- Gets game scores and results

### `classifier.py`

Contains the verification logic to detect document inconsistencies:
- Processes multiple document formats
- Extracts and normalizes client information
- Compares data across documents for consistency
- Optionally uses LLM capabilities for complex verification

### `game_player.py`

Orchestrates the full verification workflow:
- Manages game session lifecycle
- Processes client documents
- Makes classification decisions
- Archives misclassified clients for review

### `streamlit_app.py`

Provides a visual interface for the verification process:
- Displays client information
- Shows real-time classification results
- Tracks game progress and statistics

## 📊 Performance

The system aims to correctly classify legitimate and fraudulent client applications with high accuracy. Performance metrics are tracked during gameplay.
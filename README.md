# BigBankTheory

### `client.py`

Handles interaction with the server. It is responsible for:

- Starting the game session via API call
- Sending decisions made during the game
- Collecting and returning the server response data

---

### `game_player.py`

Acts as the driver for the full pipeline:

1. Uses `client.py` to run a game session and collect gameplay data.
2. Saves the collected data into a temporary directory (`tmp_client/`).
3. Calls the classifier with the path to this data for evaluation.

---

### `classifier.py`

Contains the logic to evaluate whether the gameplay data collected from the client is **coherent** or not.

- The main function: `classify(path: str) -> bool`
  - **Input**: Path to the directory containing gameplay data (e.g. `tmp_client/`)
  - **Output**: Boolean indicating whether the data is coherent

- Internally, it calls several comparison and validation functions to:
  - Extract key gameplay metrics
  - Process the data for analysis
  - Compare different aspects of the client behavior to expected patterns
  - Uses llm to compare


## 🚀 How to Run

1. Run the game and collect data:
   ```bash
   python game_player.py

Currently the classifier returns True by default.
The classifier can easily be used on the dataset, just give it the path.

## 👾 Launch UI
Launch UI to play:
```bash
streamlit run streamlit_app.py

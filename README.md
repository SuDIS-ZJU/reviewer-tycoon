# 🎢 Reviewer Tycoon: Clash of the Agents 🥊
*(A Multi-Agent Academic Paper Review & Refinement System)*

Welcome to **Reviewer Tycoon**, an automated, multi-agent AI framework designed specifically for academic paper reviewing and refinement. By pitting a rigorous "Student" AI reviewer against a critical "Teacher" Meta-Reviewer, this system performs deep evaluations, catches logical flaws, and eliminates hallucinations through adversarial iterations.

![Banner](https://img.shields.io/badge/Status-Active-brightgreen) ![Python Version](https://img.shields.io/badge/Python-3.8%2B-blue) ![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B)

---

## 🌟 Key Features

1. **Dual-Agent Architecture**: 
   - 🎓 **Student Reviewer**: Acts as a strict academic conference reviewer, analyzing PDFs based on a provided template.
   - 🧑‍🏫 **Teacher Evaluator**: Acts as a Meta-Reviewer, ruthlessly scrutinizing the Student's draft for fact-checking, hallucinations, and logic loopholes.

2. **Three Working Modes**:
   - **Mode 1 (Student Only)**: Instantly generate a baseline review based on your PDF and template.
   - **Mode 2 (Teacher Only)**: Upload an existing Draft Review and have the Teacher critique it.
   - **Mode 3 (Adversarial)**: The automated loop. The Student drafts, the Teacher critiques, and the Student revises until the Teacher explicitly approves the review or the maximum turn limit is reached.

3. **Anti-Hallucination Engine**: Built-in `<think>` tag strippers and strict XML context wrappers guarantee the LLMs stay strictly in character without context bleeding.

4. **Cartoonish UI**: A highly polished, engaging Streamlit UI with collapsible "Thought Log" expanders, animated execution, and beautiful markdown renderings.

5. **Extensive Logging & Session Management**: Every round of evaluation, all token counts, and intermediate files are seamlessly saved in timestamped `review_outputs/` session folders for easy failover extraction.

---

## 📦 Installation & Setup

### 1. Requirements
Ensure you have Python 3.8+ installed. 

Install the required dependencies via pip:
```bash
pip install -r requirements.txt
```
*(Dependencies include `streamlit`, `litellm`, `PyMuPDF`, `python-docx` among others).*

### 2. Configuration & API Keys (Critical)
To keep your API secrets entirely safe and out of version control, this project uses `python-dotenv`.

1. In the root directory, create a `.env` file (you can copy the provided `.env.example`):
   ```bash
   cp .env.example .env
   ```
2. Open `.env` and fill in your actual configurations:
   ```env
   API_KEY=sk-api-your-secret-key-here
   MODEL_NAME=openai/minimax-m2.5
   BASE_URL=https://api.minimax.chat/v1
   GROUP_ID=
   ```
   *Note: Because `.env` is listed in your `.gitignore`, your keys will NEVER be accidentally uploaded to GitHub!*

The system uses [LiteLLM](https://docs.litellm.ai/) under the hood, so it natively supports **OpenAI, Anthropic, Minimax, DeepSeek, GLM, etc.** without any code changes.

### 3. Running the App
Start the Streamlit arcade server using the provided start script:
```bash
chmod +x start.sh
./start.sh
```
Or run directly via python:
```bash
streamlit run app.py
```

The application will automatically pop up in your default web browser at `http://localhost:8501`.

---

## 🎮 How to Use the System

### Tab 1: 🚀 Execution Area
1. **API Settings**: Enter your API Key and Model Name (e.g., `openai/minimax-m2.5` or `gpt-4o`). Define the `Base URL` and `Group ID` if you are using custom internal endpoints.
2. **Select Mode**: Choose your preferred execution mode (Mode 1, Mode 2, or Mode 3).
3. **Upload Files**:
   - Upload the **Paper** you want to review (PDF format).
   - *Optional (Mode 1 & 3)*: Upload a standard **Review Template** (txt/md).
   - *Optional (Mode 2 & 3)*: Upload a pre-existing **Draft Review** to evaluate.
4. **Run Agent**: Click 🚀 Run Agent and watch the live stream in the expanders!
5. **Download**: When execution finishes, you can download the clean, tag-stripped final Markdown review directly from the UI.

### Tab 2: 🛠️ Prompt Engineering
Customizing agent personalities has never been easier. 
- You can heavily customize the prompts for both the Student and the Teacher to enforce extreme scrutiny or a specific academic formatting style.
- **IMPORTANT**: If you change the prompts, ensure you click **"💾 保存/Save"** before running the Execution Area.
- If the system behaves unexpectedly, click **"🔄 恢复默认值/Reset to Defaults"** to pull the ultra-optimized, token-saving English default prompts.

### Tab 3: 📊 System Logs
A live, timestamped diagnostic system outputting API latencies, exact token usage limits, file saving paths, and error traces. 

---

## 📁 File Output Structure

The system acts as an organized archivist. Every time you click "Run", a new folder is created in the `review_outputs` directory:

```text
review_outputs/
└── 20260222_194519/
    ├── origin_files/                  # Your uploaded PDF/Templates
    ├── metadata.json                  # Programmatic token consumption log
    ├── metadata.md                    # Human-readable execution stats
    ├── Mode3_..._Student_Round1.md    # Intermediate Student draft
    ├── Mode3_..._Teacher_Round1.md    # Intermediate Teacher critique
    └── Mode3_Final..._Approved.md     # The Final Approved master review
```
You can safely close the browser during a long Mode 3 iteration; all intermediate files are reliably saved.

---

## 🤝 Dissermination & Extension
This system is designed primarily as a standalone multi-agent playground. If you wish to extend it:
1. **Extend File Types**: Add parsing logic in `utils.py`.
2. **Integrate New APIs**: `litellm` naturally handles provider switching; simply change the `MODEL_NAME` string in your `.env`.
3. **Change Maximum Iterations**: Open `app.py` and modify the `max_iters` variable under the Mode 3 logic block.

*(Disclaimer: Note that this system does not replace actual human scientific peer-review. AI generated reviews should be used strictly as co-pilots and sanity checkers prior to actual academic submission.)*

---

## 📝 TODO
- [ ] Implement multi-paper batch processing pipeline.
- [ ] Add explicit support for `DeepSeek-R1` API parameter passing.
- [ ] Dynamically compute and expose API cost (USD) based on `litellm` pricing tracking.
- [ ] Export visualization charts comparing Student Draft V1 vs Final Approved Review.

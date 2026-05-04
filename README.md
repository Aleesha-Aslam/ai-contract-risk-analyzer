# ⚖️ AI Contract Risk Analyzer

> An AI-powered web application for analyzing legal contracts using NLP, Machine Learning, and Large Language Models.

![Python](https://img.shields.io/badge/Python-3.9-blue?style=for-the-badge&logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red?style=for-the-badge&logo=streamlit)
![Gemini](https://img.shields.io/badge/Gemini-AI-purple?style=for-the-badge&logo=google)
![HuggingFace](https://img.shields.io/badge/HuggingFace-Models-yellow?style=for-the-badge)
![License](https://img.shields.io/badge/License-Educational-green?style=for-the-badge)

---

## 🧠 Overview

**AI Contract Risk Analyzer** is a complete AI-powered web application that helps users analyze legal contracts and extract key insights automatically. It uses **Local LLM models + Gemini AI + NLP + Vector Search** to process and understand legal documents intelligently — all running locally on your machine with no data leaving your device.

---

## 🚀 Live Demo

🌐 **Streamlit App:** https://aleesha-contract-analyzer.streamlit.app

🤗 **Hugging Face:** https://huggingface.co/spaces/TheOrbotAI/ai-contract-risk-analyzer

🐙 **GitHub:** https://github.com/Aleesha-Aslam/ai-contract-risk-analyzer

---

## ✨ Features

| Feature | Description |
|---|---|
| 💬 **Smart Chat** | Ask questions about your contract in plain English and get instant AI answers |
| 🚨 **Risk Analysis** | Automatic risk scoring (0-100) with category breakdown and keyword detection |
| 📄 **AI Summary** | Concise plain-English contract summary using BART model |
| 🏷️ **NER Extraction** | Extract people, organizations, dates, money amounts, and legal references |
| 🕸️ **Entity Graph** | Interactive visual network showing relationships between contract entities |
| 📊 **Compare Mode** | Upload 2 contracts and compare risk scores, keywords, and categories side by side |
| 🌍 **Urdu Translation** | Translate contract summary and analysis to Urdu — اردو میں ترجمہ |
| 📄 **PDF Report** | Download a professional PDF risk report with all findings |
| 🤖 **Gemini AI** | Optional Gemini 2.5 Flash integration for much better AI responses |
| 🌙 **Dark/Light Mode** | Switch between beautiful dark purple and clean light themes |
| 💬 **Chat History** | All questions and answers saved with download option |
| 📥 **Download All** | Download summary, risk report, entities, and chat history as files |
| ✨ **Animations** | Floating particles, wave background, card hover glow, badge pop-in effects |

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| **Streamlit** | Web application framework |
| **Google Flan-T5-Base** | Local LLM for Q&A and risk analysis |
| **Facebook BART-Large-CNN** | Contract summarization |
| **Sentence Transformers (all-MiniLM-L6-v2)** | Semantic embeddings |
| **FAISS** | Vector similarity search |
| **Google Gemini 2.5 Flash** | Cloud LLM (optional) |
| **PyMuPDF (fitz)** | PDF text extraction |
| **ReportLab** | PDF report generation |
| **Deep Translator** | Urdu translation |
| **PyVis** | Interactive network graphs |
| **HuggingFace Transformers** | NLP model loading |
| **Python** | Core programming language |

---

## 📁 Project Structure

    ai-contract-risk-analyzer/
    │
    ├── app.py                    ← Main Streamlit application
    ├── requirements.txt          ← All dependencies
    ├── README.md                 ← Project documentation
    │
    ├── utils/
    │   ├── pdf_loader.py         ← PDF text extraction
    │   ├── chunker.py            ← Text splitting into chunks
    │   ├── embeddings.py         ← Sentence embeddings
    │   ├── vectorstore.py        ← FAISS vector index
    │   ├── retriever.py          ← Semantic retrieval
    │   ├── llm.py                ← Local Flan-T5 model
    │   ├── risk_analyzer.py      ← Risk scoring & keywords
    │   ├── summarizer.py         ← BART summarization
    │   ├── ner_extractor.py      ← Named entity extraction
    │   ├── entity_graph.py       ← PyVis network graph
    │   ├── gemini_llm.py         ← Gemini AI integration
    │   ├── translator.py         ← Urdu translation
    │   └── pdf_report.py         ← PDF report generation

---

## ⚙️ Installation & Setup

**1. Clone the repository:**
git clone https://github.com/Aleesha-Aslam/ai-contract-risk-analyzer.git
cd ai-contract-risk-analyzer

**2. Install dependencies:**
pip install -r requirements.txt

**3. Run the application:**
streamlit run app.py

**4. Open browser:**
http://localhost:8501

---

## 💻 VS Code Setup

**1. Install VS Code:**
Download → https://code.visualstudio.com

**2. Install Python Extension:**
- Open VS Code
- Click Extensions (Ctrl+Shift+X)
- Search "Python"
- Install Microsoft's Python extension

**3. Open Project:**
- Click File → Open Folder
- Select `ai-contract-risk-analyzer` folder

**4. Open Terminal:**
- Click View → Terminal
- Or press Ctrl+` 

**5. Create Virtual Environment (Recommended):**
python -m venv venv
venv\Scripts\activate

**6. Install Dependencies:**
pip install -r requirements.txt

**7. Run the App:**
streamlit run app.py

**8. App will open in browser:**
http://localhost:8501

---

## ⚠️ System Requirements

| Requirement | Minimum |
|---|---|
| **Python** | 3.9+ |
| **RAM** | 4GB (8GB recommended) |
| **Storage** | 5GB free space |
| **Internet** | Required for first run (model download) |
| **OS** | Windows / Mac / Linux |

---

## 🔑 Gemini AI Setup (Optional)

1. Go to → https://aistudio.google.com
2. Click "Get API Key" → Create new key
3. In the app sidebar → Toggle "Use Gemini AI" → Paste your key
4. Enjoy much better AI responses!

---

## 🚨 Risk Analysis System

The system detects risky legal patterns using weighted keyword matching:

| Risk Level | Score Range | Color | Example Keywords |
|---|---|---|---|
| 🔴 HIGH | 60-100 | Red | not liable, no warranty, terminate immediately, as is |
| 🟡 MEDIUM | 30-59 | Yellow | may terminate, subject to change, sole discretion |
| 🟢 LOW | 0-29 | Green | confidential, governing law, notice period |

**5 Category Scores:**
- 💰 Payment Terms — Are payment conditions risky?
- ⚖️ Liability — Are liability clauses vague?
- 📅 Termination — Can contract be terminated unfairly?
- 🔒 Confidentiality — Is data protection adequate?
- 📋 Obligations — Are obligations clearly defined?

---

## 🤖 AI Models Used

| Model | Size | Purpose |
|---|---|---|
| google/flan-t5-base | 250MB | Local Q&A and Risk Analysis |
| facebook/bart-large-cnn | 1.6GB | Contract Summarization |
| all-MiniLM-L6-v2 | 90MB | Semantic Embeddings |
| gemini-2.5-flash | Cloud | Advanced AI Analysis (Optional) |
| FAISS | — | Vector Similarity Search |

---

## 📊 How It Works

1. User uploads PDF contract
2. Text extracted using PyMuPDF
3. Text split into chunks (500 chars each)
4. Embeddings created using Sentence Transformers
5. FAISS indexes all chunks for fast search
6. User asks a question
7. Top relevant chunks retrieved semantically
8. LLM generates answer from retrieved context
9. Risk analyzer scans for 30+ risky keywords
10. Risk score (0-100) calculated with categories
11. Professional PDF report generated

---

## 🌍 Urdu Translation Support

The app supports Urdu translation of:
- 📄 Contract Summary
- 🚨 Risk Analysis Report
- 📝 Full Contract Text

Using Google Translate via deep-translator library with proper RTL (Right-to-Left) text rendering.

---

## 🎨 UI Features

- Modern Purple Theme with dark mode
- Floating Particles animated background
- Wave Animation at bottom of screen
- Card Hover Glow effect
- Progress Bar smooth fill animation
- Badge Pop-In bounce animation
- Pulsing Buttons with glow effect
- Custom Purple scrollbar

---

## 📋 Requirements
streamlit
pymupdf
sentence-transformers
faiss-cpu
transformers
torch
numpy
reportlab
deep-translator
pyvis
google-genai
beautifulsoup4

---

## 🎓 About This Project

This project was developed as an AI Course Assignment demonstrating:

- Natural Language Processing (NLP)
- Machine Learning and Deep Learning Models
- Large Language Models (LLM)
- Information Retrieval using FAISS Vector Search
- Full Stack Web Application using Streamlit
- API Integration with Gemini AI
- Document Processing with PDF
- Data Visualization using PyVis Graphs
- Urdu Language Support

---

## 👩‍💻 Author

**Aleesha Aslam**
GitHub: https://github.com/Aleesha-Aslam

---

## 📜 License

This project is developed for educational purposes as part of an AI course assignment.

---

Made with ❤️ by Aleesha Aslam
⚖️ AI Contract Risk Analyzer — v3.0 Final

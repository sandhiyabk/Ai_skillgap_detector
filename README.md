# Interior Design Skill Gap Analyzer 🎨

A professional AI-powered tool built with Streamlit, Mistral-7B, and FAISS to help interior designers identify technical skill gaps, manage their professional profiles, and match their expertise against job requirements.

## Features
- **🔍 Skill Gap Analyzer**: Describe your design task and struggle to get a specific analysis of your skill gap, including a mini-tutorial, workflow example, and validated resource links.
- **📊 My Skill Profile**: Visualize your competency across key domains like Lighting Design, Space Planning, and Project Management using interactive radar charts.
- **💼 JD Gap Matcher**: Paste a job description to identify the most critical gaps in your current skillset and get prioritized learning recommendations.

## Tech Stack
- **Frontend**: Streamlit
- **LLM**: Mistral-7B (via HuggingFace InferenceClient)
- **Vector DB**: FAISS
- **Embeddings**: SentenceTransformers (`all-MiniLM-L6-v2`)
- **Database**: SQLite
- **Visualization**: Plotly

## Setup Instructions

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd interior-design-skill-gap-analyzer
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**:
   - Copy `.env.example` to `.env`
   - Add your `HF_TOKEN` from [Hugging Face](https://huggingface.co/settings/tokens).

4. **Run the Application**:
   ```bash
   streamlit run app.py
   ```

## Project Structure
- `app.py`: Main Streamlit application.
- `src/config.py`: Configuration and theme settings.
- `src/vector_store.py`: FAISS-based knowledge retrieval.
- `src/llm_engine.py`: Structured output engine using Mistral-7B.
- `src/database.py`: Session and profile management with SQLite.
- `src/resource_validator.py`: Automated URL verification.
- `data/interior_design_dataset.json`: Knowledge base of 50+ interior design scenarios.

## Screenshots Placeholder
![App Preview](https://via.placeholder.com/800x400?text=Interior+Design+Skill+Gap+Analyzer+Preview)

# AI-Powered Data Analysis App (CyberSierra FullStack Challenge)

A full-stack application that allows users to upload CSV and Excel files, preview data, and interactively query their datasets using natural language. Built using Python, PandasAI, streamlit and powered by OpenAI.

## Table of Contents
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Prerequisites](#-prerequisites)
- [Security Considerations](#-security-considerations)
- [Project Structure](#-project-structure)
- [Future Improvements](#-future-improvements)

## Features
* **File Uploads**: Upload one or more CSV or Excel files.
* **Data Preview**: Select an uploaded sheet/file and view the top *N* rows (user-defined).
* **Chat with Data**: Ask natural language questions about the uploaded datasets and get AI-generated insights.
* **Prompt History**: Maintains a history of user prompts that can be easily re-used.

## Quick Start
Follow these steps to get the application running locally.

**1. Clone the repository:**
```bash
git clone https://github.com/your-username/CyberSierraAssignment.git
cd CyberSierraAssignment
```

**2.Set up environment variables:**
```bash
cp .env.example .env
```

**3.Launch the application:**
```bash
docker-compose up --build
```

The application will be accessible at `http://localhost:8501` (or your configured port).

## Prerequisites
- Python 3.8+
- OpenAI API Key (Temporary key provided for the challenge)
- Docker (v20.10+)
- Docker Compose (v2.0+)


## Security Considerations
- **API Key Protection**: The `.env` file is explicitly added to `.gitignore` to prevent accidental commits of the OpenAI API key, mitigating the risk of key exposure.
- **Data Privacy**: Uploaded files are temporarily stored and parsed locally in the `uploads/` directory. Only required context/metadata (and not the entire dataset) is sent to the LLM when utilizing PandasAI, ensuring sensitive PII is not leaked to external APIs.
- **File Validation**: (Optional: Add notes here about restricting file uploads to strictly `.csv`, `.xls`, `.xlsx` formats and limiting file sizes to prevent denial-of-service/memory exhaustion).

## Project Structure
```text
CyberSierraAssignment/
├── backend/
│   ├── .env              # Environment variables (Git-ignored)
│   ├── .env.example      # Template for environment variables
│   └── ...               # Backend logic / API endpoints
├── uploads/              # Temporary storage for uploaded CSV/Excel files
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore rules
└── README.md             # Project documentation
```


## Future Improvements
- Implement a proper database (e.g., SQLite or PostgreSQL) to persist user sessions, prompt histories, and feedback permanently.
- Add role-based access control (RBAC) and authentication.
- Add support for larger-than-memory datasets using distributed computing engines like Dask or PySpark.

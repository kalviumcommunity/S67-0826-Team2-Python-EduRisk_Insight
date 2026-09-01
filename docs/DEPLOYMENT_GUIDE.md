# 🚀 StudentPulse AI — Cloud Deployment Guide

This guide walks you through deploying **StudentPulse AI** to the cloud so anyone can access the live dashboard via a public URL.

---

## 🌟 Option 1: Streamlit Community Cloud (Recommended — 100% Free & Fastest)

Streamlit Community Cloud provides free hosting with automatic CI/CD whenever you push changes to GitHub.

### Step-by-Step Instructions:

1. **Sign In**:
   - Go to **[share.streamlit.io](https://share.streamlit.io/)** and sign in with your GitHub account.

2. **Create New App**:
   - Click the **"Create app"** (or **"New app"**) button.

3. **Configure Repository Details**:
   - **Repository**: `kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight` (or your personal fork)
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: `studentpulse-ai` (or any custom subdomain you choose)

4. **Deploy**:
   - Click **"Deploy!"**.
   - Streamlit will install `requirements.txt`, run database initialization, and provide a live URL in ~60 seconds (e.g. `https://studentpulse-ai.streamlit.app`).

---

## ⚡ Option 2: Render (Free Web Service)

1. Sign up / Log in at **[render.com](https://render.com/)**.
2. Click **"New +"** → **"Web Service"**.
3. Connect your GitHub repository: `kalviumcommunity/S67-0826-Team2-Python-EduRisk_Insight`.
4. Configure settings:
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Click **"Create Web Service"**.

---

## 🤗 Option 3: Hugging Face Spaces (Free)

1. Go to **[huggingface.co/spaces](https://huggingface.co/spaces)** and click **"Create new Space"**.
2. Set **Space SDK** to **Streamlit**.
3. Push or link your GitHub repository.
4. Hugging Face will automatically build and host the app with public sharing.

---

## 🐳 Option 4: Containerized Deployment (Docker / GCP Cloud Run / AWS ECS)

Build and test locally with Docker:
```bash
# 1. Build the Docker container
docker build -t studentpulse-ai .

# 2. Run container on port 8501
docker run -p 8501:8501 studentpulse-ai
```

Deploy to **Google Cloud Run**:
```bash
gcloud run deploy studentpulse-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8501
```

---

## 🔒 Environment Variables (Optional)

If using external database connections or authentication secrets:
- `STREAMLIT_SERVER_PORT`: `8501` (or `$PORT`)
- `STREAMLIT_SERVER_HEADLESS`: `true`
- `STREAMLIT_SERVER_ADDRESS`: `0.0.0.0`

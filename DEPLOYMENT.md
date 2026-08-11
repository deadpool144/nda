# Deploying LexForge Contract Platform to Render

This guide explains how to deploy the LexForge Contract Creator Platform to [Render](https://render.com/).

---

## Deployment Option 1: Blueprints (Recommended)

Render Blueprints allow you to configure and deploy your application using the `render.yaml` file included in this repository.

### Steps:
1. Push your repository to GitHub or GitLab.
2. Sign in to your [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** and select **Blueprint**.
4. Connect your GitHub/GitLab repository.
5. Render will automatically parse the `render.yaml` file.
6. Under **Environment Variables**, you will need to input your `GEMINI_API_KEY` (obtained from [Google AI Studio](https://aistudio.google.com/)).
7. Click **Apply**. Render will automatically provision the service, build it, and launch the web server.

---

## Deployment Option 2: Manual Deployment

If you prefer to configure the service manually through Render's web interface:

### Steps:
1. Push your repository to GitHub or GitLab.
2. Sign in to your [Render Dashboard](https://dashboard.render.com/).
3. Click **New +** and select **Web Service**.
4. Connect your repository.
5. Configure the service settings:
   - **Name**: `lexforge-contract-platform`
   - **Environment / Runtime**: `Python`
   - **Region**: Select the region closest to you
   - **Branch**: `main` (or your active branch)
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - **Instance Type**: `Free` (or any other tier)
6. Add the following **Environment Variables** under the **Advanced** section:
   - `GEMINI_API_KEY`: *Your actual Gemini API Key*
   - `LLM_MODEL`: `gemini-3.1-flash-lite` (or another model like `gemini-2.5-flash`)
   - `EMBEDDING_MODEL`: `models/gemini-embedding-001`
7. Click **Create Web Service**.

---

## Database Configuration (Persistence)

By default, the application uses an **SQLite** database (`contracts_v2.db`) located in the application directory. 

### Free Tier (Ephemeral Storage)
If you deploy on Render's **Free Tier**, the file system is ephemeral. Any data saved (like generated contracts and user activity) will be wiped every time the service restarts or redeploys.

### Production Setup (Persistent Storage)
For production use, you have two options to persist data:

#### Option A: Use Render PostgreSQL (Recommended)
1. Provision a free or paid **PostgreSQL** database on Render.
2. Copy the database's **Internal Connection String** (starts with `postgres://` or `postgresql://`).
3. Add a new environment variable `DATABASE_URL` to your LexForge Web Service on Render and paste the connection string.
4. The application will automatically detect the database type and initialize the tables on startup.

#### Option B: Use a Persistent Disk (Paid tiers only)
1. Upgrade your Web Service instance type to at least the **Starter** tier.
2. In the service settings, go to **Disks** and click **Add Disk**.
3. Set the Mount Path to `/data` and size to `1 GB`.
4. Add an environment variable:
   - `DATABASE_URL` = `sqlite:////data/contracts_v2.db`
5. This ensures the SQLite database file resides on a persistent volume that survives redeploys.

# AI Operations Cockpit

Centralized operations dashboard and API for AI telemetry and workflow automation.

![Cockpit Dashboard](https://via.placeholder.com/1200x600.png?text=AI+Operations+Cockpit)

## Overview
The AI Operations Cockpit monitors agent health, reviews logs, and provides a B2B sales automation engine for generating localized outreach pitches.

## Tech Stack
- **Backend**: Python (FastAPI / native scripts)
- **Edge Deployment**: Cloudflare Workers (`.wrangler`)
- **Data**: Local data tracking.

## Architecture
This project is divided into an edge component (Cloudflare) for high-availability request ingestion and a Python-based core for intensive processing. The `core/` directory contains business logic such as generating customized outreach data tailored to different GCC markets.

## Local Setup
1. Clone the repository.
2. Install Python dependencies (or setup a virtual environment).
3. Start the server using the provided `LAUNCH_AIOPS.bat` script or execute `python server.py`.

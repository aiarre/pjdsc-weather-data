# 🌊 PJDSC Flood Prediction System

**Project for PJDSC Hackathon 2025**
A web-based flood prediction system integrating AI, geospatial data, and weather analysis.

---

## 🚀 Overview

The **PJDSC Flood Prediction System** is designed to predict potential flooded areas based on user-provided **latitude**, **longitude**, and **radius**.
It uses a trained AI model deployed as a microservice, with clean API communication between backend and frontend layers.

### 🧩 Architecture

This project follows a **hybrid MVC + microservice architecture**:

* **Frontend:**
  Built with **React.js**, deployed on **Vercel**.
  → Temporary live link: [https://pjdsc-weather-data-frontend.vercel.app](https://pjdsc-weather-data-frontend.vercel.app)

* **Backend (API Gateway):**
  A **Django** application hosted on **Render**, acting as a secure middle layer between the frontend and the AI microservice.
  → Endpoint: [https://pjdsc-weather-data-backend.onrender.com](https://pjdsc-weather-data-backend.onrender.com)

* **AI Microservice:**
  A separate Python service hosted on **Render** for flood prediction using weather and location inputs.
  → Processes sanitized data sent from the backend and returns prediction results.

* **Storage:**
  **Supabase Storage** is used to store large model artifacts (e.g., `.pkl` files) and datasets.

---

## 🔐 Environment Variables

Below is the `.env` structure (no need to share your actual secrets — this is just for reference):

```env
SUPABASE_DATABASE_PASSWORD=
SUPABASE_URL=
SUPABASE_KEY=
MICROSERVICE_URL=
DJANGO_SECRET_KEY=
DJANGO_DEBUG=
```

⚠️ **Security Note:**
Do **not** commit your `.env` file to Git. Use Render’s or Vercel’s **Environment Variable settings** panel to manage these securely.

---

## 🧠 How It Works

1. The **frontend** sends an API request to the **backend** with parameters:

   ```json
   {
     "latitude": 14.5995,
     "longitude": 120.9842,
     "radius": 10000
   }
   ```

2. The **backend** sanitizes the request and forwards it to the **AI microservice**.

3. The **AI microservice** processes the data using the pre-trained model and returns predictions.

4. The **backend** sanitizes the response and sends it back to the **frontend** for display.

---

## 🛠️ Tech Stack

| Layer    | Technology                                |
| -------- | ----------------------------------------- |
| Frontend | React.js (Vite) + TailwindCSS             |
| Backend  | Django + REST Framework                   |
| AI Model | Python (scikit-learn, pandas, numpy)      |
| Storage  | Supabase                                  |
| Hosting  | Render (Backend + AI) & Vercel (Frontend) |

---

## 👨‍💻 Team Roles & Contributions

- **Leanne Mariz Austria** — Frontend & Project Management  
  Designed and implemented the web app interface, coordinated project milestones, and ensured smooth collaboration among team members.

- **Reuter Jan Camacho** — Backend Lead & Full-Stack Integration / Technical Lead  
  Refactored and developed the backend, optimized the AI pipeline, integrated frontend and backend components, and managed deployment on Render and Vercel.

- **John Mark Palpal-latoc** — Frontend Developer  
  Developed the core frontend features and interactive components of the web application.

- **Nicanor Froilan Pascual** — AI / Data Science Engineer  
  Handled end-to-end AI development, including data gathering, preprocessing, model training, and evaluation.

---

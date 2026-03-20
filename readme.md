<div align="center">

# 🎓 NexEvent

### Campus Event & Voting Management Platform

A comprehensive full-stack platform that transforms how universities manage events, elections, and student engagement — featuring real-time interactions, AI-powered recommendations, gamification, and blockchain-verified credentials.

[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=white)](https://reactjs.org/)
[![Django](https://img.shields.io/badge/Django-4.2_LTS-092E20?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Redis](https://img.shields.io/badge/Redis-7-DC382D?style=for-the-badge&logo=redis&logoColor=white)](https://redis.io/)
[![WebSocket](https://img.shields.io/badge/WebSocket-Django_Channels-blue?style=for-the-badge)](https://channels.readthedocs.io/)
[![Blockchain](https://img.shields.io/badge/Blockchain-Polygon_(MATIC)-8247E5?style=for-the-badge&logo=polygon&logoColor=white)](https://polygon.technology/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)

<br/>

[Features](#-features) •
[Tech Stack](#-tech-stack) •
[Architecture](#-architecture) •
[Getting Started](#-getting-started) •
[API Documentation](#-api-documentation) •
[Development Phases](#-development-phases) •
[Contributing](#-contributing)

<br/>

<img src="https://raw.githubusercontent.com/yourusername/nexevent/main/docs/assets/hero-banner.png" alt="NexEvent Platform Preview" width="800"/>

</div>

---

## 📋 Overview

**NexEvent** is an end-to-end campus event management and democratic voting platform designed for universities. It empowers students to discover and register for events, participate in live engagement activities, vote in campus elections, and earn rewards — while giving organizers and administrators powerful tools to manage the entire event lifecycle.

### 🎯 The Problem

Campus event management is fragmented — students miss events, organizers struggle with manual processes, and there's no transparent way to conduct campus elections or track engagement.

### 💡 The Solution

NexEvent unifies event discovery, registration, ticketing, live engagement, voting, and analytics into a single, modern platform with real-time capabilities, AI assistance, and blockchain verification.

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 📅 Event Management
- Multi-step event creation with admin approval workflow
- 5 categories: Academic, Cultural, Sports, Professional, Social
- Full-text search with fuzzy matching (PostgreSQL FTS + pg_trgm)
- Custom registration form builder
- Waitlist with automatic promotion

</td>
<td width="50%">

### 🎟️ QR Ticketing & Check-in
- Unique QR code generated per registration
- Camera-based scanning at venue entrance
- Real-time check-in dashboard (WebSocket-powered)
- Automatic attendance tracking
- Check-in confirmation notifications

</td>
</tr>
<tr>
<td width="50%">

### 🗳️ Voting System
- **4 voting types:** Elections, Polls, Surveys, Awards
- **5 voting methods:** Single choice, Multiple choice, Ranked choice, Rating/Score, Yes/No/Abstain
- Eligibility filtering (department, year, enrollment)
- Anonymous voting support
- Real-time vote count display
- Fraud detection & audit trails

</td>
<td width="50%">

### ⚡ Live Engagement
- 🔴 Live Polls with instant results
- ❓ Q&A Sessions with upvoting
- 🧠 Timed Quizzes with leaderboards
- 💬 Real-time Event Chat
- 😄 Emoji Reactions broadcast
- ✋ Virtual Raise Hand queue
- 🎨 Collaborative Whiteboard

</td>
</tr>
<tr>
<td width="50%">

### 🏆 Gamification
- Points system (registration, attendance, voting, reviews)
- **4 tiers:** 🥉 Bronze → 🥈 Silver → ���� Gold → 💎 Platinum
- Achievement badges with unlock criteria
- Attendance streaks with bonus multipliers
- Campus-wide leaderboards (filterable by department)
- Separate civic engagement leaderboard

</td>
<td width="50%">

### 🤖 AI-Powered Features
- **Smart Recommendations** — Personalized event suggestions using OpenAI embeddings + pgvector
- **Auto-Generate Descriptions** — AI writing assistant for event creation (GPT-4-turbo streaming)
- **Chatbot Assistant** — Conversational help with function calling mapped to API endpoints

</td>
</tr>
<tr>
<td width="50%">

### 🔗 Blockchain Verification
- Attendance certificates hashed on Polygon (MATIC)
- Immutable vote receipts on-chain
- Public verification page for certificates
- One-click LinkedIn credential sharing
- Batched transactions (~$0.001 per certificate)

</td>
<td width="50%">

### 💳 Payment System
- Stripe & Razorpay integration
- PCI DSS-compliant checkout
- Automatic refunds on cancellation
- Transaction history & revenue tracking
- Financial reports with payment method breakdown

</td>
</tr>
</table>

### 📊 Analytics & Reporting

| Role | Access |
|------|--------|
| **Student** | Personal stats: events attended, points, badges, voting history, certificates |
| **Organizer** | Own events: registrations, attendance, revenue, engagement metrics |
| **Admin** | Full platform: all events, users, voting, financial data, audit logs |

> 📥 All reports exportable as **CSV** and **PDF**

---

## 🛠️ Tech Stack

### Frontend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | **React 18** | Core UI framework |
| Build Tool | **Vite** | Fast HMR, ES modules |
| Styling | **Tailwind CSS + shadcn/ui** | Utility-first styling + accessible components |
| Routing | **React Router v6** | 200+ page SPA with nested layouts |
| Server State | **TanStack Query v5** | API caching, background sync, pagination |
| Client State | **Zustand** | Auth session, UI state, notifications |
| HTTP Client | **Axios** | JWT injection, auto token refresh on 401 |
| Forms | **React Hook Form + Zod** | Multi-step forms, schema validation |
| Charts | **Recharts** | Analytics dashboards, voting results |
| Real-time | **Native WebSocket API** | Live polls, Q&A, vote counts, check-in |
| QR Code | **react-qr-code + html5-qrcode** | QR display & camera scanning |
| Testing | **Vitest + RTL + Playwright** | Unit, integration, E2E |

### Backend

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Framework | **Django 4.2 LTS** | Core backend, ORM, admin panel |
| API | **DRF + drf-spectacular** | RESTful API + auto OpenAPI 3.0 docs |
| Database | **PostgreSQL 15** | Primary data store |
| Auth | **SimpleJWT + django-allauth + django-axes** | JWT tokens, email verification, brute force protection |
| Async Tasks | **Celery 5 + django-celery-beat** | Emails, reminders, waitlist, certificates |
| Cache / Broker | **Redis 7** | Celery broker, Django cache, WebSocket channel layer |
| Real-time | **Django Channels 4 + Daphne** | WebSocket server for live features |
| File Storage | **django-storages + Cloudflare R2** | Event photos, QR codes, certificates |
| Search | **PostgreSQL FTS + django-watson + pg_trgm** | Full-text + fuzzy event search |
| AI | **OpenAI API + pgvector** | Recommendations, descriptions, chatbot |
| Blockchain | **Web3.py 6 (Polygon)** | Certificate minting, vote receipts |
| Email | **django-anymail → SendGrid** | Transactional emails |
| Monitoring | **Sentry + Railway metrics** | Error tracking, observability |

### Infrastructure

| Layer | Technology |
|-------|-----------|
| Dev Environment | Docker + Docker Compose |
| Frontend Deploy | Vercel |
| Backend + DB + Redis | Railway |
| Reverse Proxy | Nginx (development) |
| Container Registry | Docker Hub / Railway |

---

## 🏗️ Architecture
┌──────────────────────────────────────────────────────────────────┐
│ FRONTEND │
│ │
│ React 18 + Vite + Tailwind CSS + shadcn/ui │
│ ┌──────────┐ ┌──────────────┐ ┌─────────────┐ ┌─────────────┐ │
│ │ React │ │ TanStack │ │ Zustand │ │ WebSocket │ │
│ │ Router │ │ Query v5 │ │ Store │ │ Client │ │
│ └──────────┘ └──────────────┘ └─────────────┘ └──────┬──────┘ │
│ │ │ │
│ Deployed on: Vercel │ Axios + JWT Interceptors │ │
└───────────────────────┼────────────────────────────────┼────────┘
│ HTTPS (REST API) │ WSS
▼ ▼
┌──────────────────────────────────────────────────────────────────┐
│ BACKEND │
│ │
│ Django 4.2 LTS + Gunicorn + Uvicorn (ASGI) │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────────────────┐ │
│ │ Django REST │ │ Django │ │ Celery 5 │ │
│ │ Framework │ │ Channels 4 │ │ + django-celery-beat │ │
│ │ + SimpleJWT │ │ + Daphne │ │ (async tasks) │ │
│ └──────┬───────┘ └──────┬───────┘ └────────────┬─────────────┘ │
│ │ │ │ │
│ Deployed on: Railway │ │ │
└─────────┼────────────────┼───────────────────────┼───────────────┘
│ │ │
▼ ▼ ▼
┌─────────────────┐ ┌──────────┐ ┌─────────────────────────────────┐
│ PostgreSQL 15 │ │ Redis 7 │ │ External Services │
│ + pgvector │ │ (Cache, │ │ ┌─────────┐ ┌───────────────┐ │
│ + pg_trgm │ │ Broker, │ │ │ OpenAI │ │ Polygon │ │
│ │ │ WS) │ │ │ API │ │ Blockchain │ │
│ │ │ │ │ ├─────────┤ ├───────────────┤ │
│ │ │ │ │ │ Stripe/ │ │ SendGrid/ │ │
│ │ │ │ │ │ Razorpay│ │ Twilio │ │
│ │ │ │ │ └─────────┘ └───────────────┘ │
└─────────────────┘ └──────────┘ └─────────────────────────────────┘

---

## 👥 User Roles & Permissions

| Permission | Student | Organizer | Admin |
|-----------|:-------:|:---------:|:-----:|
| Browse & Register for Events | ✅ | ✅ | ✅ |
| Vote in Elections | ✅ | ✅ | ✅ |
| View Personal Analytics | ✅ | ✅ | ✅ |
| Request Role Upgrade | ✅ | ✅ | — |
| Create & Manage Events | ❌ | ✅ | ✅ |
| Create Voting Events | ❌ | ✅ | ✅ |
| Launch Live Engagement | ❌ | ✅ | ✅ |
| Approve Events | ❌ | ❌ | ✅ |
| Manage Users & Roles | ❌ | ❌ | ✅ |
| Manage Venues | ❌ | ❌ | ✅ |
| View System Analytics | ❌ | ❌ | ✅ |
| View Audit Logs | ❌ | ❌ | ✅ |

---

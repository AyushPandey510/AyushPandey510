<p align="center">
  <a href="https://portfolio-ayushpandey.vercel.app"><img src="assets/header.svg" width="100%" alt="Ayush Pandey"/></a>
</p>

<p align="center">
  <a href="https://portfolio-ayushpandey.vercel.app"><img src="https://img.shields.io/badge/Portfolio-161B22?style=for-the-badge&logo=vercel&logoColor=8B949E" alt="Portfolio"/></a>
  <a href="https://www.linkedin.com/in/ayush-pandey-097027242"><img src="https://img.shields.io/badge/LinkedIn-161B22?style=for-the-badge&logo=linkedin&logoColor=8B949E" alt="LinkedIn"/></a>
  <a href="mailto:ayushgauravpandey@gmail.com"><img src="https://img.shields.io/badge/Email-161B22?style=for-the-badge&logo=gmail&logoColor=8B949E" alt="Email"/></a>
  <a href="https://swift-share-tau.vercel.app"><img src="https://img.shields.io/badge/SwiftShare-161B22?style=for-the-badge&logo=vercel&logoColor=8B949E" alt="SwiftShare live"/></a>
</p>

Backends in **Rust** and **Python**, frontends in **React**, mobile apps in **Flutter**. I pick the stack each problem needs and build it end to end.

## Featured
<sub>Pinned projects, most recently worked on first. Click a card to open the repo.</sub>

<!-- AUTO:FEATURED:START -->
<p align="center">
  <a href="https://github.com/AyushPandey510/SwiftShare"><img src="assets/cards/SwiftShare.svg" width="49%" alt="SwiftShare"/></a>
  <a href="https://github.com/AyushPandey510/anonymous"><img src="assets/cards/anonymous.svg" width="49%" alt="Space"/></a>
  <a href="https://github.com/AyushPandey510/expense_calc"><img src="assets/cards/expense_calc.svg" width="49%" alt="XpenseCalc"/></a>
  <a href="https://github.com/AyushPandey510/LifeEngine"><img src="assets/cards/LifeEngine.svg" width="49%" alt="LifeEngine AI"/></a>
  <a href="https://github.com/AyushPandey510/PDF-QA-RAG-OLLAMA-llama3"><img src="assets/cards/PDF-QA-RAG-OLLAMA-llama3.svg" width="49%" alt="PDF-QA RAG"/></a>
</p>
<!-- AUTO:FEATURED:END -->

## What I build

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"monospace","fontSize":"15px","primaryColor":"#161B22","primaryTextColor":"#E6EDF3","primaryBorderColor":"#30363D","lineColor":"#6E7681","secondaryColor":"#161B22","tertiaryColor":"#161B22","clusterBkg":"#0D1117","clusterBorder":"#30363D","edgeLabelBackground":"#0D1117"}}}%%
flowchart LR
    ME(("Ayush")):::core
    ME --> RT["Realtime"]:::rt & AI["AI / RAG"]:::ai & MO["Mobile"]:::mo & BE["Backend"]:::be & SEC["Security"]:::sec & WEB["Web"]:::web
    RT --> SPACE["Space<br/>Axum · WS · geofence"]:::rt
    RT --> SS["SwiftShare<br/>warp · QR · 4 clients"]:::rt
    AI --> LE["LifeEngine AI<br/>FastAPI · FAISS · Groq"]:::ai
    AI --> RAG["PDF-QA RAG<br/>FAISS · Llama 3"]:::ai
    MO --> XC["XpenseCalc<br/>SMS parser · sqflite"]:::mo
    BE --> RC["RustCart API<br/>Actix · Postgres"]:::be
    SEC --> PG["PhisGuard<br/>Flask · sklearn · ext"]:::sec
    WEB --> ZB["Zettabyte<br/>FastAPI · React"]:::web
    WEB --> PF["Portfolio<br/>React · shadcn"]:::web

    classDef core fill:#6E8CA8,stroke:#6E8CA8,color:#0D1117,font-weight:bold
    classDef rt fill:#161B22,stroke:#6E8CA8,color:#E6EDF3
    classDef ai fill:#161B22,stroke:#8A7FA8,color:#E6EDF3
    classDef mo fill:#161B22,stroke:#6F9A82,color:#E6EDF3
    classDef be fill:#161B22,stroke:#A8906A,color:#E6EDF3
    classDef sec fill:#161B22,stroke:#A86B6B,color:#E6EDF3
    classDef web fill:#161B22,stroke:#7A92A8,color:#E6EDF3
```

<p align="center">
  <a href="https://github.com/AyushPandey510/anonymous"><kbd>Space</kbd></a>
  <a href="https://github.com/AyushPandey510/SwiftShare"><kbd>SwiftShare</kbd></a>
  <a href="https://github.com/AyushPandey510/LifeEngine"><kbd>LifeEngine AI</kbd></a>
  <a href="https://github.com/AyushPandey510/PDF-QA-RAG-OLLAMA-llama3"><kbd>PDF-QA RAG</kbd></a>
  <a href="https://github.com/AyushPandey510/expense_calc"><kbd>XpenseCalc</kbd></a>
  <a href="https://github.com/AyushPandey510/Rust-Ecom-Api"><kbd>RustCart</kbd></a>
  <a href="https://github.com/AyushPandey510/Phis_Shield"><kbd>PhisGuard</kbd></a>
  <a href="https://github.com/AyushPandey510/Zettabyte"><kbd>Zettabyte</kbd></a>
</p>

## How they work
<sub>Architecture of the main projects. Expand one.</sub>

<details>
<summary><b>Space</b>: anonymous chat that only opens when you're physically inside the zone</summary>

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"monospace","fontSize":"15px","primaryColor":"#161B22","primaryTextColor":"#E6EDF3","primaryBorderColor":"#30363D","lineColor":"#6E7681","secondaryColor":"#161B22","tertiaryColor":"#161B22","clusterBkg":"#0D1117","clusterBorder":"#30363D","edgeLabelBackground":"#0D1117"}}}%%
flowchart TB
    APP["Flutter app"] -->|GPS fix + device id| NG["nginx"]
    NG --> AUTH["Auth<br/>HMAC(device id) → JWT + refresh"]
    NG --> GEO
    subgraph GEO["Geofence engine (server-authoritative)"]
        direction LR
        S1["median<br/>smoothing"] --> S2["spoof<br/>detection"] --> S3["hysteresis<br/>buffer"] --> S4["validator<br/>active · grace · expired"]
    end
    GEO --> CHAT["Chat: REST + WebSocket<br/>replies · reactions · polls"]
    CHAT --> MOD["Moderation worker<br/>(mpsc)"]
    CHAT & GEO & AUTH --> PG[("PostgreSQL")]
    SWEEP["Session sweeper"] --> PG
```

[→ open repo](https://github.com/AyushPandey510/anonymous)
</details>

<details>
<summary><b>SwiftShare</b>: send a file, share a 6-char code</summary>

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"monospace","fontSize":"15px","primaryColor":"#161B22","primaryTextColor":"#E6EDF3","primaryBorderColor":"#30363D","lineColor":"#6E7681","secondaryColor":"#161B22","tertiaryColor":"#161B22","clusterBkg":"#0D1117","clusterBorder":"#30363D","edgeLabelBackground":"#0D1117"}}}%%
flowchart LR
    W["React web<br/>(Vercel)"] & M["Flutter"] & D["Electron"] -->|multipart stream| API["warp API<br/>(Render)"]
    API --> CODE["6-char code<br/>+ link + QR"]
    API --> DISK[("files on disk")]
    API --> DB[("SQLite<br/>expiry · max downloads")]
    CODE --> R["Receiver"] -->|GET /download/:code| API
    API -. "WS progress" .-> W
```

[→ open repo](https://github.com/AyushPandey510/SwiftShare) · [→ live app](https://swift-share-tau.vercel.app)
</details>

<details>
<summary><b>LifeEngine AI</b>: talk to your future self</summary>

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"monospace","fontSize":"15px","primaryColor":"#161B22","primaryTextColor":"#E6EDF3","primaryBorderColor":"#30363D","lineColor":"#6E7681","secondaryColor":"#161B22","tertiaryColor":"#161B22","clusterBkg":"#0D1117","clusterBorder":"#30363D","edgeLabelBackground":"#0D1117"}}}%%
flowchart LR
    UI["React + Vite"] -->|/api| F["FastAPI"]
    F --> A["auth · profile · decisions<br/>insights · documents"]
    F --> CHAT["chat (streaming)"] --> LLM["Groq LLM"]
    CHAT <--> MEM[("FAISS<br/>conversation memory")]
    F --> PG[("PostgreSQL")]
    F <--> RD[("Redis cache")]
    F --> CQ["Celery workers<br/>memory + scheduled jobs"] --> MEM
```

[→ open repo](https://github.com/AyushPandey510/LifeEngine)
</details>

<details>
<summary><b>PDF-QA RAG</b>: answers only from the document, or says it doesn't know</summary>

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"monospace","fontSize":"15px","primaryColor":"#161B22","primaryTextColor":"#E6EDF3","primaryBorderColor":"#30363D","lineColor":"#6E7681","secondaryColor":"#161B22","tertiaryColor":"#161B22","clusterBkg":"#0D1117","clusterBorder":"#30363D","edgeLabelBackground":"#0D1117"}}}%%
flowchart TB
    subgraph INGEST["ingest.py"]
        direction LR
        PDF["PDF"] --> MU["PyMuPDF"] --> CL["clean"] --> CH["overlapping<br/>chunks"] --> EM["MiniLM-L6-v2<br/>embeddings"] --> IX[("FAISS")]
    end
    Q["POST /ask"] --> QE["embed question"] --> IX
    IX -->|top-k chunks| G{"L2 distance ≤ 1.5?"}
    G -- yes --> LL["Llama 3 via Ollama"] --> ANS["answer"]
    G -- no --> NA["'not available in the document'"]
```

[→ open repo](https://github.com/AyushPandey510/PDF-QA-RAG-OLLAMA-llama3)
</details>

<details>
<summary><b>XpenseCalc</b>: bank SMS in, spending insights out</summary>

```mermaid
%%{init: {"theme":"base","themeVariables":{"fontFamily":"monospace","fontSize":"15px","primaryColor":"#161B22","primaryTextColor":"#E6EDF3","primaryBorderColor":"#30363D","lineColor":"#6E7681","secondaryColor":"#161B22","tertiaryColor":"#161B22","clusterBkg":"#0D1117","clusterBorder":"#30363D","edgeLabelBackground":"#0D1117"}}}%%
flowchart TB
    SMS["SMS inbox"] --> SYNC["sync range<br/>7d · 90d · 180d · all"] --> P["parser<br/>bank sender · UPI · amount · type"]
    P --> F{"promo / OTP /<br/>balance-only?"}
    F -- drop --> X["discard"]
    F -- keep --> DB[("sqflite<br/>unique(sender, message)")]
    DB --> L["labels<br/>Food · Rent · Travel…"] --> CH["fl_chart analytics"]
```

[→ open repo](https://github.com/AyushPandey510/expense_calc)
</details>

## Activity

<p align="center"><img src="assets/calendar.svg" width="100%" alt="Commit calendar"/></p>
<p align="center"><img src="assets/radar.svg" width="100%" alt="Commits per week"/></p>

**Latest commits**

<!-- AUTO:COMMITS:START -->
| When | Repo | Commit |
|:--|:--|:--|
| <sub>5h ago</sub> | **counter-drop** | [`353055b`](https://github.com/AyushPandey510/counter-drop/commit/353055ba0a46737a63e6c462cdba765832e2f717) chore: initial import with docs, design and backend slice |
| <sub>12h ago</sub> | **SwiftShare** | [`cdba414`](https://github.com/AyushPandey510/SwiftShare/commit/cdba414333e263f970623cd4cdeba2a58f9211c3) feat: added a structured design file in web and dark mode fix |
| <sub>12h ago</sub> | **SwiftShare** | [`e9f4307`](https://github.com/AyushPandey510/SwiftShare/commit/e9f43071d2d5425179ce680db3d0c3c947c1572f) feat: added a structured design file and dark mode loader fix |
| <sub>12h ago</sub> | **SwiftShare** | [`4b6b17e`](https://github.com/AyushPandey510/SwiftShare/commit/4b6b17e7055c77d667a931e1d4e7e96e1cc9f042) fix: Mobile download bug |
| <sub>1w ago</sub> | **gps-mock** | [`c1b7420`](https://github.com/AyushPandey510/gps-mock/commit/c1b7420e11786d2e3ce04d1b5d90388acd849067) fix: build issue in github workflow |
| <sub>1w ago</sub> | **gps-mock** | [`162b130`](https://github.com/AyushPandey510/gps-mock/commit/162b13032db3b26841593807f0a910b838abfdf2) added privacy-policy screen and fixed minor issues |
| <sub>1w ago</sub> | **gps-mock** | [`67e7e46`](https://github.com/AyushPandey510/gps-mock/commit/67e7e46967f4feaa5e4bd1760c5484c699bfc4b2) GPS MOCK Location Ready |
| <sub>1w ago</sub> | **Space** | [`2de0291`](https://github.com/AyushPandey510/anonymous/commit/2de0291f28df2d22a574bf74c917f8a17f6e20f1) fix: theme based on system by-default and settings page |
| <sub>1w ago</sub> | **Space** | [`9b277f4`](https://github.com/AyushPandey510/anonymous/commit/9b277f46f1ecf04cebb2700675bebbb7390d3944) fix: relpy message |
| <sub>1w ago</sub> | **Space** | [`ee4cfed`](https://github.com/AyushPandey510/anonymous/commit/ee4cfed3c643c8b2fa598fb448d2407be6526f04) fix: Add privacy-safe location retention and secure auth storage |
<!-- AUTO:COMMITS:END -->

## Metrics

<p align="center"><img src="assets/rhythm.svg" width="100%" alt="When I commit"/></p>
<p align="center"><img src="assets/types.svg" width="100%" alt="Commit types"/></p>

<!-- AUTO:PIE:START -->
```mermaid
%%{init: {"theme":"base","themeVariables":{"pie1":"#6E8CA8","pie2":"#6F9A82","pie3":"#A8906A","pie4":"#8A7FA8","pie5":"#A86B6B","pie6":"#7A92A8","pie7":"#8C956A","pie8":"#6E7681","pieStrokeColor":"#0D1117","pieStrokeWidth":"2px","pieOuterStrokeColor":"#30363D","pieTitleTextColor":"#E6EDF3","pieSectionTextColor":"#0D1117","pieLegendTextColor":"#E6EDF3","fontFamily":"monospace"}}}%%
pie showData title Where my commits went, last 12 months
    "SwiftShare" : 44
    "Space" : 18
    "Placement_study_Material" : 18
    "LifeEngine AI" : 13
    "School" : 9
    "XpenseCalc" : 7
    "skill-navigator-hub" : 6
    "others" : 23
```
<!-- AUTO:PIE:END -->

## Project comparison

<p align="center"><img src="assets/compare.svg" width="100%" alt="Project comparison"/></p>
<p align="center"><img src="assets/timeline.svg" width="100%" alt="Project timeline"/></p>

<details>
<summary><b>Comparison table</b></summary>

<!-- AUTO:COMPARE:START -->
| Project | Commits | Active days (12m) | First commit | Latest commit | Main language | Size |
|:--|--:|--:|:--|:--|:--|--:|
| [counter-drop](https://github.com/AyushPandey510/counter-drop) | 1 | 1 | Sep 2026 | 27 Sep 2026 | `Go` | 35 KB |
| [SwiftShare](https://github.com/AyushPandey510/SwiftShare) | 45 | 10 | Aug 2025 | 27 Sep 2026 | `Dart` | 734 KB |
| [gps-mock](https://github.com/AyushPandey510/gps-mock) | 3 | 1 | Sep 2026 | 20 Sep 2026 | `Dart` | 512 KB |
| [Space](https://github.com/AyushPandey510/anonymous) | 26 | 9 | Jul 2026 | 14 Sep 2026 | `Dart` | 462 KB |
| [FieldTrace](https://github.com/AyushPandey510/FieldTrace) | 1 | 1 | Sep 2026 | 07 Sep 2026 | `Dart` | 294 KB |
| [XpenseCalc](https://github.com/AyushPandey510/expense_calc) | 8 | 5 | Sep 2025 | 09 Aug 2026 | `Dart` | 413 KB |
| [Procastinator](https://github.com/AyushPandey510/Procastinator) | 2 | 2 | Jan 2026 | 26 Jul 2026 | `Makefile` | 615 KB |
| [School-Management-System](https://github.com/AyushPandey510/School-Management-System) | 1 | 0 | May 2026 | 22 May 2026 | `Dart` | 270 KB |
| [indiamart-data-engineering-pipeline](https://github.com/AyushPandey510/indiamart-data-engineering-pipeline) | 2 | 2 | Apr 2026 | 19 May 2026 | `Python` | 64 KB |
| [skill-navigator-hub](https://github.com/AyushPandey510/skill-navigator-hub) | 19 | 1 | Jan 2025 | 07 May 2026 | `TypeScript` | 217 KB |
| [Portfolio](https://github.com/AyushPandey510/Portfolio) | 4 | 2 | Jan 2026 | 06 May 2026 | `TypeScript` | 182 KB |
| [LifeEngine AI](https://github.com/AyushPandey510/LifeEngine) | 13 | 3 | Apr 2026 | 05 May 2026 | `Python` | 155 KB |
| [PDF-QA RAG](https://github.com/AyushPandey510/PDF-QA-RAG-OLLAMA-llama3) | 2 | 2 | Apr 2026 | 02 May 2026 | `Python` | 6 KB |
| [Placement_study_Material](https://github.com/AyushPandey510/Placement_study_Material) | 18 | 1 | Apr 2026 | 01 May 2026 | `Python` | 256.4 MB |
| [School](https://github.com/AyushPandey510/School) | 9 | 3 | Mar 2026 | 06 Apr 2026 | `JavaScript` | 83 KB |
| [Stock_Market](https://github.com/AyushPandey510/Stock_Market) | 1 | 1 | Apr 2026 | 01 Apr 2026 | `Python` | 33 KB |
| [Madhav-gpt](https://github.com/AyushPandey510/Madhav-gpt) | 5 | 1 | Mar 2026 | 24 Mar 2026 | `JavaScript` | 50 KB |
| [Algerian_Forest_](https://github.com/AyushPandey510/Algerian_Forest_) | 2 | 1 | Mar 2026 | 21 Mar 2026 | `Python` | 56.7 MB |
| [PhisGuard](https://github.com/AyushPandey510/Phis_Shield) | 3 | 2 | Nov 2025 | 29 Nov 2025 | `Python` | 555 KB |
| [RustCart API](https://github.com/AyushPandey510/Rust-Ecom-Api) | 5 | 1 | Jul 2025 | 13 Oct 2025 | `Rust` | 146 KB |
| [Zettabyte](https://github.com/AyushPandey510/Zettabyte) | 3 | 0 | Jul 2025 | 10 Jul 2025 | `TypeScript` | 221 KB |
<!-- AUTO:COMPARE:END -->

</details>

## Languages

<p align="center"><img src="assets/stack.svg" width="100%" alt="Languages"/></p>

## All repositories

<!-- AUTO:ALL:START -->
| # | Project | Stack | Last commit | Status |
|:-:|:--|:--|:--|:-:|
| 01 | [**counter-drop**](https://github.com/AyushPandey510/counter-drop)<br><sub>No description yet.</sub> | `Go` | [chore: initial import with docs, design and b…](https://github.com/AyushPandey510/counter-drop/commit/353055ba0a46737a63e6c462cdba765832e2f717)<br><sub>5h ago</sub> | active |
| 02 | [**SwiftShare**](https://github.com/AyushPandey510/SwiftShare) · [live ↗](https://swift-share-tau.vercel.app)<br><sub>Send a file, share a 6-char code. Rust/warp API, React web, Flutter +…</sub> | `Dart` | [feat: added a structured design file in web a…](https://github.com/AyushPandey510/SwiftShare/commit/cdba414333e263f970623cd4cdeba2a58f9211c3)<br><sub>12h ago</sub> | active |
| 03 | [**gps-mock**](https://github.com/AyushPandey510/gps-mock)<br><sub>No description yet.</sub> | `Dart` | [fix: build issue in github workflow](https://github.com/AyushPandey510/gps-mock/commit/c1b7420e11786d2e3ce04d1b5d90388acd849067)<br><sub>1w ago</sub> | active |
| 04 | [**Space**](https://github.com/AyushPandey510/anonymous)<br><sub>Anonymous, location-gated chat rooms. Rust/Axum geofence engine + Flu…</sub> | `Dart` | [fix: theme based on system by-default and set…](https://github.com/AyushPandey510/anonymous/commit/2de0291f28df2d22a574bf74c917f8a17f6e20f1)<br><sub>1w ago</sub> | active |
| 05 | [**FieldTrace**](https://github.com/AyushPandey510/FieldTrace)<br><sub>No description yet.</sub> | `Dart` | [Quick Prototye Ready](https://github.com/AyushPandey510/FieldTrace/commit/ac9307ddcb5a7ebf881b348dcd3d3e91f26d7eb3)<br><sub>2w ago</sub> | stable |
| 06 | [**XpenseCalc**](https://github.com/AyushPandey510/expense_calc)<br><sub>Reads bank SMS, parses UPI/debit/credit and charts your spending. Flu…</sub> | `Dart` | [update: updated the readme](https://github.com/AyushPandey510/expense_calc/commit/71977b8c428a4dff69cc7899b784c2970bbadb55)<br><sub>1mo ago</sub> | stable |
| 07 | [**Procastinator**](https://github.com/AyushPandey510/Procastinator)<br><sub>No description yet.</sub> | `Makefile` | [fix:resolved bugs](https://github.com/AyushPandey510/Procastinator/commit/0421924b70d957f609741e70d8b2a3a3cd81157e)<br><sub>2mo ago</sub> | stable |
| 08 | [**School-Management-System**](https://github.com/AyushPandey510/School-Management-System)<br><sub>No description yet.</sub> | `Dart` | [Initial Commit](https://github.com/AyushPandey510/School-Management-System/commit/92d82f99df1ae1ad35e0efe22c4d786efece91a3)<br><sub>4mo ago</sub> | dormant |
| 09 | [**indiamart-data-engineering-pipeline**](https://github.com/AyushPandey510/indiamart-data-engineering-pipeline)<br><sub>No description yet.</sub> | `Python` | [Fix readme](https://github.com/AyushPandey510/indiamart-data-engineering-pipeline/commit/17d6c0d3d5eed62689e83c5bb74184e3f49142a1)<br><sub>4mo ago</sub> | dormant |
| 10 | [**skill-navigator-hub**](https://github.com/AyushPandey510/skill-navigator-hub) · [live ↗](https://skill-navigator-hub.vercel.app)<br><sub>No description yet.</sub> | `TypeScript` | [Remove invalid runtime config](https://github.com/AyushPandey510/skill-navigator-hub/commit/097d2151d355e61fe3cfb19c8b5067c95dbce77d)<br><sub>4mo ago</sub> | dormant |
| 11 | [**Portfolio**](https://github.com/AyushPandey510/Portfolio) · [live ↗](https://portfolio-ayushpandey.vercel.app)<br><sub>Personal site. React, Vite, TypeScript, shadcn/ui, Tailwind.</sub> | `TypeScript` | [Revise About section for clarity and detail](https://github.com/AyushPandey510/Portfolio/commit/b464c55146aad7d49f2510e911c08c024a232cc5)<br><sub>4mo ago</sub> | dormant |
| 12 | [**LifeEngine AI**](https://github.com/AyushPandey510/LifeEngine) · [live ↗](https://life-engine-orcin.vercel.app)<br><sub>Chat with your future self. FastAPI, Postgres, Redis, Celery, FAISS m…</sub> | `Python` | [fix alembic multiple heads and shorten revisi…](https://github.com/AyushPandey510/LifeEngine/commit/e168fbe061ea47eaf8d6e24c66f0362c9558040d)<br><sub>4mo ago</sub> | dormant |

<details><summary><b>+ 9 more repos</b></summary>

| # | Project | Stack | Last commit | Status |
|:-:|:--|:--|:--|:-:|
| 13 | [**PDF-QA RAG**](https://github.com/AyushPandey510/PDF-QA-RAG-OLLAMA-llama3)<br><sub>Ask a PDF anything, answered only from its text. MiniLM embeddings, F…</sub> | `Python` | [Update README.md](https://github.com/AyushPandey510/PDF-QA-RAG-OLLAMA-llama3/commit/d5f4e7b3fc9d632d290937b62525a2d5a9684145)<br><sub>4mo ago</sub> | dormant |
| 14 | [**Placement_study_Material**](https://github.com/AyushPandey510/Placement_study_Material) · [live ↗](https://placement-study-material.vercel.app)<br><sub>No description yet.</sub> | `Python` | [fix: update Groq model name and fix indentati…](https://github.com/AyushPandey510/Placement_study_Material/commit/9b52d923f1723ccd0187e935c27824c452bd56e0)<br><sub>4mo ago</sub> | dormant |
| 15 | [**School**](https://github.com/AyushPandey510/School) · [live ↗](https://school-two-sand.vercel.app)<br><sub>Edumentors Kids International School</sub> | `JavaScript` | [resolved the issue of learn more button in ad…](https://github.com/AyushPandey510/School/commit/0b84a1039bbf2d8a24c94997f969eb3077ee06ef)<br><sub>5mo ago</sub> | dormant |
| 16 | [**Stock_Market**](https://github.com/AyushPandey510/Stock_Market)<br><sub>No description yet.</sub> | `Python` | [Initial commit](https://github.com/AyushPandey510/Stock_Market/commit/0a7983a0e12d6cb19eece95fe298a04ccccecc45)<br><sub>5mo ago</sub> | dormant |
| 17 | [**Madhav-gpt**](https://github.com/AyushPandey510/Madhav-gpt)<br><sub>No description yet.</sub> | `JavaScript` | [Fixed the issues listed in BUGFIXES.md](https://github.com/AyushPandey510/Madhav-gpt/commit/fd7404c888822d8720abf808022173317488c6ef)<br><sub>6mo ago</sub> | dormant |
| 18 | [**Algerian_Forest_**](https://github.com/AyushPandey510/Algerian_Forest_)<br><sub>No description yet.</sub> | `Python` | [score changes](https://github.com/AyushPandey510/Algerian_Forest_/commit/dbf4fcf392f81fc8afd53592a12cf00534146919)<br><sub>6mo ago</sub> | dormant |
| 19 | [**PhisGuard**](https://github.com/AyushPandey510/Phis_Shield)<br><sub>Chrome extension + Flask API that scores URLs &amp; emails with scikit-le…</sub> | `Python` | [Final Changes before submission](https://github.com/AyushPandey510/Phis_Shield/commit/87ad0f3b2ca1f08e21174ff721982cc6e82106a7)<br><sub>10mo ago</sub> | dormant |
| 20 | [**RustCart API**](https://github.com/AyushPandey510/Rust-Ecom-Api)<br><sub>E-commerce backend: Actix Web, Postgres, JWT/RBAC, Razorpay, Swagger.</sub> | `Rust` | [swagger sand other errors resolved](https://github.com/AyushPandey510/Rust-Ecom-Api/commit/dd9b7d4b5f083f06035e2572c2dcff9b28a27d20)<br><sub>11mo ago</sub> | dormant |
| 21 | [**Zettabyte**](https://github.com/AyushPandey510/Zettabyte)<br><sub>Event manager with QR check-in. FastAPI + SQLAlchemy backend, React/V…</sub> | `TypeScript` | [frontend added](https://github.com/AyushPandey510/Zettabyte/commit/a74df207f319234978c4732449daa48e7ba02325)<br><sub>1y ago</sub> | dormant |

</details>
<!-- AUTO:ALL:END -->

<p align="center"><img src="assets/snake.svg" width="100%" alt="Contribution graph"/></p>

<p align="center">
<!-- AUTO:UPDATED:START -->
<sub>Updated automatically · 27 Sep 2026, 21:26 UTC</sub>
<!-- AUTO:UPDATED:END -->
</p>

# OverAchiever

> **Automated video game tracking and metadata enrichment pipeline.**

OverAchiever is a high-performance backend system designed to simplify the lifecycle of game tracking. By orchestrating data from the **Steam Store** and **HowLongToBeat**, it transforms simple queries into rich, multi-dimensional profiles—eliminating manual record-keeping and data entry.

---

## Key Features

* **Automated Metadata Ingestion**: Dynamically fetches game titles, developers, publishers, scores, and high-res header images from the **Steam Store API**.
* **Heuristic Playtime Prediction**: Automatically links game records to **HowLongToBeat (HLTB)** completion metrics (Main Story, Extra, Completionist) using similarity-based matching.
* **Smart Selection Engine**: Implements a "Search & Auto-Add" flow where the system resolves IDs and metadata gaps behind the scenes—enabling a "Zero-ID" user experience.
* **Asynchronous Architecture**: Built on a non-blocking I/O core using **FastAPI** and **httpx**, allowing concurrent processing of third-party API requests.
* **Production-Ready Infrastructure**: Fully containerized environment with integrated database, caching, and message broker nodes.

---

## Technical Architecture & Data Pipeline

OverAchiever is designed as a **Decision Support and Data Enrichment Pipeline**:

1. **Ingestion Layer**: Asynchronously queries the Steam Store API for candidate metadata using heuristic search terms.
2. **Verification Layer**: Validates external JSON payloads against strict **Pydantic** schemas to ensure data integrity.
3. **Enrichment Engine**: Performs secondary lookups via **HLTB** to append estimated completion times, performing automated record linkage between disparate datasets.
4. **Persistence Layer**: Mapped via **SQLModel (SQLAlchemy)** to a **PostgreSQL** relational database.
5. **Event Orchestration**: Prepared for asynchronous background synchronization using **Apache Kafka** for large-scale data updates.

---

## Technology Stack

| Component | Technology |
| :--- | :--- |
| **Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.12+) |
| **Database / ORM** | [PostgreSQL](https://www.postgresql.org/) / [SQLModel](https://sqlmodel.tiangolo.com/) |
| **Containerization** | [Docker](https://www.docker.com/) |
| **Async Client** | [httpx](https://www.python-httpx.org/) |
| **Messaging** | [Apache Kafka](https://kafka.apache.org/) (Work-in-progress Sync Pipeline) |
| **Caching** | [Redis](https://redis.io/) |

---

## Getting Started

### Prerequisites

*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) installed.

### Setup & Launch

The fastest way to spin up the entire cluster (API, Database, Redis, Kafka, Worker) is via Docker Compose:

1.  **Clone the repository**:

    ```bash
    git clone https://github.com/your-username/OverAchiever.git
    cd OverAchiever
    ```

2.  **Configure Environment**:
    Create a `.env` file in the root directory (refer to the sample below):

    ```env
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=your_password
    POSTGRES_DB=overachiever_db
    POSTGRES_HOST=db
    POSTGRES_PORT=5432
    STEAM_API_KEY=your_key_here
    ```

3.  **Build and Launch**:

    ```bash
    docker-compose up --build -d
    ```

Once the containers are running, you can access the interactive API docs at `http://localhost:8000/docs`.

---

## API Usage Examples

Once the server is running, access the interactive documentation at `http://localhost:8000/docs`.

### Search for a Game

`GET /steam/search?q=Portal`
Returns a list of matching Steam IDs and icons.

### Smart Auto-Add (Zero-Click Metadata)

`POST /games/search-and-add?q=The Witcher 3`
Finds the #1 match on Steam, fetches HLTB times, and saves the fully enriched record to the database in one step.

---

## Project Structure

```text
OverAchiever/
├── app/
│   ├── api/          # Route definitions (Games, Steam)
│   ├── services/     # Business logic & External API clients (HLTB, Steam)
│   ├── models.py     # SQLModel database schemas
│   ├── schemas.py    # Pydantic API schemas
│   ├── database.py   # SQLAlchemy session & engine config
│   └── main.py       # FastAPI application bootstrap
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── .env
```

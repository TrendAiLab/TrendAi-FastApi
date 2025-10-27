# TrendAI Backend

FastAPI backend for TrendAI news application.

## Setup

### Prerequisites

- Python 3.10+
- Virtual environment

### Installation

1. Clone the repository:
```bash
git clone https://github.com/TrendAiLab/TrendAi-FastApi.git
cd TrendAi-FastApi
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. Run the application:
```bash
python main.py
```

The API will be available at `http://localhost:8088`

## Project Structure

```
trendai_py/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── articles.py
│   │       │   ├── chat.py
│   │       │   ├── recommendations.py
│   │       │   └── search.py
│   │       └── router.py
│   ├── core/
│   │   └── dependencies.py
│   ├── database/
│   │   ├── milvus_client.py
│   │   └── supabase_client.py
│   ├── models/
│   │   └── schemas.py
│   ├── services/
│   │   ├── chat/
│   │   │   └── chat_service.py
│   │   ├── news/
│   │   │   ├── article_service.py
│   │   │   └── search_service.py
│   │   └── recommendations/
│   │       └── recommendation_service.py
│   └── utils/
│       └── embedding_utils.py
├── config/
│   └── settings.py
├── main.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
└── .env.example
```

## Environment Variables

Required environment variables:
- `MILVUS_URI`: Milvus cloud instance URI
- `MILVUS_TOKEN`: Milvus API token
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_ANON_KEY`: Supabase anonymous key
- `GROQ_API_KEY`: Groq API key

Optional:
- `FORCE_CPU`: Force CPU usage
- `GPU_MEMORY_FRACTION`: GPU memory fraction (0.0-1.0)
- `USE_MIXED_PRECISION`: Use mixed precision for inference

## API Endpoints

- `GET /health` - Health check
- `GET /api/v1/articles` - Get articles
- `POST /api/v1/search` - Semantic search
- `GET /api/v1/recommendations/{user_id}` - Personalized recommendations
- `POST /api/v1/chat` - Chat with AI assistant

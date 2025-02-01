# Clash of Clans API Cache Server

A FastAPI-based caching server for the Clash of Clans API that improves performance and reduces API calls by implementing an intelligent caching mechanism.

## Features

- Caches Clash of Clans API responses to reduce API calls
- Automatic background cache updates
- Simple REST API endpoints
- Docker support for easy deployment
- CORS enabled for frontend integration

## Prerequisites

- Python 3.12+
- Docker (optional)
- Clash of Clans API Key

## Setup

### Environment Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add your Clash of Clans API key to the `.env` file:
   ```
   API_KEY=your_api_key_here
   ```

### Local Development

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the server:
   ```bash
   python coc_server.py
   ```

The server will start at `http://localhost:8000`

### Docker Deployment

1. Build the Docker image:
   ```bash
   docker build -t coc-server .
   ```

2. Run with Docker Compose:
   ```bash
   docker-compose up -d
   ```

The server will be available at `http://localhost:8501`

## API Endpoints

### Get Clan Information

```
GET /clan/{clan_tag}
```

Retrieve information about a specific clan.

- `clan_tag`: The clan's tag (with or without #)

Example:
```bash
curl http://localhost:8000/clan/2LRJVVR9
```

### Get Current War Information

```
GET /clan/{clan_tag}/currentwar
```

Retrieve information about a clan's current war.

- `clan_tag`: The clan's tag (with or without #)

Example:
```bash
curl http://localhost:8000/clan/2LRJVVR9/currentwar
```

## Caching Mechanism

The server implements a file-based caching system with the following features:

- Cache data is stored in JSON files in the `cache` directory
- Cache entries expire after 12 hours
- Background tasks automatically update expired cache entries
- Cache files are named using normalized endpoint paths

## Error Handling

The server handles various error cases:

- Invalid clan tags
- API authentication errors
- Rate limiting
- Network issues

Errors are returned with appropriate HTTP status codes and descriptive messages.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
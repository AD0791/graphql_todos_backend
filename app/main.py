from fastapi import FastAPI

app = FastAPI(
    title="GraphQL Todo API",
    description="A production-ready GraphQL API with FastAPI and Strawberry",
    version="1.0.0"
)

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/")
async def root():
    return {
        "message": "GraphQL Todo API",
        "graphql_endpoint": "/graphql",
    }

    
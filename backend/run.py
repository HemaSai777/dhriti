import sys
import argparse
import uvicorn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="SAHAYA Backend Server")
    parser.add_argument("--host", default="127.0.0.1", help="Host address")
    parser.add_argument("--port", type=int, default=8000, help="Port number")
    parser.add_argument("--reload", action="store_true", help="Enable reload")
    parser.add_argument("--seed", action="store_true", help="Seed data and exit")
    args = parser.parse_args()

    if args.seed:
        from app.utils.seed_data import seed_demo_data
        seed_demo_data()
        sys.exit(0)

    print(f"Starting SAHAYA Backend on http://{args.host}:{args.port}")
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=args.reload)

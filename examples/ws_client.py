import asyncio
import websockets
import argparse

async def main(url: str, file_path: str, chunk_size: int):
    async with websockets.connect(url) as ws:
        with open(file_path, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                await ws.send(data)
                msg = await ws.recv()
                print(msg)
        await ws.send("EOS")
        msg = await ws.recv()
        print(msg)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="ws://localhost:8000/v1/audio/stream")
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--chunk", type=int, default=10240)
    parser.add_argument("--model", type=str, default=None)
    args = parser.parse_args()
    
    url = args.url
    if args.model:
        if "?" in url:
            url += f"&model={args.model}"
        else:
            url += f"?model={args.model}"
            
    asyncio.run(main(url, args.file, args.chunk))

import requests
import asyncio
import websockets
import json
import argparse

def test_rest_api(file_path, model_name="fun-asr-nano-2512"):
    url = "http://localhost:8800/v1/audio/transcriptions"
    print(f"Testing REST API with {file_path} using model {model_name}...")
    with open(file_path, "rb") as f:
        files = {"file": f}
        data = {"model": model_name, "response_format": "json"}
        response = requests.post(url, files=files, data=data)
        print("Status Code:", response.status_code)
        try:
            print("Response:", response.json())
        except:
            print("Response Text:", response.text)

async def test_websocket_api(file_path, model_name="fun-asr-nano-2512"):
    uri = f"ws://localhost:8800/v1/audio/stream?model={model_name}"
    print(f"Testing WebSocket API with {file_path} using model {model_name}...")
    async with websockets.connect(uri) as websocket:
        # Read file and send in chunks
        chunk_size = 1024 * 10 # 10KB chunks
        with open(file_path, "rb") as f:
            while True:
                data = f.read(chunk_size)
                if not data:
                    break
                # Send bytes
                await websocket.send(data) 
                
                response = await websocket.recv()
                print("Received:", response)
        
        # Send EOS
        await websocket.send("EOS")
        final_response = await websocket.recv()
        print("Final:", final_response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--file", type=str, required=True, help="Path to wav file")
    parser.add_argument("--mode", type=str, default="rest", choices=["rest", "ws"])
    parser.add_argument("--model", type=str, default="fun-asr-nano-2512", help="Model name")
    args = parser.parse_args()
    
    if args.mode == "rest":
        test_rest_api(args.file, args.model)
    else:
        asyncio.run(test_websocket_api(args.file, args.model))

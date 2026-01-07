import requests
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", type=str, default="http://localhost:8000/v1/audio/transcriptions")
    parser.add_argument("--file", type=str, required=True)
    parser.add_argument("--language", type=str, default="auto")
    parser.add_argument("--format", type=str, default="json")
    args = parser.parse_args()
    with open(args.file, "rb") as f:
        files = {"file": f}
        data = {"model": "fun-asr-nano-2512", "language": args.language, "response_format": args.format}
        r = requests.post(args.url, files=files, data=data)
        print(r.status_code)
        print(r.text)

if __name__ == "__main__":
    main()

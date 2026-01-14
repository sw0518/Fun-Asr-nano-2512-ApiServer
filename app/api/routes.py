from fastapi import APIRouter, UploadFile, File, Form, HTTPException, WebSocket, WebSocketDisconnect
from typing import Optional
from app.core.model_load import model_manager
from app.utils.audio import save_upload_file_tmp, cleanup_tmp_file
import shutil
import os
import json
import asyncio

router = APIRouter()

@router.post("/v1/audio/transcriptions")
async def transcribe_audio(
    file: UploadFile = File(...),
    model: Optional[str] = Form(None),
    language: Optional[str] = Form("auto"),
    response_format: Optional[str] = Form("json"),
    prompt: Optional[str] = Form(None),
):
    # Validate file
    if not file:
        raise HTTPException(status_code=400, detail="File is required")

    tmp_path = save_upload_file_tmp(file.file)
    
    try:
        # Transcribe
        text = await model_manager.transcribe(tmp_path, language=language, model_name=model)
        
        if response_format == "text":
            return text
        elif response_format == "verbose_json":
             return {
                "task": "transcribe",
                "language": language,
                "duration": 0, # Placeholder
                "text": text,
                "segments": [] # Placeholder
            }
        else: # json
            return {"text": text}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        cleanup_tmp_file(tmp_path)

@router.websocket("/v1/audio/stream")
async def websocket_endpoint(websocket: WebSocket, model: Optional[str] = None):
    await websocket.accept()
    cache = {}
    
    try:
        while True:
            message = await websocket.receive()
            
            if "bytes" in message:
                data = message["bytes"]
                # Process audio chunk
                result = await model_manager.transcribe_stream(data, cache=cache, is_final=False, model_name=model)
                
                # If result has text, send it
                if isinstance(result, dict) and "text" in result:
                    # FunASR streaming usually returns the current sentence or full text depending on mode
                    # We send back what we get
                    await websocket.send_text(json.dumps({"text": result["text"], "is_final": False}))
                    
            elif "text" in message:
                text_data = message["text"]
                # Check for "stop" or "eos" command
                if text_data == "EOS":
                     # Finalize
                    result = await model_manager.transcribe_stream(b"", cache=cache, is_final=True, model_name=model)
                    if isinstance(result, dict) and "text" in result:
                        await websocket.send_text(json.dumps({"text": result["text"], "is_final": True}))
                    cache = {} # Reset cache
                else:
                    # Maybe config update
                    pass

    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

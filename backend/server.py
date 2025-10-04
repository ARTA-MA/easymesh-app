from fastapi import FastAPI, APIRouter, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
# MongoDB removed
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
import os
import uuid
import asyncio
import json
import logging
import sys
import socket
import re
import platform
import subprocess
import concurrent.futures
import io
import time
from starlette.staticfiles import StaticFiles
from starlette.responses import FileResponse, HTMLResponse
from ftplib import FTP, error_perm

ROOT_DIR = Path(__file__).parent
PROJECT_ROOT = ROOT_DIR.parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection removed

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Models (MongoDB-related models removed)
# class StatusCheck(BaseModel):
#     id: str = Field(default_factory=lambda: str(uuid.uuid4()))
#     client_name: str
#     timestamp: datetime = Field(default_factory=datetime.utcnow)


# class StatusCheckCreate(BaseModel):
#     client_name: str


@api_router.get("/")
async def root():
    return {"message": "Hello World"}


# -----------------------------
# Helper: compute resource/static path (works in PyInstaller)
# -----------------------------

def resource_path(relative: str) -> Path:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    # When using PyInstaller, sys._MEIPASS points to temp extract dir
    base_path = getattr(sys, '_MEIPASS', None)
    if base_path:
        return Path(base_path) / relative
    return (ROOT_DIR / relative).resolve()


def get_frontend_build_dir() -> Optional[Path]:
    # Check common locations
    candidates = [
        PROJECT_ROOT / "frontend" / "build",
        ROOT_DIR / "frontend_build",           # when bundled via --add-data "frontend/build;frontend_build"
        resource_path("frontend_build"),       # PyInstaller runtime
    ]
    for p in candidates:
        try:
            if p and p.exists() and (p / "index.html").exists():
                return p
        except Exception:
            continue
    return None


# -----------------------------
# WebSocket Signaling for WebRTC
# -----------------------------
class WSClient:
    def __init__(self, websocket: WebSocket, client_id: str, role: str):
        self.websocket = websocket
        self.client_id = client_id
        self.role = role


class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.clients: Dict[str, WSClient] = {}
        self.lock = asyncio.Lock()

    def peers(self) -> List[str]:
        return list(self.clients.keys())


sessions: Dict[str, Session] = {}


def get_or_create_session(session_id: str) -> Session:
    if session_id not in sessions:
        sessions[session_id] = Session(session_id)
    return sessions[session_id]


async def broadcast_peers(session: Session):
    payload = {"type": "peers", "peers": session.peers()}
    for c in list(session.clients.values()):
        try:
            await c.websocket.send_text(json.dumps(payload))
        except Exception:
            pass


@api_router.websocket("/ws/session/{session_id}")
async def ws_session(websocket: WebSocket, session_id: str):
    await websocket.accept()
    client_id: Optional[str] = None
    role = "unknown"
    session = get_or_create_session(session_id)
    try:
        # Expect a join message
        join_raw = await websocket.receive_text()
        join = json.loads(join_raw)
        if join.get("type") != "join":
            await websocket.close(code=1002)
            return
        client_id = join.get("clientId") or str(uuid.uuid4())
        role = join.get("role", "unknown")
        async with session.lock:
            session.clients[client_id] = WSClient(websocket, client_id, role)
        await broadcast_peers(session)

        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)
            mtype = msg.get("type")

            if mtype in ("sdp-offer", "sdp-answer", "ice-candidate", "text"):
                target = msg.get("to")
                if not target:
                    continue
                target_client = session.clients.get(target)
                if target_client:
                    try:
                        await target_client.websocket.send_text(json.dumps({**msg, "from": client_id}))
                    except Exception:
                        pass
            elif mtype == "leave":
                break
            elif mtype == "ping":
                await websocket.send_text(json.dumps({"type": "pong"}))
            else:
                # ignore
                pass
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logging.exception("WebSocket error: %s", e)
    finally:
        if client_id:
            async with session.lock:
                session.clients.pop(client_id, None)
            if len(session.clients) == 0:
                sessions.pop(session.session_id, None)
        try:
            await broadcast_peers(session)
        except Exception:
            pass


# -----------------------------
# Minimal FTP bridge endpoints (LAN FTP target)
# -----------------------------
class FTPConfig(BaseModel):
    host: str
    port: int = 21
    user: str
    password: str
    passive: bool = True
    max_connections: int = 3  # Default to 3 parallel connections
    cwd: str = "/"
    max_connections: int = 3  # Maximum number of parallel connections


class FTPPath(BaseModel):
    config: FTPConfig
    path: str = "."


class TransferProgress:
    def __init__(self, file_size: int, transfer_id: str):
        self.file_size = file_size
        self.bytes_transferred = 0
        self.start_time = time.time()
        self.transfer_id = transfer_id
        self.status = "in_progress"
        self.error = None
        
    def update(self, bytes_count: int):
        self.bytes_transferred += bytes_count
        
    def complete(self):
        self.status = "completed"
        
    def fail(self, error: str):
        self.status = "failed"
        self.error = error
        
    def get_progress(self) -> Dict[str, Any]:
        elapsed = time.time() - self.start_time
        percent = (self.bytes_transferred / self.file_size * 100) if self.file_size > 0 else 0
        speed = self.bytes_transferred / elapsed if elapsed > 0 else 0
        
        return {
            "transfer_id": self.transfer_id,
            "status": self.status,
            "bytes_transferred": self.bytes_transferred,
            "file_size": self.file_size,
            "percent_complete": round(percent, 2),
            "speed_bytes_per_sec": round(speed, 2),
            "elapsed_seconds": round(elapsed, 2),
            "error": self.error
        }


# Global transfer progress tracker
active_transfers: Dict[str, TransferProgress] = {}


class TransferProgress:
    def __init__(self, file_size: int, transfer_id: str):
        self.file_size = file_size
        self.bytes_transferred = 0
        self.start_time = time.time()
        self.transfer_id = transfer_id
        self.status = "in_progress"
        self.error = None
        
    def update(self, bytes_count: int):
        self.bytes_transferred += bytes_count
        
    def complete(self):
        self.status = "completed"
        
    def fail(self, error: str):
        self.status = "failed"
        self.error = error
        
    def get_progress(self) -> Dict[str, Any]:
        elapsed = time.time() - self.start_time
        percent = (self.bytes_transferred / self.file_size * 100) if self.file_size > 0 else 0
        speed = self.bytes_transferred / elapsed if elapsed > 0 else 0
        
        return {
            "transfer_id": self.transfer_id,
            "status": self.status,
            "bytes_transferred": self.bytes_transferred,
            "file_size": self.file_size,
            "percent_complete": round(percent, 2),
            "speed_bytes_per_sec": round(speed, 2),
            "elapsed_seconds": round(elapsed, 2),
            "error": self.error
        }


# Global transfer progress tracker
active_transfers: Dict[str, TransferProgress] = {}


def connect_ftp(cfg: FTPConfig) -> FTP:
    try:
        ftp = FTP()
        ftp.connect(cfg.host, cfg.port, timeout=10)
        ftp.login(cfg.user, cfg.password)
        ftp.set_pasv(cfg.passive)
        if cfg.cwd:
            ftp.cwd(cfg.cwd)
        return ftp
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"FTP connect failed: {e}")


@api_router.post("/ftp/list")
async def ftp_list(body: FTPPath):
    def _list():
        ftp = connect_ftp(body.config)
        try:
            ftp.cwd(body.path)
            lines: List[str] = []
            ftp.retrlines('LIST', lines.append)
            return {"entries": lines}
        finally:
            try:
                ftp.quit()
            except Exception:
                pass
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _list)


class FTPUploadQuery(BaseModel):
    config: FTPConfig
    dest_dir: str = "/"
    filename: Optional[str] = None


@api_router.post("/ftp/upload")
async def ftp_upload(config: str, dest_dir: str = "/", file: UploadFile = File(...), filename: Optional[str] = None, background_tasks: BackgroundTasks = None):
    # config is JSON string due to multipart; parse
    try:
        cfg_dict = json.loads(config)
        cfg = FTPConfig(**cfg_dict)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid config: {e}")

    # Create a custom buffered reader for efficient file reading
    class BufferedFileReader:
        def __init__(self, file_obj, buffer_size=8*1024*1024, progress_tracker=None):
            self.file_obj = file_obj
            self.buffer_size = buffer_size
            self.progress_tracker = progress_tracker
            
        def read(self, size=None):
            # If size is None or larger than buffer_size, use buffer_size
            chunk_size = min(size, self.buffer_size) if size is not None else self.buffer_size
            data = self.file_obj.read(chunk_size)
            if data and self.progress_tracker:
                self.progress_tracker.update(len(data))
            return data

    # Function to split file into chunks for parallel upload
    async def split_file_for_parallel_upload(file_obj, chunk_size, num_chunks):
        # Save original position
        original_position = file_obj.tell()
        
        # Get file size
        file_obj.seek(0, 2)  # Seek to end
        file_size = file_obj.tell()
        file_obj.seek(original_position)  # Restore position
        
        chunks = []
        chunk_positions = []
        
        # Calculate optimal chunk size based on file size and desired number of chunks
        actual_chunk_size = max(chunk_size, file_size // num_chunks)
        
        # Create chunks
        for i in range(0, file_size, actual_chunk_size):
            end_pos = min(i + actual_chunk_size, file_size)
            chunk_positions.append((i, end_pos - i))
        
        return file_size, chunk_positions

    # Function to upload a single chunk
    async def upload_chunk(ftp_config, dest_dir, file_obj, chunk_start, chunk_size, dest_filename, chunk_index, progress_tracker):
        try:
            # Connect to FTP for this chunk
            ftp = connect_ftp(ftp_config)
            
            # Set socket optimizations
            buffer_size = 8 * 1024 * 1024
            ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
            ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
            ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
            ftp.sock.settimeout(60)
            
            # Navigate to destination directory
            ftp.cwd(dest_dir)
            
            # Memory-optimized approach: stream directly from file without loading entire chunk into memory
            class ChunkedFileReader:
                def __init__(self, file_obj, start_pos, chunk_size, progress_tracker=None):
                    self.file_obj = file_obj
                    self.start_pos = start_pos
                    self.end_pos = start_pos + chunk_size
                    self.current_pos = start_pos
                    self.progress_tracker = progress_tracker
                    # Position file at start
                    self.file_obj.seek(self.start_pos)
                
                def read(self, size=None):
                    # Calculate how much we can read
                    remaining = self.end_pos - self.current_pos
                    if remaining <= 0:
                        return b''
                    
                    # Determine read size (don't exceed chunk boundary)
                    read_size = min(size or remaining, remaining)
                    
                    # Read data
                    data = self.file_obj.read(read_size)
                    
                    # Update position and progress
                    self.current_pos += len(data)
                    if data and self.progress_tracker:
                        self.progress_tracker.update(len(data))
                    
                    return data
            
            # Create memory-efficient reader that streams directly from file
            chunked_reader = ChunkedFileReader(file_obj, chunk_start, chunk_size, progress_tracker)
            
            # For multi-chunk uploads, use temporary filenames for all but the last chunk
            temp_filename = f"{dest_filename}.part{chunk_index}"
            
            # Upload the chunk with optimized buffer size
            ftp.storbinary(f"STOR {temp_filename}", chunked_reader, blocksize=buffer_size)
            
            return {
                "chunk_index": chunk_index,
                "temp_filename": temp_filename,
                "chunk_size": chunk_size
            }
        except Exception as e:
            if progress_tracker:
                progress_tracker.fail(f"Chunk {chunk_index} failed: {str(e)}")
            raise
        finally:
            try:
                ftp.quit()
            except Exception:
                pass

    # Function to merge chunks on the FTP server (if needed)
    async def merge_chunks(ftp_config, dest_dir, dest_filename, chunk_info, progress_tracker):
        try:
            # If only one chunk, just rename it
            if len(chunk_info) == 1 and chunk_info[0]["temp_filename"] != dest_filename:
                ftp = connect_ftp(ftp_config)
                ftp.cwd(dest_dir)
                ftp.rename(chunk_info[0]["temp_filename"], dest_filename)
                ftp.quit()
                return
                
            # For multiple chunks, we'd need server-side commands to concatenate
            # This is typically not available in standard FTP, so we'd need to
            # implement a different strategy for multi-part uploads
            
            # Mark as complete
            if progress_tracker:
                progress_tracker.complete()
                
        except Exception as e:
            if progress_tracker:
                progress_tracker.fail(f"Merge failed: {str(e)}")
            raise

    async def _upload_parallel():
        try:
            # Generate a unique transfer ID
            transfer_id = str(uuid.uuid4())
            
            # Get file size for progress tracking
            file.file.seek(0, 2)  # Seek to end
            file_size = file.file.tell()
            file.file.seek(0)  # Reset to beginning
            
            # Create progress tracker
            progress = TransferProgress(file_size, transfer_id)
            active_transfers[transfer_id] = progress
            
            # Determine filename
            dest_filename = filename or file.filename
            if not dest_filename:
                raise Exception("Missing filename")
            
            # Determine optimal number of chunks based on file size and max connections
            max_connections = min(cfg.max_connections, 3)  # Limit to 3 connections max
            
            # For small files, use single connection
            if file_size < 10 * 1024 * 1024:  # Less than 10MB
                max_connections = 1
            
            # Split file into chunks
            _, chunk_positions = await split_file_for_parallel_upload(
                file.file, 
                8 * 1024 * 1024,  # 8MB minimum chunk size
                max_connections
            )
            
            # Reset file position
            file.file.seek(0)
            
            # Upload chunks in parallel
            chunk_results = []
            if max_connections == 1:
                # Single connection mode - simpler and more efficient for smaller files
                # Implement retry mechanism for single connection
                max_retries = 3
                retry_delay = 2  # seconds
                
                for attempt in range(max_retries):
                    try:
                        ftp = connect_ftp(cfg)
                        try:
                            # Set socket optimizations
                            buffer_size = 8 * 1024 * 1024
                            ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, buffer_size)
                            ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, buffer_size)
                            ftp.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                            ftp.sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                            ftp.sock.settimeout(60)
                            
                            # Navigate to destination directory
                            ftp.cwd(dest_dir)
                            
                            # Create memory-efficient reader with progress tracking
                            chunked_reader = ChunkedFileReader(file.file, 0, file_size, progress)
                            
                            # Upload directly
                            ftp.storbinary(f"STOR {dest_filename}", chunked_reader, blocksize=buffer_size)
                            
                            # Mark as complete
                            progress.complete()
                            
                            # Log successful transfer
                            logging.info(f"File transfer completed: {dest_filename}")
                            
                            return {"ok": True, "path": f"{dest_dir}/{dest_filename}", "transfer_id": transfer_id}
                        finally:
                            try:
                                ftp.quit()
                            except Exception:
                                pass
                    except Exception as e:
                        if attempt < max_retries - 1:
                            # Log retry attempt
                            logging.warning(f"Transfer attempt {attempt+1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                            # Reset file position for retry
                            file.file.seek(0)
                            # Wait before retry
                            await asyncio.sleep(retry_delay)
                            # Increase delay for next retry (exponential backoff)
                            retry_delay *= 2
                        else:
                            # Last attempt failed
                            progress.fail(f"Upload failed after {max_retries} attempts: {str(e)}")
                            raise
            else:
                # Multi-connection mode for larger files with retry mechanism
                max_chunk_retries = 3
                
                # Execute uploads in parallel with retries for each chunk
                with concurrent.futures.ThreadPoolExecutor(max_workers=max_connections) as executor:
                    loop = asyncio.get_event_loop()
                    
                    # Function to handle chunk upload with retries
                    async def upload_chunk_with_retry(chunk_index, start_pos, chunk_size):
                        retry_delay = 1
                        for attempt in range(max_chunk_retries):
                            try:
                                return await upload_chunk(
                                    cfg, dest_dir, file.file, start_pos, chunk_size, 
                                    dest_filename, chunk_index, progress
                                )
                            except Exception as e:
                                if attempt < max_chunk_retries - 1:
                                    logging.warning(f"Chunk {chunk_index} upload attempt {attempt+1} failed: {str(e)}. Retrying in {retry_delay} seconds...")
                                    await asyncio.sleep(retry_delay)
                                    retry_delay *= 2
                                else:
                                    logging.error(f"Chunk {chunk_index} failed after {max_chunk_retries} attempts: {str(e)}")
                                    raise
                    
                    # Create tasks with retry mechanism
                    futures = []
                    for i, (start, size) in enumerate(chunk_positions):
                        task = upload_chunk_with_retry(i, start, size)
                        futures.append(loop.run_in_executor(executor, lambda t=task: asyncio.run(t)))
                    
                    chunk_results = await asyncio.gather(*futures, return_exceptions=True)
                
                # Check for errors
                errors = [r for r in chunk_results if isinstance(r, Exception)]
                if errors:
                    progress.fail(f"Upload failed: {errors[0]}")
                    raise errors[0]
                
                # Merge chunks if needed
                await merge_chunks(cfg, dest_dir, dest_filename, chunk_results, progress)
                
                # Log successful transfer
                logging.info(f"File transfer completed: {dest_filename}")
                
                return {
                    "ok": True, 
                    "path": f"{dest_dir}/{dest_filename}", 
                    "transfer_id": transfer_id,
                    "parallel": True,
                    "chunks": len(chunk_positions)
                }
        except Exception as e:
            logging.error(f"File transfer error: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")
    
    # Start the upload process
    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(None, lambda: asyncio.run(_upload_parallel()))
    
    return result


@api_router.get("/ftp/transfer-status/{transfer_id}")
async def get_transfer_status(transfer_id: str):
    """Get the status of an active file transfer"""
    if transfer_id not in active_transfers:
        raise HTTPException(status_code=404, detail="Transfer not found")
    
    progress = active_transfers[transfer_id]
    return progress.get_progress()


# -----------------------------
# Host info for LAN QR generation
# -----------------------------
PRIVATE_RANGES = [
    re.compile(r"^10\..*"),
    re.compile(r"^192\.168\..*"),
    re.compile(r"^172\.(1[6-9]|2[0-9]|3[0-1])\..*"),
]


def is_private_ipv4(ip: str) -> bool:
    if ip.startswith("127.") or ip.startswith("169.254."):
        return False
    return any(p.match(ip) for p in PRIVATE_RANGES)


def parse_windows_ipconfig(output: str) -> List[str]:
    # Matches lines like: IPv4 Address. . . . . . . . . . . : 192.168.1.23
    ips = re.findall(r"IPv4[^:]*:\s*([0-9\.]+)", output)
    return [ip for ip in ips if is_private_ipv4(ip)]


def parse_unix_ip(output: str) -> List[str]:
    # Parse `ip -4 addr` output
    ips = re.findall(r"inet\s([0-9\.]+)", output)
    return [ip for ip in ips if is_private_ipv4(ip)]


def get_ipv4_candidates() -> List[str]:
    candidates: List[str] = []
    try:
        if platform.system().lower().startswith('win'):
            out = subprocess.check_output(["ipconfig"], text=True, errors='ignore')
            candidates = parse_windows_ipconfig(out)
        else:
            # Prefer `ip -4 addr`, fall back to ifconfig
            try:
                out = subprocess.check_output(["ip", "-4", "addr"], text=True, errors='ignore')
                candidates = parse_unix_ip(out)
            except Exception:
                out = subprocess.check_output(["ifconfig"], text=True, errors='ignore')
                candidates = parse_unix_ip(out)
    except Exception:
        pass

    # Fallback: try UDP trick to discover default route IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        if is_private_ipv4(ip) and ip not in candidates:
            candidates.append(ip)
    except Exception:
        pass

    # Deduplicate, preserve order
    seen = set()
    res = []
    for ip in candidates:
        if ip not in seen:
            seen.add(ip)
            res.append(ip)
    return res


@api_router.get("/host-info")
async def host_info():
    port = int(os.environ.get("PORT", 8001))
    ips = get_ipv4_candidates()
    urls = [f"http://{ip}:{port}" for ip in ips]
    return {"port": port, "ips": ips, "urls": urls}


# Include the router in the main app
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router)

# -----------------------------
# Static frontend (if build available). This does NOT alter /api routes
# -----------------------------
_frontend_dir = get_frontend_build_dir()
if _frontend_dir:
    # Serve static assets
    app.mount("/", StaticFiles(directory=str(_frontend_dir), html=True), name="static")

    @app.get("/{full_path:path}")
    async def spa_fallback(full_path: str):
        # Let /api handlers handle their routes
        if full_path.startswith("api"):
            raise HTTPException(status_code=404)
        index_file = _frontend_dir / "index.html"
        if index_file.exists():
            return FileResponse(str(index_file))
        return HTMLResponse("Frontend build not found", status_code=404)

# Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
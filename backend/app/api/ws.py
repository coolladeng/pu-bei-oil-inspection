"""WebSocket API"""
import json
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from app.websocket_manager import manager
from app.security import decode_access_token

router = APIRouter()


@router.websocket("/screen")
async def screen_websocket(
    websocket: WebSocket,
    token: str = Query(None),
):
    """大屏监控 WebSocket — 实时推送巡检进度和告警"""
    if token:
        try:
            decode_access_token(token)
        except Exception:
            await websocket.close(code=4001, reason="认证失败")
            return
    await manager.connect("screen", websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect("screen", websocket)
    except Exception:
        manager.disconnect("screen", websocket)


@router.websocket("/alert")
async def alert_websocket(
    websocket: WebSocket,
    token: str = Query(None),
):
    """告警推送 WebSocket"""
    if token:
        try:
            decode_access_token(token)
        except Exception:
            await websocket.close(code=4001, reason="认证失败")
            return
    await manager.connect("alert", websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect("alert", websocket)
    except Exception:
        manager.disconnect("alert", websocket)
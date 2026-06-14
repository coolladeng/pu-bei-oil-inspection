"""WebSocket 连接管理器"""
import asyncio
import json
from typing import Dict, Set
from fastapi import WebSocket


class ConnectionManager:
    """WebSocket 连接管理器 — 单例模式"""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {
            "screen": set(),     # 大屏监控客户端
            "alert": set(),      # 告警推送客户端
        }

    async def connect(self, channel: str, websocket: WebSocket):
        await websocket.accept()
        if channel not in self._connections:
            self._connections[channel] = set()
        self._connections[channel].add(websocket)

    def disconnect(self, channel: str, websocket: WebSocket):
        if channel in self._connections:
            self._connections[channel].discard(websocket)

    async def broadcast(self, channel: str, message: dict):
        """向指定频道的所有客户端广播消息"""
        if channel not in self._connections:
            return
        dead = set()
        for ws in self._connections[channel]:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        self._connections[channel] -= dead

    async def broadcast_alert(self, alert_data: dict):
        """广播实时告警"""
        await self.broadcast("alert", {"type": "alert", "data": alert_data})
        await self.broadcast("screen", {"type": "alert", "data": alert_data})

    async def broadcast_progress(self, progress_data: dict):
        """广播巡检进度更新"""
        await self.broadcast("screen", {"type": "progress", "data": progress_data})

    async def broadcast_stats(self, stats_data: dict):
        """广播统计数据更新"""
        await self.broadcast("screen", {"type": "stats", "data": stats_data})


# 全局单例
manager = ConnectionManager()
"""Stub adapter for future real sensor websocket ingestion."""

from __future__ import annotations


class WebSocketIngestProvider:
    def read_all_nodes(self) -> dict:
        raise NotImplementedError("WebSocket ingest provider is a P5 stub.")

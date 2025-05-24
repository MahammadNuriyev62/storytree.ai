"""
A one-liner message bus that any part of your code can import.

producer -> EventBus.publish(event_dict)
consumer -> await EventBus.subscribe()
"""
import asyncio, json, logging

log = logging.getLogger(__name__)
_queue: asyncio.Queue = asyncio.Queue()

class EventBus:
    @staticmethod
    async def subscribe():            # coroutine for the web layer
        return await _queue.get()

    @staticmethod
    def publish(event: dict):         # plain func for your generator
        try:
            _queue.put_nowait(event)
        except asyncio.QueueFull:
            log.warning("event dropped: %s", event)

from typing import Protocol, Any

class EventBus(Protocol):
    async def publish_all(self, events: list[Any]):
        ...

    async def publish(self, event: Any):
        ...
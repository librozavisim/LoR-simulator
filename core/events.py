import heapq
from collections import defaultdict


class EventManager:
    def __init__(self):
        self.listeners = defaultdict(list)

    def subscribe(self, event_type, callback, priority=100):
        # priority: меньше = раньше срабатывает
        heapq.heappush(self.listeners[event_type], (priority, callback))
        # Логируем подписку (полезно для отладки инициализации)
        # logger.log(f"Subscribed to '{event_type}' with priority {priority}", LogLevel.VERBOSE, "EventSystem")

    def emit(self, event_type, context):
        if event_type in self.listeners:
            # Логируем факт срабатывания события (VERBOSE)
            # logger.log(f"⚡ Emitting event: '{event_type}'", LogLevel.VERBOSE, "EventSystem")

            # Создаем копию списка, чтобы избежать проблем если во время итерации кто-то отпишется
            # (хотя heapq неудобно копировать, здесь упростим перебором)
            sorted_listeners = sorted(self.listeners[event_type], key=lambda x: x[0])
            for _, callback in sorted_listeners:
                callback(context)
        return context
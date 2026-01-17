from typing import Dict, TYPE_CHECKING
from core.logging import logger, LogLevel

if TYPE_CHECKING:
    pass


class UnitStatusMixin:
    def _ensure_status_storage(self):
        if not hasattr(self, "_status_effects"): self._status_effects = {}
        if not hasattr(self, "delayed_queue"): self.delayed_queue = []

    @property
    def statuses(self) -> Dict[str, int]:
        self._ensure_status_storage()
        summary = {}
        for name, instances in self._status_effects.items():
            total = sum(i["amount"] for i in instances)
            if total > 0:
                summary[name] = total
        return summary

    def add_status(self, name: str, amount: int, duration: int = 1, delay: int = 0, trigger_events: bool = True):
        self._ensure_status_storage()
        if amount <= 0: return False, None

        if hasattr(self, "iter_mechanics"):
            for mech in self.iter_mechanics():
                if hasattr(mech, "on_before_status_add"):
                    res = mech.on_before_status_add(self, name, amount)

                    # Обработка результата (bool или tuple)
                    if isinstance(res, tuple):
                        allowed, msg = res
                    else:
                        allowed, msg = res, None

                    if not allowed:
                        # Логируем блокировку (VERBOSE)
                        logger.log(f"🚫 {self.name}: Status {name} blocked ({msg})", LogLevel.VERBOSE, "Status")
                        return False, msg
        # =========================================================================

        if delay > 0:
            self.delayed_queue.append({
                "name": name, "amount": amount, "duration": duration, "delay": delay
            })
            logger.log(f"⏰ {self.name}: {name} delayed for {delay} turns", LogLevel.NORMAL, "Status")
            return True, "Delayed"

        if name not in self._status_effects:
            self._status_effects[name] = []

        POOL_STATUSES = ["smoke", "charge", "satiety", "tremor", "self_control", "poise", "adaptation"]

        if name in POOL_STATUSES and self._status_effects[name]:
            # Если статус уже есть, просто увеличиваем количество в первом слоте
            self._status_effects[name][0]["amount"] += amount
            # Обновляем длительность (берем максимум)
            self._status_effects[name][0]["duration"] = max(self._status_effects[name][0]["duration"], duration)
        else:
            # Обычное поведение: добавляем новый отдельный стак
            self._status_effects[name].append({"amount": amount, "duration": duration})

        # Логируем наложение (NORMAL)
        logger.log(f"🧪 {self.name}: +{amount} {name} ({duration}t)", LogLevel.NORMAL, "Status")

        # === [ОПТИМИЗАЦИЯ] 2. ХУК: on_status_applied ===
        if trigger_events and hasattr(self, "trigger_mechanics"):
            # Вызывает метод on_status_applied у всех активных механик
            self.trigger_mechanics("on_status_applied", self, name, amount, duration=duration)
        # ==============================================

        return True, None

    def get_status(self, name: str) -> int:
        self._ensure_status_storage()
        if name not in self._status_effects: return 0
        return sum(i["amount"] for i in self._status_effects[name])

    def remove_status(self, name: str, amount: int = None):
        self._ensure_status_storage()
        if name not in self._status_effects: return

        current_val = self.get_status(name)

        if amount is None:
            del self._status_effects[name]
            logger.log(f"🧹 {self.name}: Cleared all {name} ({current_val})", LogLevel.NORMAL, "Status")
            return

        items = sorted(self._status_effects[name], key=lambda x: x["duration"])
        rem = amount
        new_items = []

        for item in items:
            if rem <= 0:
                new_items.append(item)
                continue
            if item["amount"] > rem:
                item["amount"] -= rem
                rem = 0
                new_items.append(item)
            else:
                rem -= item["amount"]

        if not new_items:
            del self._status_effects[name]
        else:
            self._status_effects[name] = new_items

        # Логируем фактическое снятие
        removed = current_val - self.get_status(name)
        if removed > 0:
            logger.log(f"🧹 {self.name}: Removed {removed} {name}", LogLevel.NORMAL, "Status")
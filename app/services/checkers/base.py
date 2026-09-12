from abc import ABC, abstractmethod

from app.models.component import ComponentHealth


class HealthChecker(ABC):

    @abstractmethod
    async def check(
        self,
    ) -> list[ComponentHealth]:
        raise NotImplementedError

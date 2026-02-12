import logging
from datetime import datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.tracking.domain.entities import Coordinates, Tracking, User, UserStatus
from src.tracking.domain.protocols import ILocationRepository, IUserRepository
from src.tracking.infrastructure.database.models import TrackingModel, UserModel, UserStatusModel

logger = logging.getLogger(__name__)


class TrackingRepo(ILocationRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, entity: Tracking) -> None:
        logger.debug(f"Adding tracking for user {entity.user_id}")

        model = TrackingModel(
            user_id=entity.user_id,
            lat=entity.location.latitude,
            lon=entity.location.longitude,
            recorded_at=entity.recorded_at,
        )
        self.session.add(model)

    async def get_last_tracking(self, user_id: str) -> Tracking | None:
        logger.debug(f"Fetching last tracking for user {user_id}")

        stmt = (
            select(TrackingModel)
            .where(TrackingModel.user_id == user_id)
            .order_by(desc(TrackingModel.recorded_at))
            .limit(1)
        )
        result = await self.session.execute(stmt)
        model = result.scalars().first()

        if not model:
            logger.debug(f"No previous tracking found for user {user_id}")
            return None

        return Tracking(
            user_id=model.user_id,
            location=Coordinates(model.lat, model.lon),
            recorded_at=model.recorded_at,
        )

    async def commit(self) -> None:
        await self.session.commit()
        logger.debug("Transaction committed")

    async def get_locations(self, user_id: str) -> list[Tracking]:
        stmt = (
            select(TrackingModel)
            .where(TrackingModel.user_id == user_id)
            .order_by(desc(TrackingModel.recorded_at))
            .limit(5)
        )
        result = await self.session.execute(stmt)
        models = result.scalars().all()

        entities = []
        for model in models:
            entities.append(
                Tracking(
                    user_id=model.user_id, location=Coordinates(model.lat, model.lon), recorded_at=model.recorded_at
                )
            )

        return entities


class UserRepo(IUserRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: str) -> User | None:
        logger.debug(f"Fetching user with user_id={user_id}")

        stmt = select(UserModel).where(UserModel.user_id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            logger.debug(f"User {user_id} not found")
            return None

        return User(user_id=model.user_id, username=model.username, link=model.link)

    async def create(self, user: User) -> User:
        logger.info(f"Creating new user: {user.user_id} ({user.username})")

        model = UserModel(user_id=user.user_id, username=user.username, link=user.link)
        self.session.add(model)
        return user

    async def commit(self) -> None:
        await self.session.commit()
        logger.debug("User transaction committed")


class UserStatusRepo:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_user_id(self, user_id: str) -> UserStatus | None:
        stmt = select(UserStatusModel).where(UserStatusModel.user_id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            return None

        return UserStatus(user_id=model.user_id, last_sent=model.last_sent)

    async def update_last_sent(self, user_id: str, sent_at: datetime) -> None:
        stmt = select(UserStatusModel).where(UserStatusModel.user_id == user_id)
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        if not model:
            new_model = UserStatusModel(user_id=user_id, last_sent=sent_at)
            self.session.add(new_model)
        else:
            model.last_sent = sent_at
            self.session.add(model)

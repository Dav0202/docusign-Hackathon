import uuid
from typing import Optional

from sqlalchemy import or_, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.db_crud import DBRepo
from app.core.database import User, Events
from app.core.exceptions import ResourceNotExists, UserNotAllowed


class EventDBService:

    def __init__(self) -> None:
        self._repo = DBRepo()

    async def get_event(
        self,
        event_id,        
        session: AsyncSession,

    ) -> Events:
        return await self._repo.get_id(
            session,
            event_id,
            table_model=Events,
        )        

    async def get_events(
        self,
        session: AsyncSession,

    ) -> list[Events]:
        return await self._repo.get_multi(
            session,
            table_model=Events,
        )

    async def my_get_events(
        self,
        session: AsyncSession,
        *,
        created_by_id: uuid.UUID,

    ) -> list[Events]:
        return await self._repo.get_multi(
            session,
            table_model=Events,
            query_filter=Events.created_by_id == created_by_id,
        )
    
    async def add_events(
        self,
        session: AsyncSession,
        *,
        events_in
    ) -> Events:          
          try:
               return await self._repo.create(session, obj_to_create=events_in)
          except IntegrityError:
              raise IntegrityError

    async def update_events(
        self,
        session: AsyncSession,
        *,
        updated_events
    ) -> Events:
        events_to_update: Optional[Events] = await self._repo.get(
            session,
            table_model=Events,
            query_filter=Events.id == updated_events.id
        )
        if not events_to_update:
            raise ResourceNotExists(resource='events')
        if not events_to_update.created_by_id == updated_events.created_by_id:
            raise UserNotAllowed('a user can not delete a category that was not created by them')

        try:
            events_updated_obj: Optional[Events] = await self._repo.update(
                    session,
                    updated_obj=updated_events,
                    db_obj_to_update=events_to_update
                )
            if events_updated_obj:
                  return events_updated_obj
            pass #does not exist
        except IntegrityError:
            pass #raise integrity error            

    async def delete_events(
        self,
        session: AsyncSession,
        *,
        id_to_delete: int,
        created_by_id: uuid.UUID
    ) -> None:
        events_to_delete: Optional[Events] = await self._repo.get(
            session,
            table_model=Events,
            query_filter=Events.id == id_to_delete
        )
        if not events_to_delete:
            raise ResourceNotExists(resource='events')
        if events_to_delete.created_by_id != created_by_id:
            raise UserNotAllowed('a user can not delete a category that was not created by him')
        await self._repo.delete(session, table_model=Events, id_to_delete=id_to_delete)


event_db_service = EventDBService()

from typing import Annotated
from app.core.exceptions import exception_handler
from fastapi import APIRouter, Depends, status
from sqlalchemy import Executable
from app.core.database import Events_Registration, Events, User
from app.core.database import SessionDep
from app.routes.users.users import current_active_user
from sqlalchemy.future import select
from app.core import schema
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_session
from fastapi import Depends
from app.services.event_service import event_db_service
from app.core.errors import get_open_api_response

router = APIRouter(tags=["Events"])

@router.get(
    "/events/{event_id}", status_code=status.HTTP_200_OK, response_model=schema.EventsRead
)
async def get_events(
        event_id: str,   
        current_user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)) :
        return await event_db_service.get_event(
            event_id, db
        )  

@router.get(
    "/events", status_code=status.HTTP_200_OK, response_model=list[schema.EventsRead]
)
async def get_events(
        current_user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)) :
        return await event_db_service.get_events(
            db
        )        

@router.get(
    "/my-events", status_code=status.HTTP_200_OK, response_model=list[schema.EventsRead]
)
async def get_my_events(
        current_user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)) :
        return await event_db_service.my_get_events(
            db,
            created_by_id=current_user.id,
        )  

@router.post(
    "/my-events", status_code=status.HTTP_201_CREATED, response_model=schema.Events
)
@exception_handler
async def post_events(
    data: schema.Events,
    current_user: Annotated[User, Depends(current_active_user)],
    db: AsyncSession = Depends(get_async_session))-> Events:        
        event_in = schema.EventInDB(
            name = data.name,
            description = data.description,
            date =  data.date,
            location = data.location,
            capacity = data.capacity,             
            created_by_id=current_user.id
        )             
        return await event_db_service.add_events(db, events_in=event_in)
             

@router.put(
    '/my-events/{event_id}',
    response_model=schema.Events,
    responses={
        status.HTTP_404_NOT_FOUND: get_open_api_response(
            {'Trying to update non existing event': 'Event does not exists'}
        )
    }
)
@exception_handler
async def update_todo(
    event_id: str,
    current_user: Annotated[User, Depends(current_active_user)],    
    data: schema.Events,
    db: AsyncSession = Depends(get_async_session),
) -> Events:
    updated_event = schema.UpdateEventInDB(
            id=event_id,           
            name = data.name,
            description = data.description,
            date =  data.date,
            location = data.location,
            capacity = data.capacity,             
            created_by_id=current_user.id
        )       
    return await event_db_service.update_events(db, updated_events=updated_event)
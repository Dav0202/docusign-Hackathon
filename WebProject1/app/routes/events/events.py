from typing import Annotated, List
from app.core.exceptions import exception_handler
from fastapi import APIRouter, Depends, status, Request
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
from app.routes.users.users import PermissionChecker
from fastapi_sa_orm_filter.main import FilterCore
from fastapi_sa_orm_filter.operators import Operators as ops
from fastapi.params import Query

router = APIRouter(tags=["Events"])


@router.get(
    "/event/{event_id}", status_code=status.HTTP_200_OK, response_model=schema.EventsRead,
    dependencies=[Depends(PermissionChecker(["user", "volunteer", "organizer"]))]     
)
async def get_event(
        event_id: str,   
        current_user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)) :
        return await event_db_service.get_event(
            event_id, db
        )  

my_objects_filter = {
    'name': [ops.eq, ops.in_, ops.contains],    
    'date': [ops.between, ops.eq, ops.gt, ops.lt, ops.in_],
    'location': [ops.eq, ops.in_, ops.like, ops.startswith, ops.contains],    
    'capacity': [ops.between, ops.eq, ops.gte, ops.lte]
}

@router.get(
    "/events", status_code=status.HTTP_200_OK, response_model=list[schema.EventsRead],
    dependencies=[Depends(PermissionChecker(["user", "volunteer", "organizer"]))]     
)
async def get_events(
        current_user: User = Depends(current_active_user),
        filter_query: str = Query(default=''),   
        db: AsyncSession = Depends(get_async_session)) -> List[Events] :   
        my_filter = FilterCore(Events, my_objects_filter)
        query = my_filter.get_query(filter_query)
        res = await db.execute(query)
        return res.scalars().all()         

"""
async def get_events(
        current_user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)) :
        return await event_db_service.get_events(
            db
        )      """  

@router.get(
    "/my-events", status_code=status.HTTP_200_OK, response_model=list[schema.EventsRead],
    dependencies=[Depends(PermissionChecker(["organizer"]))]     
)
async def get_my_events(
        current_user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)) :
        return await event_db_service.my_get_events(
            db,
            created_by_id=current_user.id,
        )  

@router.post(
    "/events", status_code=status.HTTP_201_CREATED, response_model=schema.Events,
    dependencies=[Depends(PermissionChecker(["organizer"]))]     
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
    }, dependencies=[Depends(PermissionChecker(["organizer"]))] 
)
@exception_handler
async def update_event(
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


#events-registrations

@router.get(
    "/events-registrations/", status_code=status.HTTP_200_OK, response_model=list[schema.Event_Registration_Read], 
    dependencies=[Depends(PermissionChecker(["user", "volunteer"]))] 
)
async def get_events_registrations(
        current_user: User = Depends(current_active_user),
        db: AsyncSession = Depends(get_async_session)) :
        return await event_db_service.get_events_registrations(current_user,
            db
        )    

@router.post(
    '/events-registrations/{event_id}', status_code=status.HTTP_201_CREATED, response_model=schema.Event_Registration, 
    dependencies=[Depends(PermissionChecker(["user", "volunteer"]))] 
)
@exception_handler
async def post_events(
    request: Request,
    event_id: str,       
    current_user: Annotated[User, Depends(current_active_user)],
    db: AsyncSession = Depends(get_async_session))-> Events_Registration:        
        event_regs_in = schema.Event_RegistrationInDB(
            user_id = current_user.id,
            event_id = event_id
        )             
        return await event_db_service.add_event_registration(request, db, current_user = current_user, event_regs_in=event_regs_in)

"""
@router.get(
    "/events-demo/", status_code=status.HTTP_200_OK, response_model=None
)
async def get_events_registrations(
        request: Request,        
        current_user: User = Depends(current_active_user),       
        db: AsyncSession = Depends(get_async_session)) :
        data :dict = {
			'user_id': "iht48-t4rgtg4-yh4hgr-nti4t",
			'first_name' : 'papa',
			'last_name' :  'papa2',			
			'email' : 'davidbrain162@gmail.com',
			'event_id': "h47t44-5jg85h-5h585h-5ijt95",	            
			'event_name' :	'scd first event 001'
			}        
        return await event_db_service.after_add_event_registration(
            request, db, data=data
        ) """
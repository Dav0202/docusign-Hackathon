import uuid
from typing import Optional
from fastapi import status

from fastapi.responses import JSONResponse
from app.core import schema
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.db_crud import DBRepo
from app.core.database import User, Events, Events_Registration
from app.core.exceptions import ResourceNotExists, UserNotAllowed
from app.core.utils import QR_Generator
from app.core.mail import simple_send

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

#event-registrations

	async def get_events_registrations(
		self,
		current_user: User,		
		session: AsyncSession,

	) -> list[Events_Registration]:
		return await self._repo.get_multi(
			session,
			table_model=Events_Registration,
			query_filter = Events_Registration.user_id == current_user.id			
		)

	async def add_event_registration(
		self,
		request,
		session: AsyncSession,
		current_user,        
		event_regs_in,    
	) -> Events_Registration:

		events: Optional[Events] = await self._repo.get_id(
			session,
			event_regs_in.event_id,
			table_model=Events,
		)  

		events_reg: Optional[Events_Registration] = await self._repo.get_multi_filter(
			session,
			table_model=Events_Registration,
			query_filter1 = Events_Registration.event_id == event_regs_in.event_id,
			query_filter2 = Events_Registration.user_id == event_regs_in.user_id
						  
		)                   
		if not events:
			raise ResourceNotExists(resource='events')
		
		if events.capacity > 0 and events.attendees_count >= events.capacity:
			raise UserNotAllowed('Event full Cant register for event')

		if events_reg:
			raise UserNotAllowed('User has already registered for event')

		datam: dict = {
			'user_id': str(current_user.id),
			'first_name' : current_user.first_name,
			'last_name' :  current_user.last_name,			
			'email' : current_user.email,
			'event_id': str(events.id),	            
			'event_name' :	events.name
			}					

		create_reg = await self._repo.create_reg(session, datam, request, event_regs_in.event_id, 
										   event_table=Events, obj_to_create=event_regs_in)
		
		
		if create_reg:				
			qr_generator = QR_Generator()
			qr_code = qr_generator.generate_secure_qr_code(
					datam['user_id'], datam['event_id'], create_reg['registration_id'], datam['first_name']
					)						
			base64qr = "data:image/png;base64," + qr_code
			body = {"qr_code": base64qr, "event_name": datam['event_name']}

			Email = {
					"email": [datam['email']],
					"body": schema.ValidationSchemaQr(**body),
					"file_name": "event-registered.html",
				}

			e_mail = schema.EmailSchema(**Email)
			await simple_send(e_mail)

		return JSONResponse(create_reg, status_code=status.HTTP_201_CREATED)					
		
		
event_db_service = EventDBService()
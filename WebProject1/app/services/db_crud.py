from typing import Optional, Type, TypeVar, Union, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import Base
from app.core.schema import BaseInDB, BaseUpdateInDB
from app.services.docusign_services.ds_client import DsClient
from docusign_esign import ApiException
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.docusign_services.event_document import DsDocument
from app.services.docusign_services.event_envelope import Envelope
from app.core import config
from fastapi.responses import JSONResponse
from app.services.docusign_services.session_data import SessionData

ModelType = TypeVar('ModelType', bound=Base)
InDBSchemaType = TypeVar('InDBSchemaType', bound=BaseInDB)
UpdateSchemaType = TypeVar('UpdateSchemaType', bound=BaseUpdateInDB)

class DBRepo:

	def __init__(self) -> None:
		...

	async def get_id(
		self,
		session: AsyncSession,
		obj_id,        
		table_model: Type[ModelType],

	):
		query = select(table_model).filter_by(id = obj_id)
		result = await session.execute(query)
		return result.scalars().first()        

	async def get(
		self,
		session: AsyncSession,
		*,
		table_model: Type[ModelType],
		query_filter=None
	):
		query = select(table_model)
		if query_filter is not None:
			query = query.filter(query_filter)
		result = await session.execute(query)
		return result.scalars().first()

	async def get_multi(
		self,
		session: AsyncSession,
		*,
		table_model: Type[ModelType],
		query_filter=None,
	) -> list[ModelType]:
		query = select(table_model)
		if query_filter is not None:
			query = query.filter(query_filter)
		result = await session.execute(query)
		return result.scalars().all()

	async def create(
		self,
		session: AsyncSession,
		*,
		obj_to_create: InDBSchemaType
	) -> ModelType:     
		db_obj: ModelType = obj_to_create.to_orm()
		session.add(db_obj)
		await session.commit()
		await session.refresh(db_obj)
		return db_obj

	async def update(
		self,
		session: AsyncSession,
		*,
		updated_obj: UpdateSchemaType,
		db_obj_to_update: Optional[ModelType] = None
	) -> Optional[ModelType]:
		existing_obj_to_update: Optional[ModelType] = db_obj_to_update or await self.get(
			session,
			table_model=updated_obj.Config.orm_model,
			query_filter=updated_obj.Config.orm_model.id == updated_obj.id
		)
		if existing_obj_to_update:
			existing_obj_to_update_data = existing_obj_to_update.__dict__ 
			updated_data: dict[str, Any] = updated_obj.__dict__        
			for field in existing_obj_to_update_data:              
				if field in updated_data:                   
					setattr(existing_obj_to_update, field, updated_data[field])  
				else:
					pass                                                  
			session.add(existing_obj_to_update)
		   
			await session.commit()
			await session.refresh(existing_obj_to_update)
		return existing_obj_to_update

	async def delete(
		self,
		session: AsyncSession,
		*,
		table_model: Type[ModelType],
		id_to_delete: int
	) -> None:
		query = delete(table_model).where(table_model.id == id_to_delete)
		await session.execute(query)
		await session.commit()

	async def get_multi_filter(
		self,
		session: AsyncSession,
		*,
		table_model: Type[ModelType],
		query_filter1=None,
		query_filter2=None        
	):
		query = select(table_model)              
		query = query.filter(query_filter1).filter(query_filter2)
		result = await session.execute(query)
		return result.scalars().first()           

	async def create_reg(
		self,
		session: AsyncSession,
		datam: dict,      
		request,          
		event_id,       
		event_table,         
		*,
		obj_to_create: InDBSchemaType
	) -> ModelType:             
		event = await self.get_id(session = session, obj_id=event_id, table_model=event_table)                
		db_obj: ModelType = obj_to_create.to_orm()            

		# Create registration
		try:
			nested =  await session.begin_nested()							
			event_document = await self.after_add_event_registration(request, session, data=datam)			
			db_obj.envelope_id = event_document['envelope_id']
			session.add(db_obj)			
			event.attendees_count += 1
		except Exception as e:
			await nested.rollback()    
			raise e					
		
		await session.commit()		
		event_document['registration_id'] = db_obj.id		
		return event_document		

	async def after_add_event_registration(
		self,
		request,		
		session: AsyncSession,
		data) -> dict:
		logged = SessionData.is_logged(request)
				
		if not logged or logged is False:
			try:
				auth_data = DsClient.update_token()
				SessionData.set_auth_data(request, auth_data)				
			except ApiException as exc:
				return self.process_error(exc, session)

		envelope_args = {
			'signer_client_id': data['user_id'],
			'ds_return_url': config.APP_DS_RETURN_URL
		}
		try:
			# Create envelope
			envelope = await DsDocument.create('agreement-template.html', 'agreement.txt', data, envelope_args)
			# Submit envelope to the Docusign
			envelope_id = Envelope.send(request, envelope, session)
		except ApiException as exc:
			return self.process_error(exc, session)

		SessionData.set_ds_documents(request, envelope_id)

		try:
			# Get the recipient view
			result = Envelope.get_view(request, envelope_id, envelope_args, data, session)
		except ApiException as exc:
			return self.process_error(exc, session)
	
		return {'envelope_id': envelope_id, 'redirect_url': result.url}

	def process_error(self, exc, request):
		body = exc.body.decode('utf8')
		if "consent_required" in body:
			client_id = request.session.get('account_id')			
			consent_scopes = ' '.join(config.PERMISSION_SCOPES)
			consent_url = f"{config.DS_AUTH_SERVER}/oauth/auth?response_type=code&scope=\
					{consent_scopes}&client_id={client_id}&redirect_uri={config.APP_DS_RETURN_URL}"

			return JSONResponse(content={
					'reason': 'Unauthorized',
					'response': 'Permissions should be granted for current integration',
					'url': consent_url}, status_code=401)

		return JSONResponse(content={
				'reason': exc.reason,
				'response': exc.body.decode('utf8')
			}, status_code=400)		

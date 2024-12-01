from typing import Optional, Type, TypeVar, Union, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.core.database import Base
from app.core.schema import BaseInDB, BaseUpdateInDB

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
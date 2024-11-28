from datetime import datetime, timedelta
import secrets
from fastapi_users import models
from app.core.database import async_session_maker, OTP
from sqlalchemy.future import select

class OTPManager:
    def __init__(self):
        """
        Initialize the OTP Manager.
        Length of the OTP (default: 6 digits)
        """    

    async def generate_otp(self, user: models.UP, token: str) -> str:
        """
        Generate a numeric OTP and store it with an identifier.
        :param user: Current user.
        :return: The generated OTP.
        """
        tokenss = secrets.token_hex(16)
        otp = (str(int(tokenss, 16))[:6])
        expire_at= (datetime.utcnow() + timedelta(seconds=3600))      
        async with async_session_maker() as session:
            # Check if OTP already exists for the email
            result = await session.execute(select(OTP).filter_by(email=user.email))
            otp_entry = result.scalar_one_or_none()

            if otp_entry:
                # Update existing OTP
                otp_entry.otp = otp
                otp_entry.jwt = token                
                otp_entry.expire_at = expire_at
                await session.commit()   
            else:
                # Create a new OTP entry
                otp_entry = OTP(email=user.email, otp=otp, jwt=token, expire_at=expire_at)
                session.add(otp_entry)
                await session.commit()         
        return otp
    
    async def validate_otp(self,otp: str) -> bool:
        """
        Validate the OTP for a given identifier.
        :param otp: The OTP provided by the user.
        :return: True if the OTP is valid, False otherwise.
        """        
        async with async_session_maker() as session:        
            result = await session.execute(select(OTP).filter_by(otp=otp))
            otp_entry = result.scalar_one_or_none()        
            if otp_entry:         
                if otp_entry.otp == otp and otp_entry.expire_at > datetime.utcnow():                    
                    # OTP is valid and not expired
                    return {"is_verified":True, "otp_data": otp_entry.jwt}
                return {"is_verified":  False, "otp_data": otp_entry.jwt}

    async def del_otp(self,otp: str) -> bool:
        """
        Delete the OTP for a given user after confirming OTP.
        :param otp: The OTP to be deleted.
        """        
        async with async_session_maker() as session:        
            result = await session.execute(select(OTP).filter_by(otp=otp))
            otp_entry = result.scalar_one_or_none()        
            if otp_entry:
                 await session.delete(otp_entry)  # Remove OTP after successful validation
                 await session.commit()         
                                 
from datetime import datetime, timedelta
import secrets
from fastapi_users import models
from app.core.database import async_session_maker, OTP
from sqlalchemy.future import select
import qrcode
import hmac
import hashlib
from io import BytesIO
import base64

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


class QR_Generator:
    def __init__(self):
        """
        Initialize the Qr code generator
        """

        self._secret_key = "8618376826ca11dc027861e37575418c"

    def generate_secure_qr_code(self, user_id: str, event_id: str, registration_id: int, first_name:str):
            
        payload_str = f"{registration_id}:{user_id}:{event_id}"
    
        # Generate a secure token
        token = hmac.new(
            self._secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
    
        # Add the token to the payload
        secure_payload = {
            "registration_id": registration_id,
            "user_id": user_id,
            "event_id": event_id,
            "first_name": first_name,            
            "token": token
        }
    
        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(secure_payload)
        qr.make(fit=True)
    
        # Convert QR code to an image
        img = qr.make_image(fill_color="black", back_color="white")
    
        # Encode as Base64
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')     
        return qr_base64

    def validate_qr_code(self, payload: dict):
        # Extract data and token from payload
        registration_id = payload.get("registration_id")
        user_id = payload.get("user_id")
        event_id = payload.get("event_id")
        received_token = payload.get("token")
    
        # Recreate the token using the same secret key and data
        payload_str = f"{registration_id}:{user_id}:{event_id}"
        expected_token = hmac.new(
            self._secret_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
    
        # Compare the received token with the expected token
        if hmac.compare_digest(received_token, expected_token):
            return True  # Token is valid
        else:
            return False  # Token is invalid or tampered with

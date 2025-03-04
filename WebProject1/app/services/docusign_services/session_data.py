import os
from fastapi import Request
from datetime import datetime
from app.core import config

class SessionData:
    """
    This class provides methods for
    getting, setting and deleting session data
    """

    @staticmethod
    def set_auth_data(request, auth_data):
        expires_date = int(round(datetime.utcnow().timestamp() + auth_data['expires_in']))

        request.session['access_token'] = auth_data['access_token']
        request.session['account_id'] = auth_data['account_id']
        request.session['auth_type'] = auth_data['auth_type']
        request.session['expires_date'] = expires_date

    @staticmethod
    def is_logged(request):
        expires_date = request.session.get('expires_date')
        date_now = int(round(datetime.utcnow().timestamp()))
        return expires_date and expires_date > date_now + config.TOKEN_REPLACEMENT_IN_SECONDS

    @staticmethod
    def set_ds_documents(request,envelope_id):
        if not request.session.get('ds_documents'):
            request.session['ds_documents'] = [envelope_id]
        else:
            documents = request.session['ds_documents']
            documents.append(envelope_id)
            request.session['ds_documents'] = documents
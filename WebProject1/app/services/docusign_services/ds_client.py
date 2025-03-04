import os
import uuid

from docusign_esign import ApiClient

from app.core import config


class DsClient:
	"""
	Docusign Client class
	"""

	@staticmethod
	def get_instance():
		"""
		Getting a client instance with DS_HOST_NAME set
		"""
		client = ApiClient()
		host_name = config.DS_AUTH_SERVER.split('://')[1]
		client.set_oauth_host_name(oauth_host_name=host_name)
		return client

	@classmethod
	def get_configured_instance(cls, access_token, host=None):
		if host is None:
			host = config.APP_DS_DEMO_SERVER + '/restapi'
		client = cls.get_instance()
		client.host = host
		client.set_default_header(
			header_name="Authorization",
			header_value=f"Bearer {access_token}"
		)

		return client

	@classmethod
	def get_redirect_uri(cls):
		"""
		Receiving a redirect so that the user logs into his DS account and gives consent
		"""
		client = cls.get_instance()

		my_callback_uri = config.APP_DS_RETURN_URL + "/callback"

		uri = client.get_authorization_uri(
			client_id= config.DS_CLIENT_ID,
			scopes=config.CODE_GRANT_SCOPES,
			redirect_uri=my_callback_uri,
			response_type="code",
			state=uuid.uuid4().hex.upper()
		)
		return uri

	@classmethod
	def callback(cls, code):
		"""
		Callback method for obtaining access token on Oauth authorization
		"""
		client = cls.get_instance()
		response = client.generate_access_token(
			client_id= config.DS_CLIENT_ID,
			client_secret= config.DS_CLIENT_SECRET,
			code=code
		)

		client.set_default_header(
			header_name="Authorization",
			header_value=f"Bearer {response.access_token}"
		)
		account_info = cls._get_account_info(client)

		auth_data = {
			'access_token': response.access_token,
			'account_id': account_info['account_id'],
			'expires_in': int(response.expires_in),
			'auth_type': 'code_grant'
		}

		return auth_data

	@staticmethod
	def _get_account_info(client):
		client.host = config.DS_AUTH_SERVER
		response = client.call_api(
			'/oauth/userinfo', 'GET', response_type='object'
		)

		if len(response) > 1 and 300 > response[1] > 200:
			raise Exception(f'Cannot get user info: {response[1]}')

		accounts = response[0]['accounts']
		target = config.DS_TARGET_ACCOUNT_ID

		# Look for specific account
		if target is not None and target != 'FALSE':
			for acc in accounts:
				if acc['account_id'] == target:
					return acc

			raise Exception(f'\n\nUser does not have access to account {target}\n\n')

		# Look for default
		for acc in accounts:
			if acc['is_default']:
				return acc

		raise Exception('\n\nNo Appropriate account is found\n\n')

	@staticmethod
	def _get_private_key(private_key_path):
		"""
		Check that the private key present in the file and if it is, get it from the file.
		In the opposite way get it from config variable.
		"""
		private_key_file = os.path.abspath(private_key_path)
		if os.path.isfile(private_key_file):
			with open(private_key_file) as private_key_file:
				private_key = private_key_file.read()		
		else:
			private_key = private_key_path			

		return private_key	

	@classmethod
	def update_token(cls):
		"""
		JWT authorization
		"""
		private_key = cls._get_private_key(config.PRIVATE_KEY_FILE)
		
		client = cls.get_instance()
		client.host = config.DS_AUTH_SERVER
		host_name = config.DS_AUTH_SERVER.split('://')[1]
		oauth_token = client.request_jwt_user_token(config.DS_CLIENT_ID,
									  config.DS_IMPERSONATED_USER_GUID,
									  host_name,
									  private_key,
									  config.TOKEN_EXPIRATION_IN_SECONDS,
										config.CODE_GRANT_SCOPES
									  )

		account_info = cls._get_account_info(client)

		auth_data = {
			'access_token': oauth_token.access_token,
			'account_id': account_info['account_id'],
			'expires_in': config.TOKEN_EXPIRATION_IN_SECONDS,
			'auth_type': 'jwt'
		}

		return auth_data
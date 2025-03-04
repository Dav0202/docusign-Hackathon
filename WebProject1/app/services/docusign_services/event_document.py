import base64
from pathlib import Path
from jinja2 import Environment, BaseLoader
import aiofiles
from docusign_esign.models import (Document, Signer, Tabs, SignHere, 
InitialHere, Email, EnvelopeDefinition, Recipients, CarbonCopy)

class DsDocument:
    @classmethod
    async def create(cls, tpl, tpl2, data, envelope_args):
        """
        Creates envelope asynchronously.
        Parameters:
            tpl (str): template path for the document
            tpl2 (str): secondary template path for the document
            data (dict): user data to populate the template
            envelope_args (dict): parameters of the envelope
        Returns:
            EnvelopeDefinition object that will be submitted to DocuSign
        """
        TPL_PATH1 = Path(__file__).parent.parent.parent / 'templates' / tpl
        TPL_PATH2 = Path(__file__).parent.parent.parent / 'templates' / tpl2

        # Load and render the first template
        async with aiofiles.open(TPL_PATH1, 'r') as file:
            content_bytes = await file.read()
        
        content_bytes = Environment(loader=BaseLoader).from_string(content_bytes).render(
            first_name=data['first_name'],
            last_name=data['last_name'],
            email=data['email'],
            event_name=data['event_name'],
        )
        base64_file_content = base64.b64encode(
            bytes(content_bytes, 'utf-8')
        ).decode('ascii')

        # Load and encode the second template
        async with aiofiles.open(TPL_PATH2, "rb") as file:
            doc2_docx_bytes = await file.read()
        doc2_b64 = base64.b64encode(doc2_docx_bytes).decode("ascii")

        # Create the document models
        document = Document(
            document_base64=base64_file_content,
            name='agreement-template',
            file_extension='html',
            document_id=1
        )
        document2 = Document(
            document_base64=doc2_b64,
            name="agreement",
            file_extension="txt",
            document_id="2"
        )

        # Create the signer recipient model
        signer = Signer(
            email=data['email'],
            name=f"{data['first_name']} {data['last_name']}",
            recipient_id='1',
            routing_order='1',
            client_user_id=envelope_args['signer_client_id']
        )

        # Add a CC recipient
        cc1 = CarbonCopy(
            email=data["email"],
            name=data["first_name"],
            recipient_id="2",
            routing_order="2"
        )

        # Create tabs for the signer
        sign_here = SignHere(
            anchor_string='/signature_1/',
            anchor_units='pixels',
            anchor_y_offset='10',
            anchor_x_offset='20'
        )

        initial_here = InitialHere(
            anchor_string='/initials_1/',
            anchor_units='pixels',
            anchor_y_offset='10',
            anchor_x_offset='20'
        )

        email_tab = Email(
            document_id='1',
            page_number='1',
            anchor_string='/email/',
            anchor_units='pixels',
            required=True,
            value=data['email'],
            locked=False,
            anchor_y_offset='-5'
        )

        signer.tabs = Tabs(
            sign_here_tabs=[sign_here],
            email_tabs=[email_tab],
            initial_here_tabs=[initial_here]
        )

        # Create the envelope definition
        envelope_definition = EnvelopeDefinition(
            email_subject='Event Registration',
            documents=[document, document2],
            recipients=Recipients(signers=[signer]),
            status='sent'
        )

        return envelope_definition

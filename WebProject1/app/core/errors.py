from fastapi_users.openapi import OpenAPIResponseType
from fastapi_users.router.common import ErrorModel
from typing import Union

def get_open_api_response(examples_res_details: dict[str, str]) -> OpenAPIResponseType:
    examples: dict[str, dict[str, Union[str, dict[str, str]]]] = {}
    for example, res_detail in examples_res_details.items():
        examples[example] = {
            'summary': example,
            'value': {'detail': res_detail}
        }
    return {
        # https://fastapi.tiangolo.com/advanced/additional-responses/#additional-response-with-model
        'model': ErrorModel,  # type: ignore[dict-item]
        'content': {
            'application/json': {
                'examples': examples
            }
        }
    }
from typing import Callable

from fastapi import FastAPI


def create_start_app_handler(app: FastAPI) -> Callable:
    def start_app() -> None:
        pass

    return start_app

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import basket, common, product, admin_bootstrap
from config import settings
from models.basket import Basket  # noqa: F401
from models.product import BasketProduct, Product  # noqa: F401
from models.user import User  # noqa: F401


PROJECT_ROOT = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="Bot suggester API",
    version="0.1.0",
    redirect_slashes=False
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        settings.FRONTEND_ORIGIN,
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type"],
)

app.include_router(admin_bootstrap.router, prefix="/internal", tags=["internal"])
app.include_router(basket.router, prefix="/api/basket", tags=["basket"])
app.include_router(common.router, tags=["common"])
app.include_router(product.router, prefix="/api", tags=["product"])

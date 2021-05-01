from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from starlette.responses import JSONResponse
from app.routes.query_country_airline_info import query_country_airline_info
from app.routes.query_country_news import query_country_news
from app.routes.query_country_travel_info import query_country_travel_info
from app.routes.refresh_jhu import refresh_jhu
from app.routes.refresh_owid import refresh_owid
from app.routes.refresh_pops import refresh_pops
from app.routes.refresh_tests import refresh_tests


app = FastAPI()


# @app.on_event("startup")
# async def startup():
#     await database.connect()


# @app.on_event("shutdown")
# async def shutdown():
#     await database.disconnect()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


app.include_router(query_country_airline_info, prefix='/query/country/airline-info')
app.include_router(query_country_news, prefix='/query/country/news')
app.include_router(query_country_travel_info, prefix='/query/country/travel-info')
app.include_router(refresh_jhu, prefix='/refresh/jhu')
app.include_router(refresh_owid, prefix='/refresh/owid')
app.include_router(refresh_pops, prefix='/refresh/pops')
app.include_router(refresh_tests, prefix='/refresh/tests')

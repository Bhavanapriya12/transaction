# telegram_bot_token = "6974807327:AAGaO_XzF4b8P3OWs5HBVzyJhPeYw9adtsw"
# bot = Bot(token=telegram_bot_token)
# chat_ids = ['1331794477','6089466878']


# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)


# async def send_telegram_message(text: str):
#     for chat_id in chat_ids:
#         try:
#             await bot.send_message(chat_id=chat_id, text=text)
#         except Exception as e:
#             logger.error(f"Failed to send message to {chat_id}: {str(e)}")
# @app.exception_handler(HTTPException)
# async def http_exception_handler(request: Request, exc: HTTPException):
#     error_message = f"HTTP error occurred: {exc.detail}"
#     logger.error(error_message)
#     await send_telegram_message(text=error_message)
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": error_message}
#     )

# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request: Request, exc: RequestValidationError):
#     error_message = f"Validation error: {exc.errors()}"
#     logger.error(error_message)
#     await send_telegram_message(chat_id=chat_ids, text=error_message)
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": error_message}
#     )

# @app.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc:Exception):
#     error_message = f"internal server error: {exc}"
#     logger.error(error_message)
#     await send_telegram_message(chat_id=chat_ids, text=error_message)
#     return JSONResponse(
#         status_code=exc.status_code,
#         content={"message": error_message}
#     )

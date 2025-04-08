import time

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette import status

from app.core.container import Container
from app.core.log import generate_request_id, get_logger, request_id_ctx_var
from app.domain.exception import ServerException


class CommonRouter(APIRoute):
    def get_route_handler(self):
        original_handler = super().get_route_handler()

        async def common_handler(request: Request):
            request_id = generate_request_id()
            request_id_ctx_var.set(request_id)
            log = get_logger()

            start_time = time.time()
            status_code = 500
            try:
                oauth_token = request.headers.get("X-OAuth-Token")
                session_service = Container.session_service()
                if not oauth_token or not session_service.verify_oauth_token(
                    oauth_token
                ):
                    raise ServerException(
                        user_message="UNAUTHORIZED",
                        log_message=f"invalid oauth_token: {oauth_token}",
                        http_code=status.HTTP_401_UNAUTHORIZED,
                    )

                response = await original_handler(request)
                status_code = response.status_code
                return response
            except ServerException as exc:
                log.error(f"[ServerException] {exc.log_message}")
                return JSONResponse(
                    status_code=exc.http_code, content={"message": exc.user_message}
                )
            except Exception as exc:
                log.error(f"[UnhandledException] {exc}")
                return JSONResponse(status_code=500, content={"message": exc})
            finally:
                process_time = (time.time() - start_time) * 1000
                log.info(
                    f"{request.method} {request.url.path} - {status_code} - {process_time:.2f}ms"
                )

        return common_handler

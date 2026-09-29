from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.auth.jwt.utils import decode_access_token

ACCESS_TOKEN_COOKIE = "access_token"


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        request.state.user_id = None

        token = request.cookies.get(ACCESS_TOKEN_COOKIE)

        if token:
            try:
                request.state.user_id = decode_access_token(token)
            except Exception:
                request.state.user_id = None

        return await call_next(request)

import json

from asgiref.sync import iscoroutinefunction
from django.conf import settings


class DebugResponseLoggingMiddleware:
    async_capable = True
    sync_capable = True

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if iscoroutinefunction(self.get_response):
            return self.__acall__(request)

        response = self.get_response(request)
        self._maybe_print_response(request, response)
        return response

    async def __acall__(self, request):
        response = await self.get_response(request)
        self._maybe_print_response(request, response)
        return response

    def _maybe_print_response(self, request, response) -> None:
        if request.path.startswith("/system-admin/"):
            return
        if not request.path.startswith("/v1/"):
            return
        self._print_response(request, response)

    def _print_response(self, request, response) -> None:
        query = request.META.get("QUERY_STRING", "")
        path = f"{request.path}?{query}" if query else request.path

        if not hasattr(response, "content"):
            body = "<streaming response>"
        elif not response.content:
            body = "<empty>"
        else:
            try:
                payload = json.loads(response.content.decode())
                body = json.dumps(payload, indent=2, default=str)
            except (json.JSONDecodeError, UnicodeDecodeError):
                text = response.content.decode(errors="replace")
                body = text if len(text) <= 2000 else f"{text[:2000]}…"

        print(
            f"\n[DEBUG RESPONSE] {request.method} {path} -> {response.status_code}\n"
            f"{body}\n",
            flush=True,
        )

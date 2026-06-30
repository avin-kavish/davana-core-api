from rest_framework.pagination import CursorPagination


class VehicleCursorPagination(CursorPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 1000
    ordering = ("-created_at", "-pk")

class DetailSerializerMixin:
    serializer_detail_class = None
    queryset_detail = None

    def get_serializer_class(self):
        error_message = (
            f"'{self.__class__.__name__}' should include a "
            "'serializer_detail_class' attribute"
        )
        assert self.serializer_detail_class is not None, error_message
        if getattr(self, "action", None) in ("retrieve", "aretrieve"):
            return self.serializer_detail_class
        return super().get_serializer_class()

    def get_queryset(self):
        if (
            getattr(self, "action", None) in ("retrieve", "aretrieve")
            and self.queryset_detail is not None
        ):
            return self.queryset_detail.all()
        return super().get_queryset()

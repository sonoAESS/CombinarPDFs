import tkinter

class _DnDMixin:
    def drop_target_register(self, *dndtypes: str) -> None: ...
    def dnd_bind(
        self,
        sequence: str | None = ...,
        func: object | None = ...,
        add: object | None = ...,
    ) -> object: ...

class Tk(tkinter.Tk, _DnDMixin):
    def __init__(self, *args: object, **kwargs: object) -> None: ...

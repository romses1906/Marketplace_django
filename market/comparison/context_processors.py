from .comparison import Comparison


def comparison(request):
    return {"compare": Comparison(request)}

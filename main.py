from starlette.applications import Starlette

from src.routs import routes


app = Starlette(debug=True, routes=routes)



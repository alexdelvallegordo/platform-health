from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates


router = APIRouter(
    tags=["Dashboard"]
)

templates = Jinja2Templates(
    directory="app/templates"
)


@router.get(
    "/",
    response_class=HTMLResponse,
)
async def dashboard(
    request: Request,
) -> HTMLResponse:

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={},
    )

from fastapi import FastAPI
from routes.auth import auth_router
from routes.profile import order_router
from routes.barcode import barcode_router
from fastapi.staticfiles import StaticFiles
import os
import uvicorn


app = FastAPI(debug=False)

# Register routes
app.include_router(auth_router,  prefix="/auth")
app.include_router(order_router, prefix="/order")
app.include_router(barcode_router, prefix="/barcode")

photo_dir = os.path.join(os.path.dirname(__file__), "photo")

app.mount("/photo", StaticFiles(directory=photo_dir), name="photo")

if __name__ == "__main__":
    uvicorn.run("main:app", port=8000, reload=True)
    # docker run -d --name mycontainer -p 80:80 myimage

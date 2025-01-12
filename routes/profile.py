from fastapi import APIRouter, Depends, Form, HTTPException, status, Request, Response, Security, File, UploadFile
from models.profile_model import *
from config.database import OrderProductDatabase
from config.jwt_token import JwtManager
from routes.save_photo import save_file
import json


# Создаем роутер для пользователей
order_router = APIRouter()
jwt = JwtManager()

# Зависимость для создания экземпляра базы данных
async def get_db():
    db = OrderProductDatabase()
    try:
        yield db
    finally:
        await db.close()


# Эндпоинты для работы с товарами
@order_router.post("/products/", response_model=ProductResponse)
async def create_product(product: ProductCreate,
                         db: OrderProductDatabase = Depends(get_db),
                         jwt_token: dict = Security(jwt.verify_token)):
    product_id = await db.create_product(product.package_name, product.package_barcode, product.package_quantity)
    return ProductResponse(product_id=product_id, **product.dict())


@order_router.get("/products/{product_id}", response_model=ProductResponse)
async def get_product(product_id: int,
                      db: OrderProductDatabase = Depends(get_db),
                      jwt_token: dict = Security(jwt.verify_token)):
    product = await db.get_product(product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductResponse(**product)

# Эндпоинты для работы с заказами


@order_router.post("/orders/", response_model=OrderResponse)
async def create_order(order: OrderCreate,
                       db: OrderProductDatabase = Depends(get_db),
                       jwt_token: dict = Security(jwt.verify_token)):
    order_id = await db.create_order(**order.dict())
    return OrderResponse(order_id=order_id, **order.dict())


@order_router.get("/orders/{order_id}", response_model=OrderResponse)
async def get_order(order_id: int,
                    db: OrderProductDatabase = Depends(get_db),
                    jwt_token: dict = Security(jwt.verify_token)):
    order = await db.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderResponse(**order)


@order_router.post("/orders/{order_id}/items")
async def add_products_to_order(order_id: int, items: List[OrderItem],
                                db: OrderProductDatabase = Depends(get_db),
                                jwt_token: dict = Security(jwt.verify_token)):
    await db.add_products_to_order(order_id, [(item.product_id) for item in items])
    return {"message": "Products added to order successfully"}


@order_router.get("/orders/{order_id}/items", response_model=OrderWithItems)
async def get_order_with_items(order_id: int,
                               db: OrderProductDatabase = Depends(get_db),
                               jwt_token: dict = Security(jwt.verify_token)):
    order_with_items = await db.get_order_with_items(order_id)
    if order_with_items is None:
        raise HTTPException(status_code=404, detail="Order not found")

    # Преобразование строки JSON в список объектов Python
    if isinstance(order_with_items['items'], str):
        order_with_items['items'] = json.loads(order_with_items['items'])

    # Преобразование каждого элемента в объект ProductResponse
    order_with_items['items'] = [ProductResponse(
        **item) for item in order_with_items['items']]

    return OrderWithItems(**order_with_items)


# Эндпоинты для работы с курьерами
@order_router.post("/couriers/", response_model=int)
async def create_courier(courier_id: int,
                         db: OrderProductDatabase = Depends(get_db),
                         jwt_token: dict = Security(jwt.verify_token)):
    try:
        created_courier_id = await db.create_courier(courier_id)
        return created_courier_id
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@order_router.post("/couriers/{courier_id}/orders/{order_id}")
async def assign_order_to_courier(courier_id: int, order_id: int,
                                  db: OrderProductDatabase = Depends(get_db),
                                  jwt_token: dict = Security(jwt.verify_token)):
    try:
        await db.assign_order_to_courier(courier_id, order_id)
        return {"message": f"Order {order_id} assigned to courier {courier_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@order_router.get("/couriers/{courier_id}/orders", response_model=List[OrderWithItems])
async def get_courier_orders(courier_id: int,
                             db: OrderProductDatabase = Depends(get_db),
                             jwt_token: dict = Security(jwt.verify_token)):
    orders = await db.get_courier_orders(courier_id)
    return [OrderWithItems(**order) for order in orders]


@order_router.delete("/couriers/{courier_id}/orders/{order_id}")
async def remove_order_from_courier(courier_id: int, order_id: int,
                                    db: OrderProductDatabase = Depends(get_db),
                                    jwt_token: dict = Security(jwt.verify_token)):
    try:
        removed_order_id = await db.remove_order_from_courier(courier_id, order_id)
        if removed_order_id is None:
            raise HTTPException(
                status_code=404, detail="Order not found or not assigned to this courier")
        return {"message": f"Order {removed_order_id} removed from courier {courier_id}"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@order_router.get("/orders-list", response_model=List[OrderResponse])
async def get_all_orders(db: OrderProductDatabase = Depends(get_db),
                         jwt_token: dict = Security(jwt.verify_token)):
    orders = await db.get_all_orders()
    return [OrderResponse(**order) for order in orders]


@order_router.get("/products-list", response_model=List[ProductResponse])
async def get_all_products(db: OrderProductDatabase = Depends(get_db),
                           jwt_token: dict = Security(jwt.verify_token)):
    products = await db.get_all_products()
    return [ProductResponse(**product) for product in products]


@order_router.get("/courier-orders-list", response_model=List[CourierOrderResponse])
async def get_all_courier_orders(db: OrderProductDatabase = Depends(get_db),
                                 jwt_token: dict = Security(jwt.verify_token)):
    courier_orders = await db.get_all_courier_orders()
    return [CourierOrderResponse(**co) for co in courier_orders]


@order_router.post("/orders/{order_id}/deliver")
async def mark_order_as_delivered(
    order_id: int,
    courier_id: int,
    reason: str,
    file: UploadFile = File(...),
    db: OrderProductDatabase = Depends(get_db),
    jwt_token: dict = Security(jwt.verify_token)
):
    try:
        file_name = await save_file(file)
        print(file_name)

        await db.mark_order_as_delivered(order_id=order_id, courier_id=courier_id, photo=file_name, reason=reason)
        return {"message": f"Order {order_id} marked as delivered by courier {courier_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@order_router.post("/orders/{order_id}/undeliver")
async def mark_order_as_undelivered(
    order_id: int,
    courier_id: int,
    reason: str,
    db: OrderProductDatabase = Depends(get_db),
    jwt_token: dict = Security(jwt.verify_token)
):
    try:
        await db.mark_order_as_undelivered(order_id, courier_id, reason)
        return {"message": f"Order {order_id} marked as undelivered by courier {courier_id}"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@order_router.get("/delivered", response_model=List[DeliveredOrderResponse])
async def get_delivered_orders(
    db: OrderProductDatabase = Depends(get_db),
    jwt_token: dict = Security(jwt.verify_token)
):
    delivered_orders = await db.get_delivered_orders()
    return [DeliveredOrderResponse(
        order_id=order['order_id'],
        courier_id=order['courier_id'],
        delivery_time=order['delivery_time'],
        customer_name=order['customer_name'],
        address=order['address'],
        phone=order['phone'],
        order_total=float(order['order_total'])
    ) for order in delivered_orders]


@order_router.get("/undelivered", response_model=List[UndeliveredOrderResponse])
async def get_undelivered_orders(
    db: OrderProductDatabase = Depends(get_db),
    jwt_token: dict = Security(jwt.verify_token)
):
    undelivered_orders = await db.get_undelivered_orders()
    return [UndeliveredOrderResponse(
        order_id=order['order_id'],
        courier_id=order['courier_id'],
        delivery_time=order['delivery_time'],
        reason=order['reason'],
        customer_name=order['customer_name'],
        address=order['address'],
        phone=order['phone'],
        order_total=float(order['order_total'])
    ) for order in undelivered_orders]


@order_router.delete("/clear_all_delivered_orders")
async def clear_all_delivered_orders(
    db: OrderProductDatabase = Depends(get_db),
    jwt_token: dict = Security(jwt.verify_token)
):
    undelivered_orders = await db.clear_all_delivered_orders()
    return {'status': undelivered_orders}


@order_router.delete("/clear_all_undelivered_orders")
async def clear_all_undelivered_orders(
    db: OrderProductDatabase = Depends(get_db),
    jwt_token: dict = Security(jwt.verify_token)
):
    undelivered_orders = await db.clear_all_undelivered_orders()
    return {'status': undelivered_orders}


@order_router.delete("/clear_delivered_order")
async def clear_delivered_order(
    order_id: int,
    db: OrderProductDatabase = Depends(get_db),
    jwt_token: dict = Security(jwt.verify_token)
):
    undelivered_orders = await db.clear_delivered_order(order_id=order_id)
    return {'status': undelivered_orders}


@order_router.delete("/clear_undelivered_order")
async def clear_undelivered_order(
    order_id: int,
    db: OrderProductDatabase = Depends(get_db),
    jwt_token: dict = Security(jwt.verify_token)
):
    undelivered_orders = await db.clear_undelivered_order(order_id=order_id)
    return {'status': undelivered_orders}

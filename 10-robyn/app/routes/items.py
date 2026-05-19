from robyn import jsonify, Request, Response
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db
import json
from decimal import Decimal

def get_db_session(request: Request) -> Session:
    return next(get_db())


async def read_items(request: Request):
    db = get_db_session(request)
    skip = int(request.query_params.get("skip", "0") or "0")
    limit = int(request.query_params.get("limit", "100") or "100")

    items = crud.ItemCRUD.get_items(db, skip=skip, limit=limit)
    return jsonify({
        "items": [
            {
                "id": item.id,
                "title": item.title,
                "description": item.description,
                "price": str(item.price),
                "owner_id": item.owner_id
            }
            for item in items
        ]
    })


async def create_item(request: Request):
    db = get_db_session(request)
    try:
        item_data = json.loads(request.body)

        # 简化：从请求中获取用户ID（实际应从token获取）
        owner_id = item_data.get("owner_id", 1)

        # 转换价格字符串为Decimal
        if "price" in item_data:
            item_data["price"] = Decimal(str(item_data["price"]))

        item_create = schemas.ItemCreate(**item_data)
        item = crud.ItemCRUD.create_item(db, item_create, owner_id)

        return Response(
            status_code=201,
            headers={"Content-Type": "application/json"},
            description=jsonify({
                "id": item.id,
                "title": item.title,
                "price": str(item.price),
                "owner_id": item.owner_id,
                "message": "Item created successfully"
            })
        )
    except Exception as e:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": str(e)})
        )


async def read_item(request: Request):
    db = get_db_session(request)
    item_id = int(request.path_params["item_id"])

    item = crud.ItemCRUD.get_item(db, item_id)
    if item is None:
        return Response(
            status_code=404,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": "Item not found"})
        )

    return jsonify({
        "id": item.id,
        "title": item.title,
        "description": item.description,
        "price": str(item.price),
        "owner_id": item.owner_id,
        "created_at": item.created_at.isoformat()
    })


async def update_item(request: Request):
    db = get_db_session(request)
    item_id = int(request.path_params["item_id"])

    try:
        update_data = json.loads(request.body)

        # 转换价格
        if "price" in update_data:
            update_data["price"] = Decimal(str(update_data["price"]))

        item_update = schemas.ItemUpdate(**update_data)

        item = crud.ItemCRUD.update_item(db, item_id, item_update)
        if not item:
            return Response(
                status_code=404,
                description=jsonify({"error": "Item not found"})
            )

        return jsonify({
            "message": "Item updated successfully",
            "item": {
                "id": item.id,
                "title": item.title,
                "price": str(item.price)
            }
        })
    except Exception as e:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": str(e)})
        )


async def delete_item(request: Request):
    db = get_db_session(request)
    item_id = int(request.path_params["item_id"])

    success = crud.ItemCRUD.delete_item(db, item_id)
    if not success:
        return Response(
            status_code=404,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": "Item not found"})
        )

    return jsonify({"message": "Item deleted successfully"})


# 搜索和过滤
async def search_items(request: Request):
    db = get_db_session(request)

    try:
        # 构建过滤器
        filters = schemas.ItemFilterParams(
            page=int(request.query_params.get("page", "1") or "1"),
            size=int(request.query_params.get("size", "10") or "10"),
            min_price=Decimal(request.query_params["min_price"]) if "min_price" in request.query_params else None,
            max_price=Decimal(request.query_params["max_price"]) if "max_price" in request.query_params else None,
            search=request.query_params.get("search"),
            sort_by=request.query_params.get("sort_by"),
            sort_order=request.query_params.get("sort_order", "asc") or "asc"
        )

        result = crud.ItemCRUD.search_items(db, filters)

        return jsonify({
            "items": [
                {
                    "id": item.id,
                    "title": item.title,
                    "description": item.description,
                    "price": str(item.price),
                    "owner_id": item.owner_id
                }
                for item in result["items"]
            ],
            "pagination": {
                "total": result["total"],
                "page": result["page"],
                "size": result["size"],
                "pages": result["pages"]
            }
        })
    except Exception as e:
        return Response(
            status_code=400,
            headers={"Content-Type": "application/json"},
            description=jsonify({"error": str(e)})
        )

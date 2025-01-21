from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select

from src.api.models.tables import Product, ProductCreate, ProductRead, ProductUpdate
from src.database.session import get_session


# router instance for products endpoints
router = APIRouter(prefix="/products", tags=["products"])


@router.get("/products", response_model=list[ProductRead])
async def list_products(session: Annotated[Session, Depends(get_session)]):
    """Retrieve the list of all available products."""
    statement = select(Product)
    products = session.exec(statement).all()
    return products


@router.get(
    "/{product_id}",
    response_model=ProductRead,
    responses={
        200: {"description": "Product found"},
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Product with id 123 not found"}
                }
            },
        },
    },
)
async def get_product(
    product_id: int, session: Annotated[Session, Depends(get_session)]
):
    """Retrieve a specific product by ID."""
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found"
        )
    return product


@router.post(
    "/",
    response_model=ProductRead,
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {"description": "Product created successfully"},
        409: {
            "description": "Product number already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product with number BK-NEW-001 already exists"
                    }
                }
            },
        },
    },
)
async def create_product(product: ProductCreate, session: Session = Depends(...)):
    """Create a new product.

    Args:
        product: product data from request body (validated by ProductCreate model)
        session: database session (injected by FastAPI)

    Returns:
        the newly created product

    Raises:
        HTTP Exception: if product_number already exists
    """
    # Create a database instance from the product data
    db_product = Product.model_validate(product)

    # Check whether product number already exists
    existing = session.exec(
        select(Product).where(Product.product_number == product.product_number)
    ).first()

    if existing:
        raise HTTPException(
            status_code=409,  # Conflict
            detail=f"Product with number {product.product_number} already exists",
        )

    # Set the creation date with modified_date as current timestamp
    db_product.modified_date = datetime.now(timezone.utc)

    # Add and commit the new product
    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return ProductRead.model_validate(db_product)


@router.put(
    "/{product_id}",
    response_model=ProductRead,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Product updated successfully"},
        404: {
            "description": "Product not found",
            "content": {
                "application/json": {
                    "example": {"detail": "Product with id 123 not found"}
                }
            },
        },
        409: {
            "description": "Product number already exists",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Product with number BK-NEW-001 already exists"
                    }
                }
            },
        },
    },
)
async def update_product(
    product_id: int,
    product: ProductUpdate,
    session: Annotated[Session, Depends(get_session)],
) -> ProductRead:
    """Update a product.

    Args:
        product_id: ID of the product to update
        product: updated product data
        session: database session

    Returns:
        updated product

    Raises:
        HTTP Exception if:
            - product not found,
            - product number conflict
    """
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(
            status_code=404, detail=f"Product with id {product_id} not found"
        )

    # Check product_number uniqueness
    if (
        product.product_number is not None
        and product.product_number != db_product.product_number
    ):
        existing = session.exec(
            select(Product).where(Product.product_number == product.product_number)
        ).first()
        if existing:
            raise HTTPException(
                status_code=409,
                detail=f"Product with number {product.product_number} already exists",
            )

    # Update product fields
    product_data = product.model_dump(exclude_unset=True)
    for key, value in product_data.items():
        setattr(db_product, key, value)

    # Set the new modification date
    db_product.modified_date = datetime.now(timezone.utc)
    session.add(db_product)
    session.commit()
    session.refresh(db_product)

    return ProductRead.model_validate(db_product)

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import validator
from sqlmodel import SQLModel, Field, Relationship


# TABLE MODELS
class ProductModelProductDescription(SQLModel, table=True):
    __tablename__ = "ProductModelProductDescription"

    product_model_id: int = Field(
        foreign_key="ProductModel.ProductModelID", primary_key=True, nullable=False
    )
    product_description_id: int = Field(
        foreign_key="ProductDescription.ProductDescriptionID",
        primary_key=True,
        nullable=False,
    )
    # Culture is also part of the PK in the AdventureWorksLT schema
    culture: str = Field(..., max_length=12, primary_key=True, nullable=False)

    rowguid: str = Field(..., max_length=16, nullable=False)
    modified_date: datetime = Field(..., nullable=False)


class ProductDescription(SQLModel, table=True):
    __tablename__ = "ProductDescription"

    product_description_id: int = Field(
        primary_key=True, alias="ProductDescriptionID", nullable=False
    )
    description: str = Field(..., max_length=800, nullable=False)
    rowguid: str = Field(..., max_length=16, nullable=False)
    modified_date: datetime = Field(..., nullable=False)

    # Many-to-many Relationship back to ProductModel
    models: list["ProductModel"] = Relationship(
        back_populates="descriptions", link_model=ProductModelProductDescription
    )


class ProductModel(SQLModel, table=True):
    __tablename__ = "ProductModel"

    product_model_id: int = Field(
        primary_key=True, alias="ProductModelID", nullable=False
    )

    name: str = Field(..., max_length=100, nullable=False)

    # 'CatalogDescription' is xml, so we can store it as an optional string
    catalog_description: str | None = Field(default=None)

    rowguid: str = Field(..., max_length=16, nullable=False)

    modified_date: datetime = Field(..., nullable=False)

    # one-to many Relationship to Product:
    products: list["Product"] = Relationship(back_populates="product_model")

    # many-to-many Relationship to ProductDescription
    descriptions: list[ProductDescription] = Relationship(
        back_populates="models", link_model=ProductModelProductDescription
    )


class ProductCategory(SQLModel, table=True):
    __tablename__ = "ProductCategory"

    product_category_id: int = Field(
        primary_key=True, alias="ProductCategoryID", nullable=False
    )
    parent_product_category_id: int | None = Field(
        default=None, foreign_key="ProductCategory.ProductCategoryID"
    )
    name: str = Field(..., max_length=100, nullable=False)
    rowguid: str = Field(..., max_length=16, nullable=False)
    modified_date: datetime = Field(..., nullable=False)

    # # Self-referential Relationship: sub-categories and parent
    # # ⚠️ Commmented as they cause unsolved issues when API running
    # parent_category: "ProductCategory" | None = Relationship(
    #     back_populates="sub_categories",
    #     sa_relationship_kwargs={"remote_side": "ProductCategory.product_category_id"},
    # )
    # sub_categories: list["ProductCategory"] = Relationship(
    #     back_populates="parent_category"
    # )

    # one-to-many Relationship to Product
    products: list["Product"] = Relationship(back_populates="product_category")


class Product(SQLModel, table=True):
    __tablename__ = "Product"

    product_id: int = Field(primary_key=True, alias="ProductID", nullable=False)
    name: str = Field(..., max_length=100, nullable=False)
    product_number: str = Field(..., max_length=50, nullable=False)
    color: str | None = Field(default=None, max_length=30)

    standard_cost: Decimal = Field(..., nullable=False)
    list_price: Decimal = Field(..., nullable=False)

    size: str | None = Field(default=None, max_length=10)
    weight: Decimal | None = Field(default=None)

    product_category_id: int | None = Field(
        default=None, foreign_key="ProductCategory.ProductCategoryID"
    )
    product_model_id: int | None = Field(
        default=None, foreign_key="ProductModel.ProductModelID"
    )

    sell_start_date: datetime = Field(..., nullable=False)
    sell_end_date: datetime | None = Field(default=None)
    discontinued_date: datetime | None = Field(default=None)

    # varbinary(max) → Optional[bytes]
    thumbnail_photo: bytes | None = Field(default=None, alias="ThumbNailPhoto")
    # nvarchar(100)
    thumbnail_photo_file_name: str | None = Field(
        default=None, max_length=100, alias="ThumbnailPhotoFileName"
    )

    rowguid: str = Field(..., max_length=16, nullable=False)
    modified_date: datetime = Field(..., nullable=False)

    # Relationships
    product_category: ProductCategory | None = Relationship(back_populates="products")
    product_model: ProductModel | None = Relationship(back_populates="products")


# API MODELS
## Shared base: contains user-editable fields
## Excludes 'modified_date' as it is NEVER set by the user but by the back-end
class ProductBase(SQLModel):
    name: str = Field(..., min_length=1, max_length=100)
    product_number: str = Field(..., min_length=1, max_length=50)
    color: str | None = Field(default=None, min_length=1, max_length=30)
    standard_cost: Decimal = Field(..., gt=0, description="Must be strictly positive")
    list_price: Decimal = Field(..., gt=0, description="Must be strictly positive")
    size: str | None = Field(default=None, max_length=10)
    weight: Decimal | None = Field(default=None, gt=0)
    # Foreign keys
    product_category_id: int | None = None
    product_model_id: int | None = None
    # Dates
    sell_start_date: datetime
    sell_end_date: datetime | None = None
    discontinued_date: datetime | None = None
    # Thumbnail
    thumbnail_photo: bytes | None = None
    thumbnail_photo_file_name: str | None = Field(None, max_length=100)
    # Unique identifier, stored as a string but validated as a UUID
    rowguid: str
    
    # Custom validators
    @validator("list_price")
    def validate_list_price(cls, v, values):
        """Ensure list_price > standard_cost (if provided)."""
        standard_cost = values.get("standard_cost")
        if standard_cost is not None and v < standard_cost:
            raise ValueError("list price must be greater than standard_cost")
        return v
    
    @validator("sell_end_date")
    def validate_sell_end_date(cls, v, values):
        """
        If sell_end_date is provide, ensure it's after sell_start_date.
        """
        start = values.get("sell_start_date")
        if v and start and v < start:
            raise ValueError("sell_end_date must be after sell_start_date")
        return v
    
    @validator("discontinued_date")
    def validate_discontinued_date(cls, v, values):
        """
        If discontinued_date is provided, ensure it's after sell_start_date.
        """
        start = values.get("sell_start_date")
        if v and start and v < start:
            raise ValueError("discontinued_date must be after sell_start_date")
        return v
    
    @validator("rowguid")
    def validate_rowguid(cls, v, values):
        """Check that rowguid is a valid UUID string."""
        try:
            UUID(v)  # attempt to parse as a UUID
        except ValueError:
            raise ValueError("rowguid must be a valid UUID string")
        return v    


class ProductCreate(ProductBase):
    """
    For POST /products
    - Same as ProductBase,
      meaning the client must provide all required fields
      except anything we handle automatically (like modified_date).
    """
    pass


    """
    For GET responses
    - Include the DB primary key (product_id)
    - Also show modified_date if we want to return it.
    """
    product_id: int
    modified_date: datetime


class ProductRead(ProductBase):
    """
    For GET responses
    - Include the DB primary key (product_id)
    - Also show modified_date in the response.
    """
    product_id: int
    modified_date: datetime


class ProductUpdate(SQLModel):
    """
    For PUT /products/{id}
    - Partial updates are possible
    - So we make everything optional, with the same validation approach.
    """
    name: str | None = Field(default=None, min_length=1, max_length=100)
    product_number: str | None = Field(default=None, min_length=1, max_length=50)
    color: str | None = Field(default=None, min_length=1, max_length=30)
    standard_cost: Decimal | None = Field(default=None, gt=0)
    list_price: Decimal | None = Field(default=None, gt=0)
    size: str | None = Field(default=None, max_length=10)
    weight: Decimal | None = Field(default=None, gt=0)
    product_category_id: int | None = None
    product_model_id: int | None = None
    sell_start_date: datetime | None = None
    sell_end_date: datetime | None = None
    discontinued_date: datetime | None = None
    thumbnail_photo: bytes | None = None
    thumbnail_photo_file_name: str | None = Field(default=None, max_length=100)
    rowguid: str | None = None
    
    @validator("list_price")
    def validate_list_price(cls, v, values):
        """
        For partial updates, if standard_cost is also present in the update,
        ensure list_price >= standard_cost.
        """
        if v is None:
            return v
        
        standard_cost = values.get("standard_cost")
        
        if standard_cost is not None and v < standard_cost:
            raise ValueError(
                "list_price must be greater than or equal to standard cost.")
        return v
    
    @validator("sell_end_date")
    def validate_sell_end_date(cls, v, values):
        """
        For partial updates, if user is sending a sell_end_date,
        ensure it's after sell_start_date if that was also updated.
        """
        if v is None:
            return v

        start = values.get("sell_start_date")
        if start is not None and v < start:
            raise ValueError("sell_end_date must be after sell_start_date")
        return v

    @validator("discontinued_date")
    def validate_discontinued_date(cls, v, values):
        """
        If discontinued_date is provided, ensure it's after sell_start_date.
        """
        if v is None:
            return v

        start = values.get("sell_start_date")
        if start is not None and v < start:
            raise ValueError("discontinued_date must be after sell_start_date")
        return v

    @validator("rowguid")
    def validate_rowguid(cls, v):
        """
        If user is sending rowguid in an update, ensure it's a valid UUID string.
        """
        if v is None:
            return v
        try:
            UUID(v)
        except ValueError:
            raise ValueError("rowguid must be a valid UUID string")
        return v

from datetime import datetime
from decimal import Decimal

from sqlmodel import SQLModel, Field, Relationship


from datetime import datetime
from sqlmodel import SQLModel, Field


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

    # Self-referential Relationship: sub-categories and parent
    parent_category: "ProductCategory" | None = Relationship(
        back_populates="sub_categories",
        sa_relationship_kwargs={"remote_side": "ProductCategory.product_category_id"},
    )
    sub_categories: list["ProductCategory"] = Relationship(
        back_populates="parent_category"
    )

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
    name: str
    product_number: str
    color: str | None = None
    standard_cost: Decimal
    list_price: Decimal
    size: str | None = None
    weight: Decimal | None = None
    product_category_id: int | None = None
    product_model_id: int | None = None
    sell_start_date: datetime
    sell_end_date: datetime | None = None
    discontinued_date: datetime | None = None
    thumbnail_photo: bytes | None = None
    thumbnail_photo_file_name: str | None = None
    rowguid: str


## For CREATING a product with a POST (/products)
## All fields are required, unless optional in the base
class ProductCreate(ProductBase):
    pass


## For READING a product with a GET (/products or /products/{product_id})
## Includes 'product_id' and 'modified_date'
class ProductRead(ProductBase):
    product_id: int
    modified_date: datetime


## For UPDATING a product with a PUT (/products/{product_id})
## Fields are optional, as updates can be partial
class ProductUpdate(SQLModel):
    name: str | None = None
    product_number: str | None = None
    color: str | None = None
    standard_cost: Decimal | None = None
    list_price: Decimal | None = None
    size: str | None = None
    weight: Decimal | None = None
    product_category_id: int | None = None
    product_model_id: int | None = None
    sell_start_date: datetime | None = None
    sell_end_date: datetime | None = None
    discontinued_date: datetime | None = None
    thumbnail_photo: bytes | None = None
    thumbnail_photo_file_name: str | None = None
    rowguid: str | None = None

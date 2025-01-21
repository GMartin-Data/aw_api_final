from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import validator
from sqlmodel import SQLModel, Field, Relationship


# TABLE MODELS
class ProductModelProductDescription(SQLModel, table=True):
    """Junction table for many-to-many relationship between ProductModel and ProductDescription."""

    __tablename__ = "ProductModelProductDescription"
    __table_args__ = {"schema": "SalesLT"}

    product_model_id: int = Field(
        sa_column_kwargs={"name": "ProductModelID"},
        foreign_key="SalesLT.ProductModel.ProductModelID",
        primary_key=True,
        nullable=False,
    )
    product_description_id: int = Field(
        sa_column_kwargs={"name": "ProductDescriptionID"},
        foreign_key="SalesLT.ProductDescription.ProductDescriptionID",
        primary_key=True,
        nullable=False,
    )
    # Culture is also part of the PK in the AdventureWorksLT schema
    culture: str = Field(
        sa_column_kwargs={"name": "Culture"},
        max_length=12,
        primary_key=True,
        nullable=False,
    )
    rowguid: str = Field(
        sa_column_kwargs={"name": "rowguid"}, max_length=16, nullable=False
    )
    modified_date: datetime = Field(
        sa_column_kwargs={"name": "ModifiedDate"},
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )


class ProductDescription(SQLModel, table=True):
    __tablename__ = "ProductDescription"
    __table_args__ = {"schema": "SalesLT"}

    product_description_id: int = Field(
        sa_column_kwargs={"name": "ProductDescriptionID"},
        primary_key=True,
        nullable=False,
    )
    description: str = Field(
        sa_column_kwargs={"name": "Description"}, max_length=800, nullable=False
    )
    rowguid: str = Field(
        sa_column_kwargs={"name": "rowguid"}, max_length=16, nullable=False
    )
    modified_date: datetime = Field(
        sa_column_kwargs={"name": "ModifiedDate"},
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Many-to-many Relationship back to ProductModel
    models: list["ProductModel"] = Relationship(
        back_populates="descriptions", link_model=ProductModelProductDescription
    )


class ProductModel(SQLModel, table=True):
    __tablename__ = "ProductModel"
    __table_args__ = {"schema": "SalesLT"}

    product_model_id: int = Field(
        sa_column_kwargs={"name": "ProductModelID"},
        primary_key=True,
        alias="ProductModelID",
        nullable=False,
    )
    name: str = Field(sa_column_kwargs={"name": "Name"}, max_length=100, nullable=False)
    # 'CatalogDescription' is xml, so we can store it as an optional string
    catalog_description: str | None = Field(
        sa_column_kwargs={"name": "CatalogDescription"},
        default=None,
        description="XML-formatted catalog description",
    )
    rowguid: str = Field(
        sa_column_kwargs={"name": "rowguid"}, max_length=16, nullable=False
    )
    modified_date: datetime = Field(
        sa_column_kwargs={"name": "ModifiedDate"},
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # one-to many Relationship to Product:
    products: list["Product"] = Relationship(
        back_populates="product_model",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    # many-to-many Relationship to ProductDescription
    descriptions: list[ProductDescription] = Relationship(
        back_populates="models", link_model=ProductModelProductDescription
    )


class ProductCategory(SQLModel, table=True):
    __tablename__ = "ProductCategory"
    __table_args__ = {"schema": "SalesLT"}

    product_category_id: int = Field(
        sa_column_kwargs={"name": "ProductCategoryID"}, primary_key=True, nullable=False
    )
    parent_product_category_id: int | None = Field(
        sa_column_kwargs={"name": "ParentProductCategoryID"},
        default=None,
        foreign_key="SalesLT.ProductCategory.ProductCategoryID",
    )
    name: str = Field(sa_column_kwargs={"name": "Name"}, max_length=100, nullable=False)
    rowguid: str = Field(
        sa_column_kwargs={"name": "rowguid"}, max_length=16, nullable=False
    )
    modified_date: datetime = Field(
        sa_column_kwargs={"name": "ModifiedDate"},
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Self-referential Relationship: sub-categories and parent
    # ⚠️ Commmented as they cause unsolved issues when API running
    parent_category: Optional["ProductCategory"] = Relationship(
        sa_relationship_kwargs={
            "remote_side": "ProductCategory.product_category_id",
            "primaryjoin": "ProductCategory.parent_product_category_id==ProductCategory.product_category_id",
        },
        back_populates="sub_categories",
    )
    sub_categories: list["ProductCategory"] = Relationship(
        sa_relationship_kwargs={
            "primaryjoin": "ProductCategory.parent_product_category_id==ProductCategory.product_category_id"
        },
        back_populates="parent_category",
    )
    # one-to-many Relationship to Product
    products: list["Product"] = Relationship(
        back_populates="product_category",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Product(SQLModel, table=True):
    """
    Core product information in the AdventureWorks system. This model represents
    individual products that can be sold, tracking their basic information,
    pricing, dates, and relationships to categories and models.
    """

    __tablename__ = "Product"
    __table_args__ = {"schema": "SalesLT"}

    product_id: int = Field(
        sa_column_kwargs={"name": "ProductID"}, primary_key=True, nullable=False
    )
    name: str = Field(sa_column_kwargs={"name": "Name"}, max_length=100, nullable=False)
    product_number: str = Field(
        sa_column_kwargs={"name": "ProductNumber"}, max_length=50, nullable=False
    )
    # Physical characteristics
    color: str | None = Field(
        sa_column_kwargs={"name": "Color"}, default=None, max_length=30
    )
    size: str | None = Field(
        sa_column_kwargs={"name": "Size"}, default=None, max_length=10
    )
    weight: Decimal | None = Field(
        sa_column_kwargs={"name": "Weight"},
        default=None,
        # Scale and precision for decimal type
        decimal_places=2,
        max_digits=8,
    )
    # Financial information
    # Financial information
    standard_cost: Decimal = Field(
        sa_column_kwargs={"name": "StandardCost"},
        nullable=False,
        decimal_places=4,  # Money type in SQL Server
        max_digits=19,
    )
    list_price: Decimal = Field(
        sa_column_kwargs={"name": "ListPrice"},
        nullable=False,
        decimal_places=4,
        max_digits=19,
    )
    # Categorization foreign keys
    product_category_id: int | None = Field(
        sa_column_kwargs={"name": "ProductCategoryID"},
        foreign_key="SalesLT.ProductCategory.ProductCategoryID",
        default=None,
    )
    product_model_id: int | None = Field(
        sa_column_kwargs={"name": "ProductModelID"},
        foreign_key="SalesLT.ProductModel.ProductModelID",
        default=None,
    )
    # Lifecycle dates
    sell_start_date: datetime = Field(
        sa_column_kwargs={"name": "SellStartDate"}, nullable=False
    )
    sell_end_date: datetime | None = Field(
        sa_column_kwargs={"name": "SellEndDate"}, default=None
    )
    discontinued_date: datetime | None = Field(
        sa_column_kwargs={"name": "DiscontinuedDate"}, default=None
    )
    # Product image
    ## varbinary(max) → Optional[bytes]
    thumbnail_photo: bytes | None = Field(
        sa_column_kwargs={"name": "ThumbNailPhoto"}, default=None
    )
    ## nvarchar(100)
    thumbnail_photo_file_name: str | None = Field(
        sa_column_kwargs={"name": "ThumbnailPhotoFileName"},
        default=None,
        max_length=100,
    )
    # Record management
    rowguid: UUID = Field(sa_column_kwargs={"name": "rowguid"}, nullable=False)
    modified_date: datetime = Field(
        sa_column_kwargs={"name": "ModifiedDate"},
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # Relationships
    product_category: ProductCategory | None = Relationship(back_populates="products")
    product_model: ProductModel | None = Relationship(back_populates="products")


# API MODELS
## Shared base: contains user-editable fields
## Excludes 'modified_date' as it is NEVER set by the user but by the back-end
class ProductBase(SQLModel):
    """
    Base model for product API interactions, defining common fields and validation rules.
    This model serves as a foundation for both creating and reading products, ensuring
    consistent validation across our API.
    """

    # Core project information
    name: str = Field(
        min_length=1,  # Ensure non-empty strings
        max_length=100,
        description="Product name, required and non-empty",
    )
    product_number: str = Field(
        min_length=1,
        max_length=50,
        description="Unique product identifier, required and non-empty",
    )

    # Physical characteristics - all optional except pricing
    color: str | None = Field(
        default=None,
        min_length=1,  # If provided, must not be empty
        max_length=30,
        description="Product color, optional",
    )
    size: str | None = Field(
        default=None, max_length=10, description="Product size, optional"
    )
    weight: Decimal | None = Field(
        default=None,
        gt=0,  # If provided, must be positive
        description="Product weight in appropriate units, optional",
    )

    # Pricing - required and must be positive
    standard_cost: Decimal = Field(
        gt=0, description="Manufacturing or acquisition cost, must be positive"
    )
    list_price: Decimal = Field(
        gt=0, description="Selling price, must be greater than standard cost"
    )

    # Categorization - optional foreign keys
    product_category_id: int | None = Field(
        default=None, gt=0, description="Reference to product category, optional"
    )
    product_model_id: int | None = Field(
        default=None, gt=0, description="Reference to product model, optional"
    )

    # Lifecycle dates
    sell_start_date: datetime = Field(
        description="Date when product becomes available for sale"
    )
    sell_end_date: datetime | None = Field(
        default=None, description="Date when product is no longer available for sale"
    )
    discontinued_date: datetime | None = Field(
        default=None, description="Date when product is discontinued"
    )

    # Product image - optional
    thumbnail_photo: bytes | None = Field(
        default=None, description="Product thumbnail image as binary data"
    )
    thumbnail_photo_file_name: str | None = Field(
        default=None, max_length=100, description="Filename for the thumbnail photo"
    )

    # Unique identifier, required, stored as a string but validated as a UUID
    rowguid: str = Field(description="Unique identifier for record tracking")

    # Custom validators
    @validator("list_price")
    def validate_list_price(cls, v, values) -> Decimal:
        """Ensure list_price is greater than standard_cost (if provided)."""
        standard_cost = values.get("standard_cost")
        if standard_cost is not None and v <= standard_cost:
            raise ValueError(
                f"List price ({v}) must be greater than standard cost ({standard_cost})"
            )

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
    Model for creating new products through POST /products endpoint.

    This model inherits all fields from ProductBase but excludes any
    server-generated fields (like modified_date). All required fields
    must be provided by the client when creating a new product,
    ensuring data completeness from the start.

    Example:
        {
            "name": "New Mountain Bike",
            "product_number": "MB-NEW-20",
            "standard_cost": "500.00",
            "list_price": "899.99",
            "sell_start_date": "2025-01-01T00:00:00Z",
            "rowguid": "123e4567-e89b-12d3-a456-426614174000"
        }
    """

    pass


class ProductRead(ProductBase):
    """
    Model for product data returned by GET endpoints.

    Extends ProductBase to include server-generated fields that clients
    need to see but can't set themselves. This creates a clear distinction
    between writable and read-only fields in our API.

    The modified_date field helps clients track when products were last updated,
    useful for caching and synchronization purposes.
    """

    product_id: int = Field(description="Database-generated product identifier")
    modified_date: datetime = Field(description="Timestamp of last modification")


class ProductUpdate(SQLModel):
    """
    Model for updating existing products through PUT /products/{id}.

    All fields are optional, allowing partial updates. Each field's
    validation rules match those in ProductBase, but only provided
    fields will be updated. This follows the principle of making
    updates as flexible as possible while maintaining data integrity.

    Example partial update:
        {
            "list_price": "999.99",
            "color": "Metallic Red"
        }
    """

    # Core information - all optional for updates
    name: str | None = Field(
        default=None,
        min_length=1,
        max_length=100,
        description="New product name"
    )
    product_number: str | None = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="New product number"
    )
    
    # Physical characteristics
    color: str | None = Field(
        default=None,
        min_length=1,
        max_length=30,
        description="New color"
    )
    size: str | None = Field(
        default=None,
        max_length=10,
        description="New size"
    )
    weight: Decimal | None = Field(
        default=None,
        gt=0,
        description="New weight"
    )
    
    # Pricing
    standard_cost: Decimal | None = Field(
        default=None,
        gt=0,
        description="New standard cost"
    )
    list_price: Decimal | None = Field(
        default=None,
        gt=0,
        description="New list price"
    )
    
    # Categorization
    product_category_id: int | None = Field(
        default=None,
        gt=0,
        description="New category reference"
    )
    product_model_id: int | None = Field(
        default=None,
        gt=0,
        description="New model reference"
    )
    
    # Lifecycle dates
    sell_start_date: datetime | None = Field(
        default=None,
        description="New sell start date"
    )
    sell_end_date: datetime | None = Field(
        default=None,
        description="New sell end date"
    )
    discontinued_date: datetime | None = Field(
        default=None,
        description="New discontinued date"
    )
    
    # Product image
    thumbnail_photo: bytes | None = Field(
        default=None,
        description="New thumbnail image"
    )
    thumbnail_photo_file_name: str | None = Field(
        default=None,
        max_length=100,
        description="New thumbnail filename"
    )
    
    # Record management
    rowguid: str | None = Field(
        default=None,
        description="New row GUID"
    )

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
                "list_price must be greater than or equal to standard cost."
            )
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

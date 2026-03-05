"""
Employee database model.
Defines the SQLModel table structure for the Employee entity.
"""

from sqlmodel import Field, SQLModel


class Employee(SQLModel, table=True):
    """
    Employee database table model.
    Represents the employee table in the database with all required fields.
    """

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255, nullable=False)
    age: int | None = Field(default=None, ge=0, le=150, nullable=True)

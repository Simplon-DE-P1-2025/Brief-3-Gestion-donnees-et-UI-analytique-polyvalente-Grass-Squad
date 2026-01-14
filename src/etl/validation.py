import pandera as pa
from pandera import Column, DataFrameSchema, Check

# Define schema for operations
operations_schema = DataFrameSchema({
    "operation_id": Column(int, nullable=False, required=True),
    "latitude": Column(float, nullable=True, checks=Check.in_range(-90, 90)),
    "longitude": Column(float, nullable=True, checks=Check.in_range(-180, 180)),
    "vent_direction": Column(float, nullable=True, checks=Check.in_range(0, 360)),
    # Add other checks as needed
}, coerce=True)

def validate_operations(df):
    """
    Validates the operations dataframe against schema.
    Returns the dataframe if valid, raises SchemaError otherwise.
    """
    return operations_schema.validate(df)

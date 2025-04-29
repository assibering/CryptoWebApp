from pydantic import BaseModel
from typing import Any, Dict, Type

def transform_basemodel_field_to_dynamodb_field(
    value: Any,
    add_empty_string_to_stringsets: bool = False
) -> Any:
        if isinstance(value, str):
            return {"S": value}  # String
        elif isinstance(value, bool):
            return {"BOOL": value}  # Boolean
        elif isinstance(value, (int, float)):
            return {"N": str(value)}  # Number
        elif isinstance(value, set):
            if add_empty_string_to_stringsets:
                return {"SS": list(value)+[""]}  # Set of Strings
            return {"SS": list(value)}
        elif isinstance(value, list):
            return {"L": [transform_basemodel_field_to_dynamodb_field(item) for item in value]}  # List
        elif isinstance(value, dict):
            return {"M": {key: transform_basemodel_field_to_dynamodb_field(val) \
                          for key, val in value.items()}}  # Map
        else:
            raise TypeError(f"Unsupported type: {type(value)} for value: {value}")

def transform_dynamodb_field_to_basemodel_field(
        value: Any,
        include_empty_string_in_stringsets: bool = False
    ) -> Any:
        if isinstance(value, dict):
            if "S" in value:
                return value["S"]  # String
            elif "BOOL" in value:
                return value["BOOL"]  # Boolean
            elif "N" in value:
                return float(value["N"]) if '.' in value["N"] else int(value["N"])  # Number (integer or float)
            elif "SS" in value:
                if include_empty_string_in_stringsets:
                    return set(value["SS"])
                return set(value["SS"]).difference({""})  # Set of Strings
            elif "L" in value:
                return [transform_dynamodb_field_to_basemodel_field(item) \
                        for item in value["L"]]  # List
            elif "M" in value:
                return {key: transform_dynamodb_field_to_basemodel_field(val) \
                        for key, val in value["M"].items()}  # Nested Map
            else:
                return value  # In case of unexpected structure
        return value  # If it's not a dict, return it as is


async def basemodel_to_dynamodb(
    basemodel: BaseModel,
    add_empty_string_to_stringsets: bool = False
) -> Dict[str, Any]:
    """
    Convert a Pydantic BaseModel instance into a DynamoDB-compatible dictionary.

    Args:
        basemodel (BaseModel): The Pydantic BaseModel instance.

    Returns:
        Dict[str, Any]: A dictionary formatted for DynamoDB.
    """
    # Convert the model to a dictionary and transform it
    return {key: transform_basemodel_field_to_dynamodb_field(value, add_empty_string_to_stringsets) \
            for key, value in basemodel.model_dump().items() if value is not None}

async def dynamodb_to_basemodel(
        basemodel: Type[BaseModel],
        dynamodb_data: Dict[str, Any],
        include_empty_string_in_stringsets: bool = False
    ) -> BaseModel:
    """
    Convert a DynamoDB response body into Python data types and populate a Pydantic BaseModel.

    Args:
        basemodel (Type[BaseModel]): The Pydantic model class.
        dynamodb_data (Dict[str, Any]): The DynamoDB response.

    Returns:
        BaseModel: An instance of the Pydantic BaseModel filled with transformed data.
    """
    # Validate and return the BaseModel instance
    try:
        return basemodel.model_validate(
            {key: transform_dynamodb_field_to_basemodel_field(value, include_empty_string_in_stringsets) \
              for key, value in dynamodb_data.items()}
        )
    except Exception as e:
        raise ValueError(f"Error validating data against {basemodel.__name__}: {str(e)}")

async def get_key(
        pkey_name: str,
        pkey_value: str | int,
        skey_name: str = None,
        skey_value: str | int = None
    ) -> dict:
    '''
    This function generates the key schema, i.e. which item to retrieve/update/delete etc.
    '''
    key = {}
    if isinstance(pkey_value, str):
        key[pkey_name] = {'S': pkey_value}
    elif isinstance(pkey_value, int):
        key[pkey_name] = {'N': str(pkey_value)}
    else:
        raise TypeError(f"Unsupported type for partition key value: {type(pkey_value)}")
    
    if skey_name:
        if not skey_value:
            raise ValueError("No value provided for sort key")
        else:
            if isinstance(skey_value, str):
                key[skey_name] = {'S': skey_value}
            elif isinstance(skey_value, int):
                key[skey_name] = {'N': skey_value}
            else:
                raise TypeError(f"Unsupported type for sort key value: {type(skey_value)}")
    
    return key
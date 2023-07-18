import boto3
import json
import logging
from custom_encoder import CustomEncoder

# Create a logger and set its logging level to INFO
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Define the name of the DynamoDB table
dynamodbTableName = "product-inventory"

# Create a DynamoDB resource object using boto3
dynamodb = boto3.resource("dynamodb")

# Retrieve the DynamoDB table using the resource object and table name
table = dynamodb.Table(dynamodbTableName)

# Define HTTP methods and paths
getMethod = "GET"
postMethod = "POST"
patchMethod = "PATCH"
deleteMethod = "DELETE"
healthPath = "/health"
productPath = "/product"
productsPath = "/products"

# Lambda handler function that handles the incoming event and context
def lambda_handler(event, context):
    # Log the event object
    logger.info(event)

    # Extract the HTTP method and path from the event
    httpMethod = event["httpMethod"]
    path = event["path"]

    # Perform actions based on the HTTP method and path
    if httpMethod == getMethod and path == healthPath:
        # If the method is GET and the path is /health, return a 200 response
        response = build_response(200)
    elif httpMethod == getMethod and path == productPath:
        # If the method is GET and the path is /product, retrieve a single product
        # based on the productId provided in the query string parameters
        response = get_product(event["queryStringParameters"]["productId"])
    elif httpMethod == getMethod and path == productsPath:
        # If the method is GET and the path is /products, retrieve all products
        response = get_products()
    elif httpMethod == postMethod and path == productPath:
        # If the method is POST and the path is /product, save a new product
        # based on the JSON data provided in the request body
        response = save_product(json.loads(event["body"]))
    elif httpMethod == patchMethod and path == productPath:
        # If the method is PATCH and the path is /product, modify an existing product
        # based on the productId, updateKey, and updateValue provided in the request body
        requestBody = json.loads(event["body"])
        response = modify_product(requestBody['productId'], requestBody['updateKey'], requestBody['updateValue'])
    elif httpMethod == deleteMethod and path == productPath:
        # If the method is DELETE and the path is /product, delete a product
        # based on the productId provided in the request body
        requestBody = json.loads(event["body"])
        response = delete_product(requestBody['productId'])
    else:
        # If no matching route is found, return a 404 response
        response = build_response(404, "404 Not Found")

    # Return the response
    return response


def get_product(product_id):
    try:
        # Retrieve a single item from the DynamoDB table using the productId as the key
        response = table.get_item(Key={'productId': product_id})

        # Check if the item is found in the response
        if "Item" in response:
            # If the item is found, return a 200 response with the item data
            return build_response(200, response['Item'])
        else:
            # If the item is not found, return a 404 response with an error message
            return build_response(404, {'message': 'productId: %s is not found' % product_id})
    except Exception as e:
        # If an exception occurs, log the exception and return an error response
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')


def get_products():
    try:
        # Perform a scan operation on the DynamoDB table to retrieve all items
        response = table.scan()
        result = response['Items']

        # Continue scanning the table if there are more items to fetch
        while "LastEvaluatedKey" in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])

        # Build a response body containing the retrieved products
        body = {
            'products': result
        }

        # Return a 200 response with the response body
        return build_response(200, body)
    except Exception as e:
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')


def save_product(request_body):
    try:
        # Save a new item in the DynamoDB table using the provided request body as the item data
        table.put_item(Item=request_body)

        # Build a response body indicating the success of the operation
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': request_body
        }

        # Return a 200 response with the response body
        return build_response(200, body)
    except Exception as e:
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')


def modify_product(product_id, update_key, update_value):
    try:
        # Update an existing item in the DynamoDB table using the provided product_id, update_key, and update_value
        response = table.update_item(
            Key={'productId': product_id},
            UpdateExpression='Set %s = :value' % update_key,
            ExpressionAttributeValues={':value': update_value},
            ReturnValues='UPDATED_NEW'
        )

        # Build a response body indicating the success of the operation and the updated attributes
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }

        # Return a 200 response with the response body
        return build_response(200, body)
    except Exception as e:
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')


def modify_product(product_id, update_key, update_value):
    try:
        # Update an existing item in the DynamoDB table using the provided product_id, update_key, and update_value
        response = table.update_item(
            Key={'productId': product_id},
            UpdateExpression='Set %s = :value' % update_key,
            ExpressionAttributeValues={':value': update_value},
            ReturnValues='UPDATED_NEW'
        )

        # Build a response body indicating the success of the operation and the updated attributes
        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdatedAttributes': response
        }

        # Return a 200 response with the response body
        return build_response(200, body)
    except Exception as e:
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')


def delete_product(product_id):
    try:
        # Delete an item from the DynamoDB table using the provided product_id
        response = table.delete_item(
            Key={'productId': product_id},
            ReturnValues='ALL_OLD'
        )

        # Build a response body indicating the success of the operation and the deleted item
        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }

        # Return a 200 response with the response body
        return build_response(200, body)
    except Exception as e:
        logger.exception('Do your custom error handling here. I am just gonna log it out here!!')


def build_response(status_code, body=None):
    # Build a response dictionary with the provided status code
    response = {
        "statusCode": status_code,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }

    if body is not None:
        # If a response body is provided, convert it to JSON using a custom encoder (CustomEncoder)
        # and assign it to the 'body' key in the response dictionary
        response["body"] = json.dumps(body, cls=CustomEncoder)

    # Return the response dictionary
    return response


    response = {
        "statusCode": status_code,
        "headers": {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        }
    }


    if body is not None:
        # If a response body is provided, convert it to JSON using a custom encoder (CustomEncoder)
        # and assign it to the 'body' key in the response dictionary
        response["body"] = json.dumps(body, cls=CustomEncoder)


    # Return the response dictionary
    return response

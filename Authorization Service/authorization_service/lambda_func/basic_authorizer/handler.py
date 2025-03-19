# authorization_service/lambda_functions/basic_authorizer/handler.py
import os
import json
import base64

def lambda_handler(event, context):
    print(f"Event: {json.dumps(event)}")
    authorization_header = event['authorizationToken']

    if 'authorizationToken' not in event:
        return {
            'statusCode':401,
            'body': json.dumps({
                'message': 'Unauthorized'
            })'
        }
        
        #generate_policy('undefined', 'Deny', event['methodArn'])

    try:
        # Encode Credentials
        # Get token from Authorization header
        token = event['authorizationToken'].split(' ')[1]
        
        
        # Decode credentials
        decoded = base64.b64decode(token).decode('utf-8')
        username, password = decoded.split(':')
        password = password.strip()

        # Get stored credentials from environment
        # stored_username = os.environ.get('AUTH_USER')
        # stored_password = os.environ.get('AUTH_PASSWORD')
        stored_credentials = os.getenv(username)

        # Verify credentials
        if username == stored_username and password == stored_password:
            effect = 'Allow'
        else:
            effect = 'Deny'

        return generate_policy(token, effect, event['methodArn'])

    except Exception as e:
        print(f"Error: {str(e)}")
        return generate_policy('undefined', 'Deny', event['methodArn'])

def generate_policy(principal_id: str, effect: str, resource: str) -> dict:
    """Generate IAM policy for API Gateway authorization"""
    return {
        'principalId': principal_id,
        'policyDocument': {
            'Version': '2012-10-17',
            'Statement': [{
                'Action': 'execute-api:Invoke',
                'Effect': effect,
                'Resource': resource
            }]
        }
    }

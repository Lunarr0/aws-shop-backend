from aws_cdk import (
    aws_lambda as _lambda,
    aws_s3 as s3,
    aws_s3_notifications as s3n,
    Duration,
    aws_iam as iam
)
from constructs import Construct

def create_parse_products_lambda(
    scope: Construct, 
    import_bucket: s3.IBucket
) -> _lambda.Function:

    # Create importFileParser Lambda
    import_file_parser = _lambda.Function(
        scope, 'ImportFileParser',
        runtime=_lambda.Runtime.PYTHON_3_9,
        handler='import_file_parser.lambda_handler',
        code=_lambda.Code.from_asset('import_service/lambda_func/'),
        environment={
            'BUCKET_NAME': import_bucket.bucket_name
        },
        timeout=Duration.seconds(60),
        memory_size=256
    )

    # Grant S3 permissions to Lambda
    import_bucket.grant_read(import_file_parser)
    import_bucket.grant_write(import_file_parser)
    import_bucket.grant_put(import_file_parser)
    import_bucket.grant_delete(import_file_parser)

    # Add S3 notification for the uploaded/ prefix
    import_bucket.add_event_notification(
        s3.EventType.OBJECT_CREATED,
        s3n.LambdaDestination(import_file_parser),
        s3.NotificationKeyFilter(prefix='uploaded/')
    )

    # Add Lambda permissions for S3 invocation
    import_file_parser.add_permission(
        'AllowS3Invoke',
        principal=iam.ServicePrincipal('s3.amazonaws.com'),
        action='lambda:InvokeFunction',
        source_arn=import_bucket.bucket_arn
    )

    return import_file_parser

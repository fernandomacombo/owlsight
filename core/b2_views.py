import os, uuid
import boto3
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # depois podemos trocar por auth + csrf certinho
@require_POST
def presign_upload(request):
    filename = request.POST.get("filename", "file.pdf")
    content_type = request.POST.get("content_type", "application/pdf")

    key = f"uploads/books/{uuid.uuid4()}-{filename}"

    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"),
        region_name=os.getenv("AWS_S3_REGION_NAME", "us-east-1"),
    )

    bucket = os.getenv("AWS_STORAGE_BUCKET_NAME")

    presigned = s3.generate_presigned_post(
        Bucket=bucket,
        Key=key,
        Fields={"Content-Type": content_type},
        Conditions=[{"Content-Type": content_type}],
        ExpiresIn=3600,
    )

    return JsonResponse({"key": key, "url": presigned["url"], "fields": presigned["fields"]})
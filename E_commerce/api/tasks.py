import zipfile
import os
import pandas as pd
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from celery import shared_task
from .models import ProductModel, CategoryModel, UploadProduct
from django.core.files.storage import default_storage
import requests
import shutil
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# List of expected CSV headers
expected_headers = ["Product_Name", "Category_Name", "Product_Price", "Product_Unit", "Product_Stock", "Product_Desc", "Product_IMG"]

@shared_task
def process_product_csv(file_path, user_email=None):
    logger.info(f"Processing CSV file: {file_path}")
    status_report = []
    created_count = 0
    updated_count = 0
    failed_count = 0

    try:
        # Read the CSV file
        df = pd.read_csv(file_path)

        # Check headers
        if not all(header in df.columns for header in expected_headers):
            raise ValueError("CSV headers are not properly formatted")

        for index, row in df.iterrows():
            try:
                # Find the category by name
                category = CategoryModel.objects.filter(category=row["Category_Name"]).first()
                if not category:
                    raise ValueError(f"Invalid category name: {row['Category_Name']}")

                # Resolve image path (URL or local path)
                img_path_or_url = row["Product_IMG"]
                img_file = None

                # Handle image URL
                if img_path_or_url.startswith("http"):
                    response = requests.get(img_path_or_url)
                    if response.status_code != 200:
                        raise ValueError(f"Image URL not accessible: {img_path_or_url}")
                    img_file = ContentFile(response.content, name=os.path.basename(img_path_or_url))

                else:
                    img_path = os.path.join(settings.MEDIA_ROOT, 'product_images', img_path_or_url)
                    if not os.path.exists(img_path):
                        raise ValueError(f"Image path does not exist: {img_path}")
                    with open(img_path, "rb") as f:
                        img_file = ContentFile(f.read(), name=os.path.basename(img_path))

                # Save or update the product
                product_obj, created = ProductModel.objects.update_or_create(
                    name=row["Product_Name"],
                    category=category,
                    defaults={
                        "price": row["Product_Price"],
                        "unit": row["Product_Unit"],
                        "stock": row["Product_Stock"],
                        "desc": row["Product_Desc"],
                    }
                )

                # Handle image update (save using default storage backend)
                if img_file:
                    existing_image_name = product_obj.img.name.split("/")[-1]  # Get the current image name
                    new_image_name = img_file.name
                    if existing_image_name != new_image_name:
                        product_obj.img.save(img_file.name, img_file)
                        logger.info(f"Image updated for product: {row['Product_Name']}")

                action = "Created" if created else "Updated"
                status_report.append(row.to_dict())
                status_report[-1]["Remark"] = action

                # Update counts
                if created:
                    created_count += 1
                else:
                    updated_count += 1

            except Exception as e:
                logger.error(f"Row {index + 1} failed: {e}")
                row_data = row.to_dict()
                row_data["Remark"] = f"Failed: {str(e)}"
                status_report.append(row_data)
                failed_count += 1

        # Generate and save status report
        status_df = pd.DataFrame(status_report)
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        status_file_name = f"product_upload_status_{timestamp}.csv"
        status_file_path = os.path.join(settings.MEDIA_ROOT, "files", status_file_name)
        status_df.to_csv(status_file_path, index=False)

        # Delete the original uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Original CSV file deleted: {file_path}")

        # Send email with the status report
        if user_email:
            try:
                template_path = os.path.join(settings.BASE_DIR, 'api/templates/bulk_product_status_mail.txt')
                with open(template_path, 'r') as template_file:
                    template_content = template_file.read()

                email_body = template_content.format(
                    created_count=created_count,
                    updated_count=updated_count,
                    failed_count=failed_count,
                )

                email = EmailMessage(
                    subject="CSV Product Upload Status Report",
                    body=email_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user_email],
                )
                email.attach_file(status_file_path)
                email.send()
                logger.info(f"Email sent successfully to {user_email}")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")

        logger.info(
            f"CSV processed successfully: Created={created_count}, Updated={updated_count}, Failed={failed_count}. "
            f"Report sent to {user_email}"
        )

    except Exception as e:
        logger.error(f"CSV processing failed: {e}")
        if user_email:
            error_message = f"An error occurred while processing the CSV: {e}"
            email = EmailMessage(
                subject="Error in CSV Product Upload",
                body=error_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user_email],
            )
            email.send()

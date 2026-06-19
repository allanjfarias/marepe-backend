from uuid import uuid4


async def upload_image(
    file,
    vendor_id: str,
    folder: str,
    supabase_client,
):
    extension = file.filename.split(".")[-1]

    file_path = (
        f"{vendor_id}/{folder}/{uuid4()}.{extension}"
    )

    file_bytes = await file.read()

    supabase_client.storage.from_("vendor-media").upload(
        file_path,
        bytes(file_bytes),
        {
            "content-type": file.content_type,
            "upsert": "false"
        }
    )

    return supabase_client.storage.from_(
        "vendor-media"
    ).get_public_url(file_path)
from urllib.parse import quote


def get_or_create_drive_folder(authed_session, folder_name="langdeng"):
    """在 Google Drive 中查找或创建文件夹 (使用 requests 提高稳定性)"""
    # 1. 查找文件夹
    query = (
        f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' "
        f"and trashed = false"
    )
    url = f"https://www.googleapis.com/drive/v3/files?q={quote(query)}&fields=files(id, name)"

    resp = authed_session.get(url)
    resp.raise_for_status()
    items = resp.json().get("files", [])

    if items:
        return items[0]["id"]

    # 2. 不存在则创建
    create_url = "https://www.googleapis.com/drive/v3/files"
    payload = {"name": folder_name, "mimeType": "application/vnd.google-apps.folder"}
    create_resp = authed_session.post(create_url, json=payload)
    create_resp.raise_for_status()

    return create_resp.json().get("id")


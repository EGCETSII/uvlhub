import uuid

from flask import jsonify, make_response, request, send_from_directory
from flask_login import current_user

from app.features.hubfile import hubfile_bp
from app.features.hubfile.services import (
    HubfileDownloadRecordService,
    HubfileService,
    HubfileViewRecordService,
)

hubfile_service = HubfileService()
hubfile_download_record_service = HubfileDownloadRecordService()
hubfile_view_record_service = HubfileViewRecordService()


@hubfile_bp.route("/file/download/<int:file_id>", methods=["GET"])
def download_file(file_id):
    hubfile = hubfile_service.get_or_404(file_id)
    directory = hubfile_service.directory_for(hubfile)

    cookie = request.cookies.get("file_download_cookie") or str(uuid.uuid4())

    resp = make_response(send_from_directory(directory=directory, path=hubfile.name, as_attachment=True))
    hubfile_download_record_service.record_download(current_user, file_id, cookie)
    resp.set_cookie("file_download_cookie", cookie, max_age=60 * 60 * 24 * 365 * 2)
    return resp


@hubfile_bp.route("/file/view/<int:file_id>", methods=["GET"])
def view_file(file_id):
    hubfile = hubfile_service.get_or_404(file_id)
    try:
        content = hubfile_service.read_text(hubfile)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    if content is None:
        return jsonify({"success": False, "error": "File not found"}), 404

    cookie = request.cookies.get("view_cookie") or str(uuid.uuid4())
    hubfile_view_record_service.record_view(current_user, file_id, cookie)

    resp = jsonify({"success": True, "content": content})
    if not request.cookies.get("view_cookie"):
        resp = make_response(resp)
        resp.set_cookie("view_cookie", cookie, max_age=60 * 60 * 24 * 365 * 2)
    return resp

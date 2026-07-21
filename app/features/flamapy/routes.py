import logging

from flask import after_this_request, jsonify, send_file
from werkzeug.exceptions import NotFound

from app.features.flamapy import flamapy_bp
from app.features.flamapy.services import FlamapyService

logger = logging.getLogger(__name__)

flamapy_service = FlamapyService()


@flamapy_bp.route("/flamapy/check_uvl/<int:file_id>", methods=["GET"])
def check_uvl(file_id):
    try:
        errors = flamapy_service.validate_uvl(file_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if errors:
        return jsonify({"errors": errors}), 400
    return jsonify({"message": "Valid Model"}), 200


@flamapy_bp.route("/flamapy/valid/<int:file_id>", methods=["GET"])
def valid(file_id):
    if not flamapy_service.hubfile_exists(file_id):
        return jsonify({"error": f"No hubfile with id {file_id}"}), 404
    try:
        errors = flamapy_service.validate_uvl(file_id)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"success": not errors, "file_id": file_id}), 200


@flamapy_bp.route("/flamapy/to_glencoe/<int:file_id>", methods=["GET"])
def to_glencoe(file_id):
    return _stream_export(file_id, "glencoe")


@flamapy_bp.route("/flamapy/to_splot/<int:file_id>", methods=["GET"])
def to_splot(file_id):
    return _stream_export(file_id, "splot")


@flamapy_bp.route("/flamapy/to_cnf/<int:file_id>", methods=["GET"])
def to_cnf(file_id):
    return _stream_export(file_id, "cnf")


def _stream_export(file_id, target):
    try:
        path, download_name = flamapy_service.export(file_id, target)
    except NotFound:
        return jsonify({"error": f"No hubfile with id {file_id}"}), 404
    except FileNotFoundError:
        return jsonify({"error": "The UVL file is missing from disk"}), 500

    @after_this_request
    def _cleanup(response):
        FlamapyService.cleanup(path)
        return response

    return send_file(path, as_attachment=True, download_name=download_name)

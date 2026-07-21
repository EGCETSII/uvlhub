import logging
import uuid

from flask import (
    abort,
    jsonify,
    make_response,
    redirect,
    render_template,
    request,
    send_from_directory,
    url_for,
)
from flask_login import current_user, login_required

from app.features.dataset import dataset_bp
from app.features.dataset.forms import DataSetForm
from app.features.dataset.services import (
    DataSetService,
    DOIMappingService,
    DSDownloadRecordService,
    DSMetaDataService,
    DSViewRecordService,
)

logger = logging.getLogger(__name__)


dataset_service = DataSetService()
dsmetadata_service = DSMetaDataService()
doi_mapping_service = DOIMappingService()
ds_view_record_service = DSViewRecordService()


@dataset_bp.route("/dataset/upload", methods=["GET"])
@login_required
def create_dataset():
    return render_template("dataset/upload_dataset.html", form=DataSetForm())


@dataset_bp.route("/dataset/upload", methods=["POST"])
@login_required
def upload_dataset():
    form = DataSetForm()
    if not form.validate_on_submit():
        return jsonify({"message": form.errors}), 400

    result = dataset_service.upload_dataset(form=form, current_user=current_user)
    return jsonify({"message": result["message"]}), result["code"]


@dataset_bp.route("/dataset/list", methods=["GET", "POST"])
@login_required
def list_dataset():
    return render_template(
        "dataset/list_datasets.html",
        datasets=dataset_service.get_synchronized(current_user.id),
        local_datasets=dataset_service.get_unsynchronized(current_user.id),
    )


@dataset_bp.route("/dataset/file/upload", methods=["POST"])
@login_required
def upload():
    result = dataset_service.save_temp_uvl(request.files.get("file"), current_user)
    payload = {"message": result["message"]}
    if "filename" in result:
        payload["filename"] = result["filename"]
    return jsonify(payload), result["code"]


@dataset_bp.route("/dataset/file/delete", methods=["POST"])
@login_required
def delete():
    filename = (request.get_json() or {}).get("file")
    result = dataset_service.delete_temp_file(filename, current_user)
    payload = {k: result[k] for k in ("message", "error") if k in result}
    return jsonify(payload), result["code"]


@dataset_bp.route("/dataset/download/<int:dataset_id>", methods=["GET"])
def download_dataset(dataset_id):
    dataset = dataset_service.get_or_404(dataset_id)
    tmp_dir, zip_name = dataset_service.build_download_archive(dataset)

    cookie = request.cookies.get("download_cookie") or str(uuid.uuid4())
    resp = make_response(send_from_directory(tmp_dir, zip_name, as_attachment=True, mimetype="application/zip"))
    if not request.cookies.get("download_cookie"):
        # Two years, matching hubfile: a session cookie made the download
        # dedupe reset whenever the browser closed.
        resp.set_cookie("download_cookie", cookie, max_age=60 * 60 * 24 * 365 * 2)

    DSDownloadRecordService().record_download(current_user, dataset_id, cookie)
    return resp


@dataset_bp.route("/doi/<path:doi>/", methods=["GET"])
def subdomain_index(doi):

    # Check if the DOI is an old DOI
    new_doi = doi_mapping_service.get_new_doi(doi)
    if new_doi:
        # Redirect to the same path with the new DOI
        return redirect(url_for("dataset.subdomain_index", doi=new_doi), code=302)

    # Try to search the dataset by the provided DOI (which should already be the new one)
    ds_meta_data = dsmetadata_service.filter_by_doi(doi)

    if not ds_meta_data:
        abort(404)

    # Get dataset
    dataset = ds_meta_data.data_set

    # Save the cookie to the user's browser
    user_cookie = ds_view_record_service.create_cookie(dataset=dataset)
    resp = make_response(render_template("dataset/view_dataset.html", dataset=dataset))
    resp.set_cookie("view_cookie", user_cookie, max_age=60 * 60 * 24 * 365 * 2)

    return resp


@dataset_bp.route("/dataset/unsynchronized/<int:dataset_id>/", methods=["GET"])
@login_required
def get_unsynchronized_dataset(dataset_id):

    # Get dataset
    dataset = dataset_service.get_unsynchronized_dataset(current_user.id, dataset_id)

    if not dataset:
        abort(404)

    return render_template("dataset/view_dataset.html", dataset=dataset)

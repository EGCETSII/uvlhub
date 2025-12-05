from flask import Flask, request, jsonify
import uuid
import copy

app = Flask(__name__)

DATASETS = {}
VERSIONS = {}

def generate_doi():
    return f"10.1234/fakezenodo.{uuid.uuid4().hex[:8]}"

@app.route("/deposit/depositions", methods=["POST"])
def create_deposition():
    data = request.get_json()
    record_id = str(uuid.uuid4())
    DATASETS[record_id] = {
        "id": record_id,
        "metadata": data.get("metadata", {}),
        "files": [],
        "doi": None,
        "published_versions": []
    }
    return jsonify(DATASETS[record_id]), 201

@app.route("/deposit/depositions/<record_id>", methods=["PUT"])
def edit_metadata(record_id):
    if record_id not in DATASETS:
        return jsonify({"error": "Deposition not found"}), 404
    data = request.get_json()
    DATASETS[record_id]["metadata"].update(data.get("metadata", {}))
    return jsonify(DATASETS[record_id]), 200

@app.route("/deposit/depositions/<record_id>/files", methods=["POST"])
def upload_file(record_id):
    if record_id not in DATASETS:
        return jsonify({"error": "Deposition not found"}), 404
    file_info = request.form.to_dict()
    DATASETS[record_id]["files"].append(file_info.get("name", "unnamed_file"))
    return jsonify({"message": "File added", "files": DATASETS[record_id]["files"]}), 201

@app.route("/deposit/depositions/<record_id>/actions/publish", methods=["POST"])
def publish_deposition(record_id):
    if record_id not in DATASETS:
        return jsonify({"error": "Deposition not found"}), 404
    version_id = str(uuid.uuid4())
    new_doi = generate_doi()
    version_data = copy.deepcopy(DATASETS[record_id])
    version_data["doi"] = new_doi
    VERSIONS[version_id] = version_data
    DATASETS[record_id]["published_versions"].append(version_data)
    return jsonify(version_data), 202

@app.route("/deposit/depositions/<record_id>/versions", methods=["GET"])
def list_versions(record_id):
    if record_id not in DATASETS:
        return jsonify({"error": "Deposition not found"}), 404
    return jsonify(DATASETS[record_id]["published_versions"]), 200

@app.route("/deposit/depositions/<record_id>", methods=["GET"])
def get_deposition(record_id):
    if record_id not in DATASETS:
        return jsonify({"error": "Deposition not found"}), 404
    return jsonify(DATASETS[record_id]), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)

from flask import jsonify, render_template, request

from app.features.explore import explore_bp
from app.features.explore.forms import ExploreForm
from app.features.explore.services import ExploreService

explore_service = ExploreService()


@explore_bp.route("/explore", methods=["GET"])
def index():
    return render_template(
        "explore/index.html",
        form=ExploreForm(),
        query=request.args.get("query", ""),
    )


@explore_bp.route("/explore", methods=["POST"])
def search():
    datasets = explore_service.filter(**(request.get_json(silent=True) or {}))
    return jsonify([dataset.to_dict() for dataset in datasets])

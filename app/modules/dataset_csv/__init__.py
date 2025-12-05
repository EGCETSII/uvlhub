from flask_restful import Api

from app.modules.dataset_csv.api import init_blueprint_api
from core.blueprints.base_blueprint import BaseBlueprint


dataset_csv_bp = BaseBlueprint("dataset_csv", __name__, template_folder="templates")


api = Api(dataset_csv_bp)
init_blueprint_api(api)

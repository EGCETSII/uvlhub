import logging
import os

import requests
from dotenv import load_dotenv
from flask import Response, jsonify
from flask_login import current_user
from splent_framework.configuration.configuration import uploads_folder_name
from splent_framework.services.BaseService import BaseService

from app.features.dataset.models import DataSet
from app.features.featuremodel.models import FeatureModel
from app.features.zenodo.repositories import ZenodoRepository

logger = logging.getLogger(__name__)

load_dotenv()


class ZenodoService(BaseService):

    def get_zenodo_url(self):

        FLASK_ENV = os.getenv("FLASK_ENV", "development")

        if FLASK_ENV == "production":
            default_url = "https://zenodo.org/api/deposit/depositions"
        else:
            default_url = "https://sandbox.zenodo.org/api/deposit/depositions"

        return os.getenv("ZENODO_API_URL", default_url)

    def get_zenodo_access_token(self):
        return os.getenv("ZENODO_ACCESS_TOKEN")

    def __init__(self):
        super().__init__(ZenodoRepository())
        self.ZENODO_ACCESS_TOKEN = self.get_zenodo_access_token()
        self.ZENODO_API_URL = self.get_zenodo_url()
        self.headers = {"Content-Type": "application/json"}
        self.params = {"access_token": self.ZENODO_ACCESS_TOKEN}

    def test_connection(self) -> bool:
        """
        Test the connection with Zenodo.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """
        response = requests.get(self.ZENODO_API_URL, params=self.params, headers=self.headers)
        return response.status_code == 200

    def test_full_connection(self) -> Response:
        """
        Test the connection with Zenodo by creating a deposition, uploading an empty test file, and deleting the
        deposition.

        Returns:
            bool: True if the connection, upload, and deletion are successful, False otherwise.
        """

        success = True
        messages = []  # List to store messages

        # Create a test file
        working_dir = os.getenv("WORKING_DIR", "")
        file_path = os.path.join(working_dir, "test_file.txt")
        with open(file_path, "w") as f:
            f.write("This is a test file with some content.")

        try:
            # Step 1: Create a deposition on Zenodo
            data = {
                "metadata": {
                    "title": "Test Deposition",
                    "upload_type": "dataset",
                    "description": "This is a test deposition created via Zenodo API",
                    "creators": [{"name": "John Doe"}],
                }
            }

            response = requests.post(self.ZENODO_API_URL, json=data, params=self.params, headers=self.headers)

            if response.status_code != 201:
                return jsonify(
                    {
                        "success": False,
                        "messages": [
                            f"Failed to create test deposition on Zenodo. Response code: {response.status_code}"
                        ],
                    }
                )

            deposition_id = response.json()["id"]

            # Step 2: Upload a test file to the deposition
            data = {"name": "test_file.txt"}
            publish_url = f"{self.ZENODO_API_URL}/{deposition_id}/files"
            with open(file_path, "rb") as file:
                response = requests.post(publish_url, params=self.params, data=data, files={"file": file})

            logger.info(f"Publish URL: {publish_url}")
            logger.info(f"Response Status Code: {response.status_code}")
            logger.info(f"Response Content: {response.content}")

            if response.status_code != 201:
                messages.append(f"Failed to upload test file to Zenodo. Response code: {response.status_code}")
                success = False

            # Step 3: Delete the deposition
            response = requests.delete(f"{self.ZENODO_API_URL}/{deposition_id}", params=self.params)

            if response.status_code != 204:
                messages.append(f"Failed to delete test deposition on Zenodo. Response code: {response.status_code}")
                success = False
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

        return jsonify({"success": success, "messages": messages})

    def get_all_depositions(self) -> dict:
        """
        Get all depositions from Zenodo.

        Returns:
            dict: The response in JSON format with the depositions.
        """
        response = requests.get(self.ZENODO_API_URL, params=self.params, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to get depositions")
        return response.json()

    def create_new_deposition(self, dataset: DataSet) -> dict:
        """
        Create a new deposition in Zenodo.

        Args:
            dataset (DataSet): The DataSet object containing the metadata of the deposition.

        Returns:
            dict: The response in JSON format with the details of the created deposition.
        """

        logger.info("Dataset sending to Zenodo...")
        logger.info(f"Publication type...{dataset.ds_meta_data.publication_type.value}")

        publication_type = dataset.ds_meta_data.publication_type.value
        metadata = {
            "title": dataset.ds_meta_data.title,
            "upload_type": "dataset" if publication_type == "none" else "publication",
            **({"publication_type": publication_type} if publication_type != "none" else {}),
            "description": dataset.ds_meta_data.description,
            "creators": [
                {
                    "name": author.name,
                    **({"affiliation": author.affiliation} if author.affiliation else {}),
                    **({"orcid": author.orcid} if author.orcid else {}),
                }
                for author in dataset.ds_meta_data.authors
            ],
            "keywords": (
                ["uvlhub"] if not dataset.ds_meta_data.tags else dataset.ds_meta_data.tags.split(", ") + ["uvlhub"]
            ),
            "access_right": "open",
            "license": "CC-BY-4.0",
        }

        data = {"metadata": metadata}

        response = requests.post(self.ZENODO_API_URL, params=self.params, json=data, headers=self.headers)
        if response.status_code != 201:
            error_message = f"Failed to create deposition. Error details: {response.json()}"
            raise Exception(error_message)
        return response.json()

    def upload_file(self, dataset: DataSet, deposition_id: int, feature_model: FeatureModel, user=None) -> dict:
        """
        Upload a file to a deposition in Zenodo.

        Args:
            deposition_id (int): The ID of the deposition in Zenodo.
            feature_model (FeatureModel): The FeatureModel object representing the feature model.
            user (FeatureModel): The User object representing the file owner.

        Returns:
            dict: The response in JSON format with the details of the uploaded file.
        """
        uvl_filename = feature_model.fm_meta_data.uvl_filename
        data = {"name": uvl_filename}
        user_id = current_user.id if user is None else user.id
        file_path = os.path.join(uploads_folder_name(), f"user_{str(user_id)}", f"dataset_{dataset.id}/", uvl_filename)

        publish_url = f"{self.ZENODO_API_URL}/{deposition_id}/files"
        with open(file_path, "rb") as file:
            response = requests.post(publish_url, params=self.params, data=data, files={"file": file})
        if response.status_code != 201:
            error_message = f"Failed to upload files. Error details: {response.json()}"
            raise Exception(error_message)
        return response.json()

    def publish_deposition(self, deposition_id: int) -> dict:
        """
        Publish a deposition in Zenodo.

        Args:
            deposition_id (int): The ID of the deposition in Zenodo.

        Returns:
            dict: The response in JSON format with the details of the published deposition.
        """
        publish_url = f"{self.ZENODO_API_URL}/{deposition_id}/actions/publish"
        response = requests.post(publish_url, params=self.params, headers=self.headers)
        if response.status_code != 202:
            raise Exception("Failed to publish deposition")
        return response.json()

    def get_deposition(self, deposition_id: int) -> dict:
        """
        Get a deposition from Zenodo.

        Args:
            deposition_id (int): The ID of the deposition in Zenodo.

        Returns:
            dict: The response in JSON format with the details of the deposition.
        """
        deposition_url = f"{self.ZENODO_API_URL}/{deposition_id}"
        response = requests.get(deposition_url, params=self.params, headers=self.headers)
        if response.status_code != 200:
            raise Exception("Failed to get deposition")
        return response.json()

    def get_doi(self, deposition_id: int) -> str:
        """
        Get the DOI of a deposition from Zenodo.

        Args:
            deposition_id (int): The ID of the deposition in Zenodo.

        Returns:
            str: The DOI of the deposition.
        """
        return self.get_deposition(deposition_id).get("doi")

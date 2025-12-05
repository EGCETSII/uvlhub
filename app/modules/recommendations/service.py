from sqlalchemy import func, desc
from app import db
from app.modules.dataset.models import DataSet, DSDownloadRecord, Author, DSMetaData

def get_recommended_datasets(dataset):
    """
    Devuelve hasta 5 datasets del mismo autor(es), ordenados por número de descargas (MySQL-compatible).
    """
    if not dataset or not dataset.ds_meta_data or not dataset.ds_meta_data.authors:
        return []

    author_names = [author.name for author in dataset.ds_meta_data.authors if author.name]

    if not author_names:
        return []

    # Subconsulta: cuenta descargas por dataset
    downloads_subquery = (
        db.session.query(
            DSDownloadRecord.dataset_id,
            func.count(DSDownloadRecord.id).label("download_count")
        )
        .group_by(DSDownloadRecord.dataset_id)
        .subquery()
    )

    # Consulta principal (compatible con MySQL/MariaDB)
    recommended = (
        db.session.query(DataSet)
        .join(DSMetaData, DataSet.ds_meta_data_id == DSMetaData.id)
        .join(Author, Author.ds_meta_data_id == DSMetaData.id)
        .outerjoin(downloads_subquery, DataSet.id == downloads_subquery.c.dataset_id)
        .filter(Author.name.in_(author_names))
        .filter(DataSet.id != dataset.id)
        # Reemplazo de NULLS LAST → usar COALESCE o IFNULL para tratar NULL como 0
        .order_by(desc(func.coalesce(downloads_subquery.c.download_count, 0)))
        .limit(5)
        .all()
    )

    return recommended

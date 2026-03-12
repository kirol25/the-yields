from app.api.finance.repository import YieldRepository
from app.api.finance.s3_repository import S3YieldRepository

YieldRepositoryType = YieldRepository | S3YieldRepository

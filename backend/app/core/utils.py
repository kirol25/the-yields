from app.api.finance.db_repository import DBYieldRepository
from app.api.finance.repository import YieldRepository

YieldRepositoryType = YieldRepository | DBYieldRepository

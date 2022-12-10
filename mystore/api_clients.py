import logging
from requests import request, exceptions

logger = logging.getLogger(__name__)


class BaseClient:
    base_url = None

    def get_request(self,
                    method: str,
                    params: dict = None,
                    headers: dict = None,
                    data: dict = None,
                    url: str = None) -> dict or bytes:
        try:
            response = request(
                url=url or self.base_url,
                method=method,
                params=params or {},
                headers=headers or {},
                data=data or {}
            )
            json_response = response.json()
        except exceptions.JSONDecodeError:
            return response.content
        except (exceptions.ConnectionError, exceptions.Timeout) as err:
            logger.error(err)
        else:
            return json_response

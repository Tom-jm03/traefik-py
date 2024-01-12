from __future__ import annotations

import queue
import ssl
import asyncio
from types import TracebackType
import aiohttp
from typing import (
    Any,
    AsyncContextManager,
    Callable,
    Dict,
    Generator,
    Generic,
    Iterable,
    List,
    Literal,
    Optional,
    Type,
    TypeVar,
    Union,
    overload,
)


class ResponseObject:
    def __init__(self, dictionary):
        """
        Initializes a ResponseObject.

        Args:
            dictionary (dict): The dictionary to initialize the ResponseObject with.
        """
        for key, value in dictionary.items():
            setattr(self, key, value)

    def __str__(self):
        """
        Returns a string representation of the ResponseObject.

        Returns:
            str: String representation of the ResponseObject.
        """
        return str(self.__dict__)

class TraefikClient(aiohttp.ClientSession):
    """
    A client for the Traefik API.

    This class inherits from aiohttp.ClientSession and adds some methods specific to the Traefik API.
    """

    def __init__(self, traefik_url: str, port: int, scheme: str = "http", verify_ssl: bool = False, timeout: int = 10, password: str = None, username: str = None):
        """
        Initializes the TraefikClient with the given parameters.

        Args:
            traefik_url (str): The URL of the Traefik instance.
            port (int): The port on which the Traefik instance is running.
            scheme (str, optional): The scheme to use for the requests. Defaults to "http".
            verify_ssl (bool, optional): Whether to verify SSL certificates. Defaults to False.
            timeout (int, optional): The timeout for the requests in seconds. Defaults to 10.
            password (str, optional): The password for Basic Authentication. Defaults to None.
            username (str, optional): The username for Basic Authentication. Defaults to None.
        """
        ssl_context = ssl.create_default_context()
        if not verify_ssl:
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
        super().__init__(timeout=aiohttp.ClientTimeout(total=timeout), connector=aiohttp.TCPConnector(ssl=ssl_context), auth=aiohttp.BasicAuth(username, password))
        self.traefik_url = traefik_url
        self.port = port
        self.password = password
        self.username = username
        self.scheme = scheme

    @property
    async def base_url(self) -> str:
        """
        Gets the base URL for the requests.

        Returns:
            str: The base URL for the requests.
        """
        return f'{self.scheme}://{self.traefik_url}:{self.port}'

    @property
    async def auth(self) -> Optional[aiohttp.BasicAuth]:
        """
        Gets the Basic Authentication for the requests.

        Returns:
            aiohttp.BasicAuth, optional: The Basic Authentication for the requests, or None if username or password are not set.
        """
        if self.username and self.password:
            return aiohttp.BasicAuth(self.username, self.password)
        return None

    @property
    async def version(self) -> ResponseObject:
        """
        Gets the version information from the Traefik API.

        Returns:
            ResponseObject: The version information as a ResponseObject.
        
        Raises:
            ValueError: If the response is not in JSON format.
        """
        async with self.get(f'{await self.base_url}/api/version', auth=await self.auth) as resp:
            if resp.headers['Content-Type'] == 'application/json; charset=UTF-8':
                return ResponseObject(await resp.json())
            else:
                raise ValueError('Response is not in JSON format')

    async def close(self) -> None:
        """
        Closes the client.

        Returns:
            None
        """
        await super().close()

    
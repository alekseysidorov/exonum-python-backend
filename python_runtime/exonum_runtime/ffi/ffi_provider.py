"""TODO"""
from typing import Any
import ctypes as c
from threading import Thread

from exonum_runtime.runtime.types import DeploymentResult
from exonum_runtime.runtime.runtime_interface import RuntimeInterface
from .raw_types import RawPythonMethods, RawArtifactId, RawIndexAccess


class RustFFIProvider:
    """TODO"""

    _FFI_ENTITY = None

    # FFI is a singleton entity.
    def __new__(cls, *_args: Any) -> "RustFFIProvider":
        if cls._FFI_ENTITY is None:
            cls._FFI_ENTITY = super().__new__(cls)

        return cls._FFI_ENTITY

    @classmethod
    def instance(cls) -> "RustFFIProvider":
        """Gets an initialized instance of FFI provider."""
        if cls._FFI_ENTITY is None:
            raise RuntimeError("FFI is not initialized")
        return cls._FFI_ENTITY

    def __init__(self, rust_library_path: str, runtime: RuntimeInterface, ffi_callbacks: RawPythonMethods) -> None:
        self._rust_library_path = rust_library_path
        self._runtime = runtime
        self._ffi_callbacks = ffi_callbacks

        c.cdll.LoadLibrary(self._rust_library_path)
        self._rust_interface = c.CDLL(self._rust_library_path)

        # Init python-side signatures.
        self._rust_interface.init_python_side.argtypes = [c.POINTER(RawPythonMethods)]
        self._rust_interface.deployment_completed.argtypes = [RawArtifactId, c.c_uint8]

        self._rust_interface.get_snapshot_token.argtypes = []
        self._rust_interface.get_snapshot_token.restype = c.c_void_p

        self._rust_interface.main.argtypes = []

        self._rust_thread = Thread(target=self._rust_interface.main)
        self._rust_thread.setDaemon(True)
        self._rust_thread.start()

    def init_rust(self) -> None:
        """Initializes Python interfaces in the Rust side."""
        self._rust_interface.init_python_side(c.byref(self._ffi_callbacks))

    def rust_interface(self) -> c.CDLL:
        """Gets the rust FFI interface."""
        return self._rust_interface

    def deploy_completed(self, result: DeploymentResult) -> None:
        """Method to be called when deployment is completed."""
        raw_artifact = RawArtifactId.from_artifact_id(result.artifact_id)

        self._rust_interface.deployment_completed(raw_artifact, result.result.value)

    def runtime(self) -> RuntimeInterface:
        """Returns runtime."""
        return self._runtime

    def snapshot_token(self) -> RawIndexAccess:
        """Retrieves an Snapshot token for API interaction."""
        return self._rust_interface.get_snapshot_token()

from fhirdrill.auth import AUTH_PARAMS_PRESETS
from fhirdrill.auth import Auth
from pandas import DataFrame
from fhirpy import SyncFHIRClient
import warnings

import fhirdrill.base
import fhirdrill.extraction
import fhirdrill.transformation
import fhirdrill.load
import fhirdrill.custom
import fhirdrill.utils
from fhirdrill.constants import CONFIG

LOGGER = CONFIG.getLogger(__name__)


class Drill(
    fhirdrill.base.BaseMixin,
    fhirdrill.extraction.ExtractorMixin,
    fhirdrill.transformation.TransformerMixin,
    fhirdrill.load.LoaderMixin,
    fhirdrill.custom.PluginMixin,
):
    def __init__(
        self,
        client=None,
        envFile=None,
        unconnected=False,
        authMethod=None,
        authParams=None,
    ):

        self.logger = CONFIG.getLogger(__name__)
        self.logger.info("Drill initialization started.")

        if envFile:
            CONFIG.loadConfig(envFile)
        else:
            CONFIG.loadConfig()

        if client:
            self.client = client
        elif unconnected:
            self.client = None
        else:
            self.__setupClient(authMethod=authMethod, authParams=authParams)
        try:
            self.client._do_request("get", self.client.url + "/Patient")
        except:
            warnings.warn("Drill is not connected to server.")
            self.logger.info("Drill is not connected to server.")
            self.client = SyncFHIRClient("")

        self.logger.info("drill initialization finished")

    def __setupClient(self, authMethod=None, authParams=None):

        if authMethod:
            CONFIG.set("AUTH_METHOD", authMethod)

        if isinstance(authParams, dict) and authParams:
            pass
        elif isinstance(authParams, str) and authParams:
            authParams = AUTH_PARAMS_PRESETS[authParams]
        elif CONFIG.get("AUTH_PARAMS_PRESET"):
            authParams = AUTH_PARAMS_PRESETS[CONFIG.get("AUTH_PARAMS_PRESET")]

        authorization = None

        if CONFIG.get("AUTH_METHOD") == "oauth_password":
            token = Auth.getToken("password", authParams)
            CONFIG.set("OAUTH_TOKEN", token["access_token"]),
            authorization = f"Bearer {token['access_token']}"
        elif CONFIG.get("AUTH_METHOD") == "oauth_token":
            token = CONFIG.get("OAUTH_TOKEN")
            authorization = f"Bearer {token}"
        elif authMethod is None:
            authorization = None
        else:
            raise NotImplementedError

        self.client = SyncFHIRClient(CONFIG.get("APIBASE"), authorization=authorization)

    def countServerResources(self):

        results = []
        # TODO write function in utils to retrieve current installation path
        # TODO move path with others to common location, CONFIG?
        with open(
            f"{fhirdrill.utils.getInstallationPath()}/../../assets/supported.list"
        ) as f:
            while resource := f.readline().strip():
                count = self.client.execute(
                    # TODO handle and test when slash at the end of APIBASE in .env and without
                    # WARNING path must either:
                    # 1. be relative and allow FHIRPy to parametrize the URL
                    # 2. be absolute and contain the params already as they will otherwise be ignored
                    resource,
                    method="get",
                    # if _count has the value 0, this shall be treated the same as _summary=count
                    # https://www.hl7.org/fhir/search.html#count
                    params={"_count": 0},
                ).total
                results.append((resource, count))
        results = DataFrame(results, columns=["resourceType", "count"])
        return results

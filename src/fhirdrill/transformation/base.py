import json
import importlib
from typing import Union

import pandas as pd

from fhirpy.lib import SyncFHIRResource
from fhirpy.lib import SyncFHIRReference
import numpy as np
import fhirdrill.utils as utils
import fhirdrill.base

# LOGGER = CONFIG.getLogger(__name__)


class BaseTransformerMixin:
    def validate(
        self,
        references: Union[
            list[str],
            list[SyncFHIRReference],
            list[SyncFHIRResource],
        ] = None,
    ):

        if references:
            references = self.prepareReferences(references)

        result = []
        if not references and self.isFrame:
            references = [e.to_reference() for e in self.data]
        elif references and not self.isFrame:
            pass
        elif references and self.isFrame:
            # TODO raise error references and isFrame not allowed
            # TODO raise in other similar methods
            pass

        references = self.referencesToResources(references)
        for ref in references:
            try:
                rtype = ref["resourceType"]
                res = getattr(
                    importlib.import_module(f"fhir.resources.{rtype.lower()}"), rtype
                )

                obj = res.parse_obj(ref)
            except Exception as e:
                # TODO raise or log?
                return False
                pass

        # TODO what makes more sense, false or self?
        # TODO add guessResource type to prepareOutput when no resourceType given
        return self.prepareOutput(references)

    def gatherSimplePaths(
        self,
        paths: list[str],
        input: Union[
            list[str],
            list[SyncFHIRReference],
            list[SyncFHIRResource],
        ] = None,
        params: dict = {},
    ):
        if not params:
            params = {}

        if not input and self.isFrame:
            input = self.data.values
        elif input and not self.isFrame:
            input = self.prepareOperationInput(input, SyncFHIRResource)
        elif input and self.isFrame:
            # TODO your code for data coming in as arguments and frame
            raise NotImplementedError

        result = {k: [] for k in paths}
        for path in paths:
            # print(results)
            for element in input:
                if isinstance(element, SyncFHIRReference) or isinstance(
                    element, SyncFHIRResource
                ):
                    element = element.to_resource()
                elementResult = self.__gatherSimplePath(element, path)

                if elementResult.get(path, None):
                    result[path].append(elementResult[path])
                else:
                    result[path].append(None)
                # print(f"\n\n\n\n\n\n\n\n ..........result ...........")
                # print(json.dumps(results,indent=4,sort_keys=True))
        # return results
        # return pd.DataFrame(results)

        return self.prepareOutput(
            result, resourceType=self.resourceType, columns=paths, wrap=False
        )

    # TODO test path one level (no dot)
    # TODO test path two levels
    # TODO test path three levels

    # TODO test leaf is a list
    # drill.validate(
    # ['Patient/4137ebc9d2d745fbcf7ab6ea86d626a6d97096a3384dc53d666c3611c16b8136']
    # ).filterPaths(['name.given'])

    def __gatherSimplePath(self, data: dict, path: Union[str, list[str]]):

        if isinstance(path, str):
            frags = path.split(".")
        else:
            frags = path

        firstFrag = frags[0]
        # print(f"\n\n\n\n\n\n\n\n ..........entering {firstFrag}.....{len(frags)}")
        # print(json.dumps(data,indent=4,sort_keys=True))

        if isinstance(data, dict) and data.get(firstFrag):
            # print(f"dict........{frags}...{len(frags)}")
            if len(frags) == 1:
                # print(f"dict leaf ..... .....{frags}.....{len(frags)}")
                return {firstFrag: data[firstFrag]}
            else:
                # print(f"dict nonleaf ..... .....{frags}.....{len(frags)}")
                partialResults = self.__gatherSimplePath(data[firstFrag], frags[1:])
                # print(f"dict partial results ..........{frags}.....{len(frags)}")
                # print(json.dumps(partialResults,indent=4,sort_keys=True))
                results = {firstFrag + "." + k: v for k, v in partialResults.items()}
                # print(f"dict partial  ..........{frags}.....{len(frags)}")
                # print(json.dumps(results,indent=4,sort_keys=True))
                return results
        elif isinstance(data, list):
            results = {}
            for e in data:
                # print(f"list iter {e}........{frags}.......{len(frags)}")
                partialResults = self.__gatherSimplePath(e, frags)
                # print(f"list partial results ..........{frags}.....{len(frags)}")
                # print(json.dumps(partialResults,indent=4,sort_keys=True),'\n\n\n')
                # print(json.dumps(partialResults,indent=4,sort_keys=True),'\n\n\n')
                for k, v in partialResults.items():
                    # print('.............', k, v)
                    if results.get(k, None):
                        results[k].append(v)
                    else:
                        results[k] = [v]
                # print(f"list final results ..........{frags}.....{len(frags)}")
                # print(json.dumps(results,indent=4,sort_keys=True),'\n\n\n')
            return results
        # print(f"neither.........{frags}.......{len(frags)}")
        return {}

    # TODO test
    # drill.getPatients(
    # 	['Patient/4137ebc9d2d745fbcf7ab6ea86d626a6d97096a3384dc53d666c3611c16b8136'],
    #   includeLinkedPatients=True
    # ).gatherReferences(recursive=True)

    def gatherReferences(
        self,
        references: Union[
            list[str],
            list[SyncFHIRReference],
            list[SyncFHIRResource],
        ] = None,
        recursive: bool = False,
    ):

        if references:
            references = self.prepareReferences(references)

        result = []
        if not references and self.isFrame:
            references = [e.to_reference() for e in self.data]
        elif references and not self.isFrame:
            pass
        elif references and self.isFrame:
            # TODO raise error references and isFrame not allowed
            # TODO raise in other similar methods
            raise NotImplementedError

        pending = references
        visited = []
        ret = []
        level = 0
        while len(pending) > 0:
            ref = pending.pop(0)
            if ref in visited:
                continue
            visited.append(ref)
            nrefs = []
            try:
                if not isinstance(ref, SyncFHIRReference):
                    ref = self.prepareReferences([ref])[0]
                nrefs = utils.valuesForKeys(ref.to_resource(), ["reference"])
            except Exception as e:
                print("Fatal error", e, "for ", ref, " referenced by ", visited[:-1])
            nrefs = list(nrefs)
            ret.append([ref, nrefs])
            level += 1
            if recursive:
                pending.extend(nrefs)
        return pd.DataFrame(ret, columns=["referencer", "referencee"])

    def gatherText(
        self,
        recursive: bool = False,
        references: Union[
            list[str],
            list[SyncFHIRReference],
            list[SyncFHIRResource],
        ] = None,
    ):

        if references:
            references = self.prepareReferences(references)

        if not references and self.isFrame:
            references = [e.to_reference() for e in self.data]
        elif references and not self.isFrame:
            pass
        elif references and self.isFrame:
            # TODO raise error references and isFrame not allowed
            # TODO raise in other similar methods
            raise NotImplementedError

        result = []
        for ref in references:

            resource = ref.to_resource()
            resource.pop("meta")

            # TODO text representation is dependent of resource type, handle others and move to constants.py
            result.append(
                list(
                    utils.valuesForKeys(
                        resource,
                        [
                            "display",
                            "summary",
                            "description",
                            "title",
                            "conclusion",
                            "note",
                            "text",
                            "answer",
                            "valueString",
                        ],
                    )
                )
            )

        return pd.DataFrame(pd.Series(result, dtype="object"), columns=["text"])

    def gatherKeys(
        self,
        params: dict = None,
        input: Union[
            list[str],
            list[SyncFHIRReference],
            list[SyncFHIRResource],
        ] = None,
    ):

        params = {} if params is None else params

        # TODO avoid converting provided resources into references and back
        # if references:
        # references = self.prepareReferences(references)

        if not input and self.isFrame:
            input = self.data
            pass
        elif input and not self.isFrame:
            input = self.prepareOperationInput(input, SyncFHIRResource)
            pass
        elif input and self.isFrame:
            # TODO raise error references and isFrame not allowed
            # TODO raise in other similar methods
            raise NotImplementedError

        result = []

        for i, e in input.items():
            e = e.serialize()
            result.append(list(utils.keys(e)))

        return pd.DataFrame(pd.Series(result, dtype="object"), columns=["data"])

    def gatherValuesForKeys(
        self,
        keys: list[str],
        params: dict = None,
        input: Union[
            list[str],
            list[SyncFHIRReference],
            list[SyncFHIRResource],
        ] = None,
    ):

        params = {} if params is None else params

        # TODO avoid converting provided resources into references and back
        # if references:
        # references = self.prepareReferences(references)

        if not input and self.isFrame:
            input = self.data
            pass
        elif input and not self.isFrame:
            input = self.prepareOperationInput(input, SyncFHIRResource)
            pass
        elif input and self.isFrame:
            # TODO raise error references and isFrame not allowed
            # TODO raise in other similar methods
            raise NotImplementedError

        result = []

        for i, e in input.items():
            e = e.serialize()
            result.append(list(utils.valuesForKeys(e, keys)))

        return pd.DataFrame(pd.Series(result, dtype="object"), columns=["values"])

    def gatherDates(
        self,
        recursive: bool = False,
        input: Union[
            list[str],
            list[SyncFHIRReference],
            list[SyncFHIRResource],
        ] = None,
        params: dict = None,
    ):

        params = {} if params is None else params

        # TODO avoid converting provided resources into references and back
        # if references:
        # references = self.prepareReferences(references)

        if not input and self.isFrame:
            input = self.data
            pass
        elif input and not self.isFrame:
            input = self.prepareOperationInput(input, SyncFHIRResource)
            pass
        elif input and self.isFrame:
            # TODO raise error references and isFrame not allowed
            # TODO raise in other similar methods
            raise NotImplementedError

        result = []

        for i, e in input.items():
            e = e.serialize()
            dates = list(
                # TODO move list of date-like elements to constants.py or infer them
                utils.valuesForKeys(
                    e,
                    [
                        "recordedDate",
                        "effectiveDate",
                        "issued",
                        "effectiveDateTime",
                    ],
                )
            )
            result.append(dates)
            # result.append([datetime.datetime.fromisoformat(d) for d in dates])

        result = pd.DataFrame(pd.Series(result), columns=["dates"])
        return result

        # TODO improve date parsing
        return pd.to_datetime(result.timestamp)
        (pd.Series(result, columns=["timestamp"]).to_datetime)
        # return pd.DataFrame(pd.Series(result,dtype="datetime64[ns]"),columns=["timestamp"])
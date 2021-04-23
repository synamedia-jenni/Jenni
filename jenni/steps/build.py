from abc import ABC
from typing import Union, List

from jenni.stepbase import StepBase
from jenni.utils import quote1or3xs, quote3xs, bool2groovy


class Step(StepBase, ABC):
    CLASS_MAP = {
        "string": "StringParameterValue",
        "text": "TextParameterValue",
        "bool": "BooleanParameterValue",
    }

    # https://www.jenkins.io/doc/pipeline/steps/pipeline-build-step/#build-build-a-job
    def build(
        self,
        job: str,
        parameters: List = None,
        propagate: bool = True,
        wait: bool = True,
    ) -> Union[None, dict]:  # TODO not sure if the return types are ok
        """
        :param job:
            Name of a downstream job to build. May be another Pipeline job,
            but more commonly a freestyle or other project. Use a simple name if the job is in
            the same folder as this upstream Pipeline job; otherwise can use relative paths like
            ``../sister-folder/downstream`` or absolute paths like ``/top-level-folder/nested-folder/downstream``

        :param parameters: list of [type, name, value].

            Name and value are obvious;
            type is one of the types listed in https://www.jenkins.io/doc/pipeline/steps/pipeline-build-step/#build-build-a-job
            EG:

            * "booleanParam"
            * "string"
            * "text"

        :param propagate:
            If enabled (default state), then the result of this step is that of the downstream build
            (e.g., success, unstable, failure, not built, or aborted).
            If disabled, then this step succeeds even if the downstream build is unstable, failed, etc.;
            use the result property of the return value as needed.

        :param wait: Wait for the job to complete. Defaults to True.

        :return:
            You may ask that this Pipeline build wait for completion of the downstream build. In that case the return value of the step is an object on which you can obtain the following read-only properties: so you can inspect its .result and so on.

            getBuildCauses
                Returns a JSON array of build causes for the current build
            EXPERIMENTAL - MAY CHANGE getBuildCauses(String causeClass)
                Takes a string representing the fully qualified Cause class and returns a JSON array of build causes filtered by that type for the current build, or an empty JSON array if no causes of the specified type apply to the current build
            number
                build number (integer)
            result
                typically SUCCESS, UNSTABLE, or FAILURE (may be null for an ongoing build)
            currentResult
                typically SUCCESS, UNSTABLE, or FAILURE. Will never be null.
            resultIsBetterOrEqualTo(String)
                Compares the current build result to the provided result string (SUCCESS, UNSTABLE, or FAILURE) and returns true if the current build result is better than or equal to the provided result.
            resultIsWorseOrEqualTo(String)
                Compares the current build result to the provided result string (SUCCESS, UNSTABLE, or FAILURE) and returns true if the current build result is worse than or equal to the provided result.
            displayName
                normally #123 but sometimes set to, e.g., an SCM commit identifier.
            fullDisplayName
                normally folder1 » folder2 » foo #123.
            projectName
                Name of the project of this build, such as foo.
            fullProjectName
                Full name of the project of this build, including folders such as folder1/folder2/foo.
            description
                additional information about the build
            id
                normally number as a string
            timeInMillis
                time since the epoch when the build was scheduled
            startTimeInMillis
                time since the epoch when the build started running
            duration
                duration of the build in milliseconds
            durationString
                a human-readable representation of the build duration
            previousBuild
                another similar object, or null
            nextBuild
                similarly
            absoluteUrl
                URL of build index page
            buildVariables
                for a non-Pipeline downstream build, offers access to a map of defined build variables; for a Pipeline downstream build, any variables set globally on env at the time the build ends. Child Pipeline jobs can use this to report additional information to the parent job by setting variables in env. Note that build parameters are not shown in buildVariables.
            changeSets
                a list of changesets coming from distinct SCM checkouts; each has a kind and is a list of commits; each commit has a commitId, timestamp, msg, author, and affectedFiles each of which has an editType and path; the value will not generally be Serializable so you may only access it inside a method marked @NonCPS
            upstreamBuilds
                a list of upstream builds. These are the builds of the upstream projects whose artifacts feed into this build.
            rawBuild
                a hudson.model.Run with further APIs, only for trusted libraries or administrator-approved scripts outside the sandbox; the value will not be Serializable so you may only access it inside a method marked @NonCPS
            keepLog
                true if the log file for this build should be kept and not deleted.

            If you do not wait, this step succeeds so long as the downstream build can be added to the queue (it will not even have been started). In that case there is currently no return value.
        """
        param_code = []
        if parameters:
            for parameter in parameters:
                class_, name, value = parameter
                if class_ == "bool":
                    value = bool2groovy(value)
                else:
                    value = quote1or3xs(value)
                class_ = self.CLASS_MAP.get(class_, class_)
                param_code.append(f"[$class: '{class_}', name: '{name}', value: {value}]")
            params = ", parameters: [" + ",\n".join(param_code) + "]"
        else:
            params = ""
        code = (
            "build(job:"
            + quote1or3xs(job)
            + ", propagate:"
            + bool2groovy(propagate)
            + ", wait:"
            + bool2groovy(wait)
            + params
            + ")"
        )
        return self.execute_groovy(code)

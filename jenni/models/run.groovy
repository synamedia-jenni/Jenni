package jenni.models
/*
Instance entry point for a job, Groovy part
*/

import groovy.json.JsonOutput
this.done = false
this.debug = false
def debug_msg(def s) {
    if (debug) {
        echo(s)
    }
}

def runPython() {
    try {
        // TODO how to handle running python in docker. Needs configurability
        // TODO need to be able to pass args
        // TODO config-dir should be configurable
        sh script: '''
JENNIPATH=$WORKSPACE/pica-jenkins/config
CONFIG_DIR=$WORKSPACE/pica-jenkins/config
export PYTHONPATH=$JENNIPATH
python3 -u -m jenni --config-dir $CONFIG_DIR --log-file jenni-debug.log run
'''
    }
    finally {
        archiveArtifacts artifacts: 'jenni-debug.log'
        done = true
    }
}

def runStepServer() {
    debug_msg "runStepServer starting..."
    try {
        def pythonUrlFile = '_url.txt'
        def pythonUrl = null
        for (int i = 0; i < 50 && !pythonUrl; i++) {
            debug_msg "runStepServer i = $i"
            if (!fileExists(file: pythonUrlFile)) {
                debug_msg "$pythonUrlFile not exists, sleeping"
                sleep(time: 1000, unit: 'MILLISECONDS')
                continue
            }
            debug_msg "$pythonUrlFile exists, sleeping"
            sleep(time: 200, unit: 'MILLISECONDS')
            try {
                debug_msg "reading $pythonUrlFile"
                pythonUrl = readFile(file: pythonUrlFile)
                fileOperations([fileDeleteOperation(excludes: '', includes: pythonUrlFile)])
                continue
            }
            catch (Exception ex) {
                debug_msg "WARNING: $ex"
                sleep(time: 200, unit: 'MILLISECONDS')
            }
        }
        if (!pythonUrl) {
            error "Failed to read $pythonUrlFile"
        }

        int errors = 0
        def data = ['result': null, 'status': 'initial']
        debug_msg "runStepServer calling ${pythonUrl}"
        while (!done && errors < 10) {
            try {
                def response = httpRequest(
                        url: pythonUrl,
                        httpMode: 'POST',
                        acceptType: 'TEXT_PLAIN',
                        contentType: 'APPLICATION_JSON',
                        requestBody: JsonOutput.toJson(data), //data['status'],
                        responseHandle: 'STRING',
//                        timeout: 10,
                        quiet: true,
                )
                debug_msg "Response: $response"
                def status = response.getStatus()
                if (status == 408) { // timeout
                    debug_msg 'Request timeout'
//                    sleep(time: 1, unit: 'SECONDS')
//                    continue
                }
                if (status != 200) {
                    error("ERROR: Response: $response")
                }
                def step_request_data = response.getContent()
                debug_msg "step_request_data: ${step_request_data}"
                if (step_request_data == 'exit') {
                    done = true
                    continue
                }
                if (! (step_request_data =~ /^request-\d+\.groovy$/)) {
                    echo("ERROR: unexpected request data!!! - $step_request_data")
                    error("ERROR: unexpected request data!")
                }
                def code_text = readFile(step_request_data)
                debug_msg("code: ${code_text}")
                code = load(step_request_data)
                fileOperations([fileDeleteOperation(excludes: '', includes: step_request_data)])
                code.delegate = this
                data['result'] = code()
                data['status'] = 'ok'
            }
            catch (Exception ex) {
                echo "ERROR: $ex"
                errors += 1
                sleep(time: 1000, unit: 'MILLISECONDS')
                data['result'] = "ERROR: $ex"
                data['status'] = 'error'
            }
        }
    }
    catch (Exception ex) {
        sleep(time: 1000, unit: 'MILLISECONDS')
        debug_msg "done = $done"
        if (done) {
            debug_msg "INFO: $ex"
        } else {
            echo "ERROR: $ex"
            throw ex
        }
    }
    finally {
        sh script:"""#!/bin/sh +x
if [ $done != true ]; then
  kill \$(cat _python.pid) 2>/dev/null
fi
rm -f _python.pid _url.txt
exit 0
"""
    }
    debug_msg "runStepServer exiting."
}

def run_job(String node_label) {
    node(node_label) {
//WRAP_INSIDE_NODE
        try {
            parallel([
                "step_server": { runStepServer() },
                "python": { runPython() }
            ])
        }
        catch (Exception ex) {
            throw ex
        }
        finally {
            // In case no log files were archived
            try {
                archiveArtifacts("*.log, */*.log")
            }
            catch (Exception ex) {
                echo "$ex"
            }
        }
//WRAP_INSIDE_NODE
    }
}

// TODO make configurable
run_job("builder")

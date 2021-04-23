Security
========

The only known security concerns are as follows:

1. When Jenkins jobs are derived from
:py:class:`jenni.models.PythonPipelineJobBase`, as implemented at the time of writing
using a plain http server listener (see file ``stepserver.py``  :py:mod:`jenni.stepserver`), then
sensitive data could possibly be obtained if network traffic on the loopback network could be captured,
due to http being used.

2. The stepserver listens on localhost and an attacker could craft a malicious request
that would cause a security incident.

Thus do not use :py:class:`jenni.models.PythonPipelineJobBase` in an environment where the above issues
could arise.

Pipeline Execution Step Server
------------------------------

A POC. See above for security concerns.

.. automodule:: jenni.stepserver
   :members:
   :undoc-members:

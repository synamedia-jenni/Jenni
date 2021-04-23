Introduction
============

Summary
-------

Jenni (JENkins New Interface) provides a Python-based system for configuring and running Jenkins jobs.

Why use Jenni?
--------------

- It allows programmatic generation of Jenkins Jobs using the flexibility and familiarity of the Python language.
- Using class-based models for defining jobs allows for template-like instantiation of jobs.
- It provides a flexible framework for iterative development of Jenkins jobs.
- Jenkins `Pipeline Groovy <https://plugins.jenkins.io/workflow-cps>`_ has several (surprising) restrictions.
- Many engineers know and love Python.
- Python has excellent IDE support.

How does it work?
-----------------

- Each Jenkins job is defined by a class called ``Job`` in a Python module.
- Each Jenkins folder is defined by a class named ``Folder`` in a Python package module.
- Job parameters are defined by instances of a ``ParamBase`` sub-class.
- A ``python -m jenni seed`` generates an intermediate JobDSL file.
- In Jenkins a ``seed`` job can process this JobDSL file to create/update folders and jobs.
- As a developer in your own workspace, the JobDSL file can also be processed
  to generate a directory tree with Jenkins folder&job xml files.
- This generated directory tree can be compared with a reference directory tree,
  to check if the changes are as expected.
- One or more folder&job xml files can be uploaded to Jenkins to modify specific folders&jobs.
- A Gradle build file handles these local-workspace activities.

What will be next?
------------------

The Jenni package is far from complete. The ultimate goal is both generate
and execute jobs using Python, without using any Groovy pipeline code directly.
The beginnings of this has been implemented as a proof of concept:

- Various Python methods provide functionality equivalent to corresponding pipeline steps
  (eg sofar mostly the basic steps like stash/unstash, archiveArtifact, copyArtifact, git, unstable, stage, etc etc).
- These methods effectively perform a Remote Procedure Call to a Groovy listener, which executes
  the requested pipeline step, and returns the result.

Help for the following would be much appreciated:

- improving the Folder and Job creation api
- allow creating Views
- implementation of many more steps
- implementation of a plugin for a pipeline step RPC listener (replacing the prototype scripted approach).

Security Warning
----------------

Please see `Security <security.html>`_ for deployment on 'insecure / multi-tenant' Jenkins hosts.

Sample Directory Structure
--------------------------

.. code-block::

    jobs/                   # a directory called "jobs" is required.
        __init__.py         # defines a "Folder" class derived from RootFolderBase
        folder1/
            __init__.py
            job1.py

CLI
---

The ``python3 -m jenni`` command has this usage:

.. code-block:: shell

    jenni [-h] [-q] -c CONFIG_DIR [-l LOG_FILE] {run,seed} ...

It has two sub-commands, ``seed`` and ``run``.

Seed Command
^^^^^^^^^^^^

The ``python3 -m jenni seed`` command processes a directory containing the "jobs" directory and writes a Groovy file with JobDSL code.
See :ref:`seed-job`.

.. code-block:: shell

    jenni seed -o OUTPUT_FILE [--append]

    optional arguments:
      -h, --help            show this help message and exit
      -o OUTPUT_FILE, --output OUTPUT_FILE
                            Output jobdsl filename
      --append              Append rather than overwrite output jobdsl file

Run Command
^^^^^^^^^^^

The ``python -m jenni run`` command runs a Jenkins job. This is work in progress.

.. code-block:: shell

    jenni run [-j JOB_NAME] [param_assignment [param_assignment ...]]

    positional arguments:
      param_assignment      name=value for each job parameter

    optional arguments:
      -j JOB_NAME, --job JOB_NAME
                            Name of job to run. Default is $JOB_NAME


.. _seed-job:

Seed Job
--------

A job like this can be used to update the folders/jobs on a Jenkins server after a commit to the code using Jenni.

.. code-block:: groovy

    pipeline {
        agent { label 'master' }
        options {
            disableConcurrentBuilds()
        }
        stages {
            stage('Checkout') { checkout ... }
            stage('Generate') { sh script: 'python -m jenni seed >jobdsl.groovy' }
            stage('Execute') {
                jobDsl(
                    lookupStrategy: 'SEED_JOB',
                    removedConfigFilesAction: 'DELETE',
                    removedJobAction: 'DISABLE',
                    removedViewAction: 'IGNORE',
                    scriptText: readFile(file:'jobdsl.groovy')
                )
            }
        }
    }

Testing
-------

Run ``make test`` to run the unittests located in the ``test`` folder.

Running Bandit
--------------

`Bandit <https://pypi.org/project/bandit/>`_ is a Security oriented static analyser for python code.
Run it using ``make bandit`` (it will automatically create a local venv folder).

Implementation Details
----------------------

Jenkins folders and jobs are defined by singleton instances of classes.
Each class can define exactly one folder or job. Each class also resides in a unique module.

The root folder normally is defined in a ``jobs/__init__.py`` file
with a class named ``Folder`` derived from :py:class:`jenni.models.RootFolderBase`.

Other Jenkins folders are defined as ``Folder`` classes
derived from :py:class:`jenni.models.FolderBase`.

Jenkins jobs are defined as ``Job`` classes
derived from :py:class:`jenni.models.JobBase`; however in practice they are normally derived from
:py:class:`jenni.models.GroovyJobBase`
or
:py:class:`jenni.models.PythonPipelineJobBase`.

After this, these classes and modules can be statically defined in Python source code files,
or can be programmatically generated, or any combination of this.

A Jenkins folder normally maps to a ``__init__.py`` file in a directory that is the same as the Jenkins folder path,
except hyphens are changed to underscores.

Programmatic Job Generation
---------------------------

A folder can programmatically generate new sub-items (jobs/folders) by overriding the ``yield_items`` method,
instead of by creating a new Python file for each sub-item.
The new sub-item is created and added by calling ``yield from self.yield_sub_item(sub_item_name, sub_item_class)``.
For example:

.. code-block:: python

    # jobs/__init__.py
    from jenni.models import RootFolderBase, GroovyJobBase

    class Folder(RootFolderBase):
        def yield_items(self):
            yield from super().yield_items()
            yield from self.yield_sub_item("job1", Job)

    class Job(GroovyJobBase):
        def __init__(self):
            super().__init__()
            self.code(f"echo 'hello from {self.name}';")

There are various method names that start with ``yield``, which can all be used to create additional jobs/folder
at various points, and if overriding them they must always call
``yield from super().<method_name>(...)``, and use ``yield`` something themselves.

Please see the customisation hooks below for further information.

Customisation Hooks
-------------------

FolderBase.add_new_job
^^^^^^^^^^^^^^^^^^^^^^

The :py:func:`jenni.models.FolderBase.add_new_job` is
executed after the Python job instance has been created (``__init__`` completed).
It can be used by the parent folder to customise the newly added job.

For example, you want to repeat the description of the Jenkins folder at the end of the description of every job in it:

.. code-block:: python

    import jenni
    class Folder(jenni.models.FolderBase):
        def __init__...

        def add_new_job(self, job: "jenni.models.jobbase.JobBase"):
            super().add_new_job(job)
            job.description = f"{job.description}<br/>{self.description}"

FolderBase.add_new_folder
^^^^^^^^^^^^^^^^^^^^^^^^^

The :py:func:`jenni.models.FolderBase.add_new_folder` is
executed after the Python Folder instance has been created (``__init__`` completed).
It can be used by the parent folder to customise the newly added sub-folder.
It is similar to :py:func:`jenni.models.FolderBase.add_new_job` method.

For example, you want to add a link to a url in every sub-folder description, but the url depends on the parent folder:

.. code-block:: python

    import jenni
    class Folder(jenni.models.FolderBase):
        def __init__...

        def add_new_folder(self, sub_folder: "FolderBase"):
            super().add_new_folder(sub_folder)
            if self.should_i_add_link():
                sub_folder.description = f"{sub_folder.descripton}<br/>See also {jenni.utils.html_link(sub_folder.the_link_url)}"""

FolderBase.yield_items_pre_sub_item
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :py:func:`jenni.models.FolderBase.yield_items_pre_sub_item` is
called before :py:func:`jenni.models.itembase.ItemBase.yield_items()` is called.
It allows you to yield additional items, before the sub-item will yield any items.
EG you may want to create additional jobs/folders, such that the sub-item can find/use these.

FolderBase.yield_items_post_sub_item
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :py:func:`jenni.models.FolderBase.yield_items_post_sub_item` is
called before :py:func:`jenni.models.itembase.ItemBase.yield_items()` is called.
It allows you to yield additional items, after the sub-item has yielded any items.
EG you may want to create additional jobs/folders, that find/use the sub-item just created.

FolderBase.sub_item_completed_handler
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The :py:func:`jenni.models.FolderBase.sub_item_completed_handler` is
called after a sub-item has completed yielding any items.
The sub-item can be customised by overriding this method.

Summary
^^^^^^^

Let folder be a :py:class:`~jenni.models.FolderBase` instance, and sub_item a (new)
:py:class:`~jenni.models.FolderBase` or :py:class:`~jenni.models.JobBase` instance to be created,
then this shows the sequence of calls:

.. code-block::

    sub_item.__init__(...)
        super().__init__(...)
    if isinstance(sub_item, JobBase):
        folder.add_new_job(sub_item)
    if isinstance(sub_item, FolderBase):
        folder.add_new_folder(sub_item)
    yield from folder.yield_items_pre_sub_item(sub_item)
    yield from sub_item.yield_items()
    yield from folder.yield_items_post_sub_item(sub_item)
    folder.sub_item_completed_handler(sub_item)

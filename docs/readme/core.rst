============
Ebonite Core
============

This module is responsible for model analysis and
model persisting.
If you use vanilla ebonite, this is mainly what
you are working with.

Main model analysis API abstractions are

* :class:`~ebonite.core.analyzer.dataset.DatasetHook` - hook for dataset analysis

* :class:`~ebonite.core.objects.dataset_type.DatasetType` - dataset descriptor

* :class:`~ebonite.core.analyzer.model.ModelHook` - hook for model understanding

* :class:`~ebonite.core.objects.wrapper.ModelWrapper` - model wrapper for different ml libraries

Main model persisting abstractions are

* :class:`~ebonite.repository.MetadataRepository` - Repository to store model metadata (like sql database)

* :class:`~ebonite.repository.ArtifactRepository` - Repository to store model artifacts (like s3 or nexus)

* :class:`~ebonite.client.Ebonite` - Main user-facing ebonite client class


Also these helper functions available:

* :func:`~ebonite.create_model` - creates :class:`~ebonite.core.objects.core.Model` instance from model object and sample data
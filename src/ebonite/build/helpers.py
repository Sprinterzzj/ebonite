from typing import Union

import ebonite
from ebonite.build.provider.ml_model import MLModelProvider
from ebonite.build.runner.base import LocalTargetHost
from ebonite.build.runner.docker import DockerImage, DockerRunner, DockerServiceInstance
from ebonite.core.objects import core
from ebonite.runtime.server import Server
from ebonite.utils.importing import module_importable


def build_model_docker(image_params: Union[str, DockerImage], model: 'core.Model', server: Server = None,
                       force_overwrite=False, debug=False, **kwargs) -> 'core.Image':
    """
    Builds docker image from Model instance

    :param image_params: params (or simply name) for docker image to be built
    :param model: model to create image
    :param server: server instance to wrap model
    :param force_overwrite: force overwrite image if it exists
    :param debug: run server in debug mode
    :param kwargs: same as in :meth:`~ebonite.build.builder.docker_builder.DockerBuilder.__init__`
    :return built image
    """
    if isinstance(image_params, str):
        image_params = DockerImage(image_params)

    if server is None:
        from ebonite.ext.flask import FlaskServer
        server = FlaskServer()

    if not module_importable('docker'):
        raise RuntimeError("Can't build docker container: docker module is not installed. Install it "
                           "with 'pip install docker'")

    from ebonite.build.builder.docker_builder import DockerBuilder, is_docker_running

    if not is_docker_running():
        raise RuntimeError("Docker is unavailable")

    provider = MLModelProvider(model, server, debug)
    builder = DockerBuilder(provider, image_params, force_overwrite, **kwargs)
    image = builder.build()
    image.model = model
    return image


def run_docker_img(container_name: str, image_name: str, port_mapping=None, detach=False):
    if port_mapping is None:
        port_mapping = {9000: 9000}
    runner = DockerRunner()
    service = DockerServiceInstance(container_name, DockerImage(image_name), LocalTargetHost(), port_mapping)
    runner.run(service, detach=detach)


def create_service_from_model(model_name: str, model_object, model_input, *,
                              project_name: str = 'default_project', task_name: str = 'default_project',
                              service_name: str = None, run_service: bool = False):
    """
    This function does full default Ebonite's pipeline.
    Creates model, pushes it, wraps with a server, builds the docker image and runs it (if needed).

    :param model_name: model name to create.
    :param model_object: object containing model.
    :param model_input: model input.
    :param project_name: project name.
    :param task_name: task name.
    :param service_name: service name. Use model_name if not provided.
    :param run_service: run wrapped model with docker container if provided.
    """
    service_name = service_name or model_name
    ebnt = ebonite.Ebonite.inmemory()

    t = ebnt.get_or_create_task(project_name, task_name)
    model = t.create_and_push_model(model_object, model_input, model_name)

    ebnt.build_service(service_name, model)

    if run_service:
        run_docker_img(service_name, service_name, detach=True)

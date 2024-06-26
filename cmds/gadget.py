"""
Gadget Commands
"""

import config
import utils.color_print as color_print
import utils.checkers as checkers
import utils.system as system_func
from core.env_managers.docker_installer import DockerInstaller
from core.env_managers.kubernetes_installer import KubernetesInstaller
from core.env_managers.kernel_installer import KernelInstaller
from core.env_managers.kata_containers_installer import KataContainersInstaller


def install(args):
    """Install a cloud native gadget with specified version.

    Args:
        args.gadget: Name of the specified cloud native gadget.
        args.verbose: Verbose or not.
        args.http_proxy: HTTP proxy.
        args.https_proxy: HTTPS proxy.
        args.no_proxy: Domains which should be visited without proxy.
      Args below only used when installing Kubernetes:
        args.cni_plugin: Name of CNI plugin.
        args.pod_network_cidr: CIDR of pod network.
        args.domestic: Pull Kubernetes images from domestic source or not.
        args.taint_master: Taint the master node or not.
      Args below only used when installing kata-containers:
        args.kata_runtime_type: Runtime of Kata (e.g. qemu/clh/...).
    Returns:
        None.
    """
    if args.gadget == 'docker':
        if args.default_version:
            install_version = config.docker_default_version
        else:
            install_version = args.version
        temp_gadgets = [{
                'name': 'docker-ce',
                'version': install_version,
            }, {
                'name': 'docker-ce-cli',
                'version': install_version,
            }]
        if checkers.docker_specified_installed(temp_gadgets):
            color_print.debug(
                '{gadget} with version {version} already installed'.format(
                    gadget=args.gadget, version=install_version))
            return
        color_print.debug('uninstalling current docker if applicable')
        
        # ask user whether to uninstall current docker
        loop_count = 0
        while True:
            if loop_count > 10:
                color_print.error_and_exit('too many invalid inputs')
            uninstall = color_print.debug_input(
                'uninstall current docker gadgets? (y/n) ')
            if uninstall == 'y' or uninstall == 'Y':
                DockerInstaller.uninstall(verbose=args.verbose)
                break
            elif uninstall == 'n' or uninstall == 'N':
                break
            else:
                color_print.error('invalid input')
                loop_count += 1
                
        if not DockerInstaller.install_by_version(
                temp_gadgets, verbose=args.verbose):
            color_print.error(
                'failed to install {gadget}'.format(
                    gadget=args.gadget))
        else:
            color_print.debug(
                '{gadget} with version {version} successfully installed'.format(
                    gadget=args.gadget, version=install_version))

    if args.gadget == 'k8s':
        if args.default_version:
            install_version = config.k8s_default_version
        else:
            install_version = args.version
        temp_gadgets = [
            {'name': 'kubelet', 'version': install_version},
            {'name': 'kubeadm', 'version': install_version},
            {'name': 'kubectl', 'version': install_version},
        ]
        if checkers.kubernetes_specified_installed(
                temp_gadgets, verbose=args.verbose):
            color_print.debug(
                '{gadget} with version {version} already installed'.format(
                    gadget=args.gadget, version=install_version))
            return
        if not checkers.docker_installed(verbose=args.verbose):
            color_print.error(
                'it seems docker is not installed or correctly configured')
            color_print.error_and_exit(
                'you can run `metarget gadget install docker --version 18.03.1` to install one')
        color_print.debug('uninstalling current kubernetes if applicable')
        KubernetesInstaller.uninstall(verbose=args.verbose)
        temp_pod_network_cidr = args.pod_network_cidr if args.pod_network_cidr else config.cni_plugin_cidrs[
            args.cni_plugin]
        if not KubernetesInstaller.install_by_version(temp_gadgets,
                                                      cni_plugin=args.cni_plugin,
                                                      pod_network_cidr=temp_pod_network_cidr,
                                                      domestic=args.domestic,
                                                      taint_master=args.taint_master,
                                                      http_proxy=args.http_proxy,
                                                      https_proxy=args.https_proxy,
                                                      no_proxy=args.no_proxy,
                                                      verbose=args.verbose):
            color_print.error(
                'failed to install {gadget}'.format(
                    gadget=args.gadget))
        else:
            color_print.debug(
                '{gadget} successfully installed'.format(
                    gadget=args.gadget))

    if args.gadget == 'kata':
        if args.default_version:
            install_version = config.kata_default_version
        else:
            install_version = args.version
        temp_gadgets = [
            {'name': 'kata-containers', 'version': install_version},
        ]
        if checkers.kata_specified_installed(
                temp_gadgets, kata_runtime_type=args.kata_runtime_type, verbose=args.verbose):
            color_print.debug(
                '{gadget} with version {version} already installed'.format(
                    gadget=args.gadget, version=install_version))
            return
        if not checkers.docker_installed(verbose=args.verbose):
            color_print.error(
                'it seems docker is not installed or correctly configured')
            color_print.error_and_exit(
                'you can run `metarget gadget install docker --version 18.03.1` to install one')
        color_print.debug('uninstalling current kata-containers if applicable')
        KataContainersInstaller.uninstall(verbose=args.verbose)
        if not KataContainersInstaller.install_by_version(
                temp_gadgets, kata_runtime_type=args.kata_runtime_type, verbose=args.verbose):
            color_print.error(
                'failed to install {gadget}'.format(
                    gadget=args.gadget))
        else:
            color_print.debug(
                '{gadget} with version {version} (runtime type: {runtime_type}) successfully installed'.format(
                    gadget=args.gadget, version=install_version, runtime_type=args.kata_runtime_type))

    if args.gadget == 'kernel':
        if args.default_version:
            install_version = config.kernel_default_version
        else:
            install_version = args.version
        temp_gadgets = [
            {'name': 'kernel', 'version': install_version},
        ]
        if checkers.kernel_specified_installed(
                temp_gadgets, verbose=args.verbose):
            color_print.debug(
                '{gadget} with version {version} already installed'.format(
                    gadget=args.gadget, version=install_version))
            return
        if not KernelInstaller.install_by_version(
                temp_gadgets, verbose=args.verbose):
            color_print.error(
                'failed to install {gadget}'.format(
                    gadget=args.gadget))
        else:
            color_print.debug(
                '{gadget} successfully installed'.format(
                    gadget=args.gadget))
            # reboot
            reboot = color_print.debug_input('reboot system now? (y/n) ')
            if reboot == 'y' or reboot == 'Y':
                system_func.reboot_system(verbose=args.verbose)


def remove(args):
    """Remove an installed cloud native gadget.

    Args:
        args.gadget: Name of the specified cloud native gadget.
        args.verbose: Verbose or not.

    Returns:
        None.
    """
    if args.gadget == 'docker':
        DockerInstaller.uninstall(verbose=args.verbose)
        color_print.debug(
            '{gadget} successfully removed'.format(
                gadget=args.gadget))
    if args.gadget == 'k8s':
        KubernetesInstaller.uninstall(verbose=args.verbose)
        color_print.debug(
            '{gadget} successfully removed'.format(
                gadget=args.gadget))
    if args.gadget == 'kata':
        if KataContainersInstaller.uninstall(verbose=args.verbose):
            color_print.debug(
                '{gadget} successfully removed'.format(
                    gadget=args.gadget))
        else:
            color_print.error(
                'failed to remove {gadget}'.format(
                    gadget=args.gadget))
    if args.gadget == 'kernel':
        if args.default_version:
            install_version = config.kernel_default_version
        else:
            install_version = args.version
        temp_gadgets = [
            {'name': 'kernel', 'version': install_version},
        ]
        if KernelInstaller.uninstall(temp_gadgets, verbose=args.verbose):
            color_print.debug(
                '{gadget} successfully removed'.format(
                    gadget=args.gadget))
            # reboot
            reboot = color_print.debug_input('reboot system now? (y/n) ')
            if reboot == 'y' or reboot == 'Y':
                system_func.reboot_system(verbose=args.verbose)
        else:
            color_print.error(
                'failed to remove {gadget}'.format(
                    gadget=args.gadget))
        # color_print.warning(
        #     'removal of {gadget} is unsupported'.format(
        #         gadget=args.gadget))


def retrieve(args):
    """List supported cloud native components.

    Args:
        args: Actually not used.

    Returns:
        None.
    """
    print(' '.join(config.gadgets_supported))

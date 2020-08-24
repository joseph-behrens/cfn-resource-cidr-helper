import logging
import boto3
import ipaddress
import netaddr
import boto3
import uuid
from botocore.exceptions import ClientError
from typing import Any, MutableMapping, Optional

from cloudformation_cli_python_lib import (
    Action,
    HandlerErrorCode,
    OperationStatus,
    ProgressEvent,
    Resource,
    SessionProxy,
    exceptions,
)

from .models import ResourceHandlerRequest, ResourceModel

# Use this logger to forward log messages to CloudWatch Logs.
LOG = logging.getLogger(__name__)
TYPE_NAME = "JB::VPC::CidrCalc"

resource = Resource(TYPE_NAME, ResourceModel)
test_entrypoint = resource.test_entrypoint


class Lister:
    def __init__(self):
        super().__init__()

    def split_by_host_numbers(self, starting_cidr, list_of_num_hosts):
        cidr_list = []
        for num_hosts in list_of_num_hosts:
            next_cidr = CIDR(ipaddress.IPv4Network(
                starting_cidr)[0], num_hosts).get_cidr()
            cidr_list.append(str(next_cidr))
            starting_cidr = ipaddress.IPv4Network(next_cidr)[-1] + 1
        return cidr_list

    def split_by_prefix(self, cidr_to_split, prefix):
        cidr_list = CIDR(cidr_to_split, 0).split_by_prefix(
            cidr_to_split, prefix)
        return cidr_list


class CIDR:
    def __init__(self, starting_address, number_of_hosts):
        super().__init__()
        self.starting_address = starting_address
        self.number_of_hosts = number_of_hosts
        self.map = {
            16: 28,
            32: 27,
            64: 26,
            128: 25,
            256: 24,
            512: 23,
            1000: 22,
            2000: 21,
            4000: 20,
            8000: 19,
            16000: 18,
            32000: 17,
            64000: 16
        }

    def _find_closest(self, num):
        list_of_host_nums = list(self.map.keys())
        closest = min(list_of_host_nums, key=lambda x: abs(x-num))
        if closest < num:
            try:
                closest = list_of_host_nums[list_of_host_nums.index(
                    closest) + 1]
            except IndexError:
                raise ValueError(
                    f"Subnets must be in range of 16 to 64,000 hosts, {num} is outside the upper bound")
        return closest

    def _get_starting_cidr(self):
        suffix = self.map[self._find_closest(self.number_of_hosts)]
        return ipaddress.ip_network(str(self.starting_address) + '/' + str(suffix), False)

    def get_cidr(self):
        starting = self._get_starting_cidr()
        if starting[0] < ipaddress.ip_address(self.starting_address):
            return str(netaddr.IPNetwork(str(starting)).next())
        return str(starting)

    def split_by_prefix(self, cidr_to_split, new_prefix):
        starting = ipaddress.ip_network(cidr_to_split, False)
        cidrs = starting.subnets(new_prefix=new_prefix)
        return [str(address) for address in cidrs]


def set_cidr_list(model):
    if model.HostCounts:
        if not isinstance(model.HostCounts, list) or not all(isinstance(item, int) for item in model.HostCounts):
            raise exceptions.InvalidRequest(
                f"Host number list must be an array of integers, received {model.HostCounts}")
        try:
            cidr_list = Lister().split_by_host_numbers(
                model.CidrToSplit, model.HostCounts)
        except ValueError as value_error:
            raise exceptions.InvalidRequest(str(value_error))
    elif model.PrefixForEvenSplit:
        cidr_list = Lister().split_by_prefix(model.CidrToSplit, model.PrefixForEvenSplit)
    else:
        raise exceptions.InvalidRequest(
            f"Must pass either a host count list or a prefix to split the cidr by")
    return cidr_list


def write_ssm_parameters(name, value, param_type, session):
    try:
        ssm = session.client('ssm')
        ssm.put_parameter(
            Name=name,
            Value=value,
            Type=param_type,
            Overwrite=True
        )
    except ClientError as client_error:
        raise exceptions.InternalFailure(str(client_error))


def get_ssm_parameter(name, session):
    try:
        ssm = session.client('ssm')
        response = ssm.get_parameter(Name=name)
        return response['Parameter']['Value']
    except ClientError:
        raise exceptions.NotFound(TYPE_NAME, name)


def remove_ssm_parameter(name, session):
    try:
        ssm = session.client('ssm')
        ssm.delete_parameter(Name=name)
    except ClientError as client_error:
        raise exceptions.InternalFailure(str(client_error))


@resource.handler(Action.CREATE)
def create_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    model.UID = str(uuid.uuid4())
    model.CIDRs = ','.join(set_cidr_list(model))
    write_ssm_parameters(model.UID + '-CidrList',
                         model.CIDRs, 'StringList', session)
    write_ssm_parameters(model.UID + '-State', 'CREATED', 'String', session)
    progress.status = OperationStatus.SUCCESS
    return progress


@ resource.handler(Action.UPDATE)
def update_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    if not model.UID:
        raise exceptions.NotFound(TYPE_NAME, 'UID')
    state = get_ssm_parameter(model.UID + '-State', session)
    if state == 'DELETED':
        raise exceptions.NotFound(TYPE_NAME, 'UID')
    model.CIDRs = ','.join(set_cidr_list(model))
    write_ssm_parameters(model.UID + '-CidrList',
                         model.CIDRs, 'StringList', session)
    write_ssm_parameters(model.UID + '-State', 'UPDATED', 'String', session)
    progress.status = OperationStatus.SUCCESS
    return progress


@ resource.handler(Action.DELETE)
def delete_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState
    progress: ProgressEvent = ProgressEvent(
        status=OperationStatus.IN_PROGRESS,
        resourceModel=model,
    )
    state = get_ssm_parameter(model.UID + '-State', session)
    if state == 'DELETED':
        progress.status = OperationStatus.FAILED
        raise exceptions.NotFound(TYPE_NAME, 'UID')
    elif state == 'CREATED' or state == 'UPDATED':
        remove_ssm_parameter(model.UID + '-CidrList', session)
        write_ssm_parameters(model.UID + '-State',
                             'DELETED', 'String', session)
        return ProgressEvent(
            status=OperationStatus.SUCCESS,
            resourceModel=None,
        )
    else:
        raise exceptions.NotFound(TYPE_NAME, state)


@ resource.handler(Action.READ)
def read_handler(
    session: Optional[SessionProxy],
    request: ResourceHandlerRequest,
    callback_context: MutableMapping[str, Any],
) -> ProgressEvent:
    model = request.desiredResourceState

    if get_ssm_parameter(model.UID + '-State', session) == 'DELETED':
        raise exceptions.NotFound(TYPE_NAME, 'UID')

    model.CIDRs = get_ssm_parameter(
        model.UID + '-CidrList', session)

    return ProgressEvent(
        status=OperationStatus.SUCCESS,
        resourceModel=model,
    )

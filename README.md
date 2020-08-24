# JB::VPC::CidrCalc

The purpose of this resource is to provide more tools to building subnet CIDRs within CloudFormation than the current option available in [Fn::Cidr](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-cidr.html) which currently only allows you to create a number of CIDR blocks of a given bit size from a larger starting CIDR.

## Current Functionality

The following shows current functionality that can be used by this resource type and instructions on usage.

### Create CIDRs from List of Number of Hosts

By passing in a beginning IP address and a list of the number of hosts a list will be created of CIDR blocks to fit each of the number of hosts in the list in order. The current version does not help with saving addresses that may need to be skipped because of block sizes, though that is a planned enhancement.

#### Example

To create a list of CIDR blocks, first block you want 64 hosts to fit, next needs 128 hosts, third needs 64 hosts, and so on.

```yaml
CidrBuilderExampleResource:
    Type: JB::VPC::CidrCalc
    Properties:
        CidrToSplit: "10.0.0.0/24"
        HostCounts:
            - 64
            - 128
            - 64
            - 250
            - 500
```

The list can be accessed from the CIDRs property of GetAtt. This example would add the list '10.0.0.0/26', '10.0.0.128/25', '10.0.1.0/26', '10.0.2.0/24', '10.0.4.0/23' to the 'GeneratedCidrList' output of the Stack.

```yaml
Outputs:
    GeneratedCidrList:
        Value: !GetAtt CidrBuilderExampleResource.CIDRs
```

This example would select the third element, '10.0.1.0/26', to set as the CidrBlock for the subnet.

```yaml
SubnetOne:
    Type: AWS::EC2::Subnet
    Properties:
      AvailabilityZone: zone-id
      VpcId: vpc-id
      CidrBlock: !Select [2, !Split [',', !GetAtt CidrBuilderExampleResource.CIDRs]]
      Tags:
        - Key: keyname
          Value: value
```


### Split the full given CIDR evenly by a provided prefix

Rather than providing a set number of blocks and the bits wanted like the Fn::Cidr tool this will allow you to pass in a CIDR range such as '10.0.0.0/24' and then a smaller prefix to evenly split the CIDR by, such as '/26'

#### Example

```yaml
CidrBuilderExampleResource:
    Type: JB::VPC::CidrCalc
    Properties:
        CidrToSplit: "10.0.0.0/24"
        PrefixForEvenSplit: 26
```

Accessing the list is the same as the previous example. This time we'd get an evenly distributed number of /26 CIDR blocks, '10.0.0.0/26', '10.0.0.64/26', '10.0.0.128/26', '10.0.0.192/26'

## Planned Enhancements

- **HostCounts**: Provide a property to show a list of skipped IPs
- **HostCounts**: Track skipped IPs and if a host number fits within a block that was skipped, use those IPs
- **HostCounts**: Handling requests with too many hosts for given CIDR
- **Prefix**: Friendly message if prefix is bigger than existing CIDR
- Template validates that only one of HostCounts or Prefix parameters is passed in
- Allow for selecting a position of the list without having to first split the string
- Other suggestions????
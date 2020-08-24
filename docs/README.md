# JB::VPC::CidrCalc

An example resource schema demonstrating some basic constructs and validation rules.

## Syntax

To declare this entity in your AWS CloudFormation template, use the following syntax:

### JSON

<pre>
{
    "Type" : "JB::VPC::CidrCalc",
    "Properties" : {
        "<a href="#cidrtosplit" title="CidrToSplit">CidrToSplit</a>" : <i>String</i>,
        "<a href="#hostcounts" title="HostCounts">HostCounts</a>" : <i>[ Double, ... ]</i>,
        "<a href="#prefixforevensplit" title="PrefixForEvenSplit">PrefixForEvenSplit</a>" : <i>Double</i>,
    }
}
</pre>

### YAML

<pre>
Type: JB::VPC::CidrCalc
Properties:
    <a href="#cidrtosplit" title="CidrToSplit">CidrToSplit</a>: <i>String</i>
    <a href="#hostcounts" title="HostCounts">HostCounts</a>: <i>
      - Double</i>
    <a href="#prefixforevensplit" title="PrefixForEvenSplit">PrefixForEvenSplit</a>: <i>Double</i>
</pre>

## Properties

#### CidrToSplit

The CIDR block to split into subnets

_Required_: No

_Type_: String

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### HostCounts

List of the number of hosts needed in each subnet

_Required_: No

_Type_: List of Double

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

#### PrefixForEvenSplit

A prefix higher than the given CIDR to do an even split against

_Required_: No

_Type_: Double

_Update requires_: [No interruption](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-updating-stacks-update-behaviors.html#update-no-interrupt)

## Return Values

### Ref

When you pass the logical ID of this resource to the intrinsic `Ref` function, Ref returns the UID.

### Fn::GetAtt

The `Fn::GetAtt` intrinsic function returns a value for a specified attribute of this type. The following are the available attributes and sample return values.

For more information about using the `Fn::GetAtt` intrinsic function, see [Fn::GetAtt](https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/intrinsic-function-reference-getatt.html).

#### UID

Unique ID of the resource

#### CIDRs

The generated list of CIDR blocks


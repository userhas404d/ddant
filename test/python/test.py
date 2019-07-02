import boto3
import click
import json

# configure the boto3 client
ec2_client = boto3.client('ec2', region_name='us-east-1')


def describe_network_acls(**kwargs):
    """Describe network ACLs provided a VPC-id."""
    response = ec2_client.describe_network_acls(
        **kwargs,
        DryRun=False,
        MaxResults=1000
    )
    return response['NetworkAcls']


def describe_routes(**kwargs):
    """Describe routes provided a VPC id"""
    response = ec2_client.describe_route_tables(
        **kwargs,
        DryRun=False
    )
    return response['RouteTables']


def describe_subnets(**kwargs):
    """Describe subnets provided a VPC id"""
    response = ec2_client.describe_subnets(
        **kwargs,
        DryRun=False
    )
    return response['Subnets']


def describe_security_groups(**kwargs):
    """Describe security groups provided a VPC id."""

    response = ec2_client.describe_security_groups(
        **kwargs,
        DryRun=False
    )
    return response['SecurityGroups']


def render(**kwargs):
    """Return describe actions as json."""
    json_blobs = {
        "subnets": describe_subnets(**kwargs),
        "nacls": describe_network_acls(**kwargs),
        "routes": describe_routes(**kwargs),
        "security_groups": describe_security_groups(**kwargs)
    }
    for blob in json_blobs:
        f = open("ddant-{}.json".format(blob), "w+")
        f.write(json.dumps(json_blobs[blob], indent=4, sort_keys=True))
        # print("Wrote {} describe results to disk".format(blob))


@click.command()
@click.option("--vpc", prompt="Id of the Target VPC",
              help="Number of greetings.")
@click.option("--path", default="",
              help="Path of the rendered template.")
def json_gen(vpc, path):
    """Simple program that greets NAME for a total of COUNT times."""
    Filters = [
            {
                'Name': 'vpc-id',
                'Values': [
                    vpc,
                ]
            },
        ]
    render(Filters=Filters)


if __name__ == '__main__':
    json_gen()
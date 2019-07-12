import boto3
import click
import html
import json
import random
import string

from jinja2 import Environment, FileSystemLoader


# configure the boto3 client
ec2_client = boto3.client('ec2', region_name='us-east-1')

# configure jinja
env = Environment(loader=FileSystemLoader('templates'))


def randomStringDigits(stringLength=20):
    """Generate a random string of letters and digits """
    lettersAndDigits = string.ascii_letters + string.digits
    return ''.join(random.choice(lettersAndDigits) for i in range(stringLength))


def render_template(file, **variables):
    """Renders a jinja template."""
    template = env.get_template(file)
    return template.render(**variables)


def json_pretty_print(json_obj):
    """Return pretty printed JSON obj."""
    return json.dumps(json_obj, indent=4, separators=(',', ': '))


class cell:
    def __init__(
        self,
        count=0,
        value="",
        xpos=0,
        ypos=0,
        height=0,
        width=0,
        template_path="",
        additional_data={},
        target="",
    ):
        self.id = "{}-{}".format(randomStringDigits(), count)
        self.count = count
        self.value = self.render_value(value, template_path)
        self.xpos = xpos
        self.ypos = ypos
        self.height = height
        self.width = width
        self.template_path = template_path
        self.additional_data = additional_data
        self.target = target

    def get(self):
        return {
            "id": self.id,
            "count": self.count,
            "value": self.value,
            "xpos": self.xpos,
            "ypos": self.ypos,
            "height": self.height,
            "width": self.width,
            "additional_data": self.additional_data,
            "source": self.id,
            "target": self.target
        }

    def render_value(self, value, template_path):
        if value:
            return html.escape(
                render_template(
                    template_path,
                    **value
                )).replace("\n", "")
        else:
            return value


def wrap_cells(rendered_cells):
    """Wraps cells into groups of three."""
    wrapped_cells = []

    xpos_count = 0
    ypos_count = 0
    blob_counter = 0
    for cell_blob in rendered_cells:
        if blob_counter % 3 == 0:
            xpos_count = 0
            ypos_count += 1
        cell_blob['group']['xpos'] = (
          cell_blob['group']['xpos'] +
          cell_blob['group']['width']*xpos_count
        )
        cell_blob['group']['ypos'] = (
          cell_blob['group']['ypos'] +
          cell_blob['group']['height']*ypos_count
        )
        blob_counter += 1
        xpos_count += 1
        wrapped_cells.append(cell_blob)

    return wrapped_cells


def describe_security_groups(**kwargs):
    """Describe security groups provided a VPC id."""

    response = ec2_client.describe_security_groups(
        **kwargs,
        DryRun=False
    )
    return response['SecurityGroups']


def generate_sgs_cells(security_groups):
    count = 0
    rendered_sgs = []

    xpos = 870.5
    ypos = 1160

    for security_group in security_groups:

        group_cell = cell(
            count=count,
            value="",
            xpos=xpos,
            ypos=ypos,
            width=890,
            height=490
        ).get()

        container_cell = cell(
            count=count,
            value="",
            width=group_cell['width'],
            height=490
            ).get()

        description_text_cell = cell(
            count=count,
            value=security_group,
            xpos=30,
            ypos=40,
            width=890,
            height=110,
            template_path='SG_Description.html',
            additional_data=security_group
            ).get()

        inbound_rules_cell = cell(
            count=count,
            value=security_group,
            xpos=30,
            ypos=180,
            width=490,
            height=260,
            template_path='SG_Inbound.html'
            ).get()

        outbound_rules_cell = cell(
            count=count,
            value=security_group,
            xpos=30 + 490,
            ypos=180,
            width=490,
            height=260,
            template_path='SG_Outbound.html'
            ).get()

        sg_cell = {
            "group": group_cell,
            "container": container_cell,
            "description_text": description_text_cell,
            "inbound_rules": inbound_rules_cell,
            "outbound_rules": outbound_rules_cell
        }

        count = count+1
        rendered_sgs.append(sg_cell)

    return rendered_sgs


def describe_network_acls(**kwargs):
    """Describe network ACLs provided a VPC-id."""
    response = ec2_client.describe_network_acls(
        **kwargs,
        DryRun=False,
        MaxResults=1000
    )
    return response['NetworkAcls']


def generate_nacl_cells(network_acls):
    """Generate the NACL cell."""

    count = 0
    xpos = 0
    ypos = 0
    nacl_cells = []

    for nacl in network_acls:

        group_cell = cell(
            count=count,
            value="",
            xpos=xpos,
            ypos=ypos,
            width=1170,
            height=490
        ).get()

        container_cell = cell(
                count=count,
                value="",
                width=group_cell['width'],
                height=490
                ).get()

        description_text_cell = cell(
            count=count,
            value=nacl,
            xpos=30,
            ypos=40,
            width=930,
            height=110,
            template_path='NACL_Description.html',
            additional_data=nacl
            ).get()

        inbound_rules_cell = cell(
            count=count,
            value=nacl,
            xpos=30,
            ypos=180,
            width=490,
            height=260,
            template_path='NACL_Ingress.html'
            ).get()

        outbound_rules_cell = cell(
            count=count,
            value=nacl,
            xpos=30 + 490,
            ypos=180,
            width=490,
            height=260,
            template_path='NACL_Egress.html'
            ).get()

        nacl_cell = {
            "group": group_cell,
            "container": container_cell,
            "description_text": description_text_cell,
            "ingress_rules": inbound_rules_cell,
            "egress_rules": outbound_rules_cell
        }

        nacl_cells.append(nacl_cell)

    return nacl_cells


def get_nacl_to_route_table_association(nacl_cells, route_table_cells):
    """Creates an arrow between NACLs and RouteTables."""
    updated_nacl_cells = []

    # iterate over each NACL cell
    for nacl_cell in nacl_cells:
        # reference the AWS provided json object within the description_text of the cell
        nacl_associations = nacl_cell['description_text']['additional_data']['Associations']
        # iterate over each route table cell
        for route_table_cell in route_table_cells:
            # reference the AWS provided json object within the description_text of the cell
            for rt_association in route_table_cell['description_text']['additional_data']['Associations']:
                for nacl_association in nacl_associations:
                    try:
                        rt_association_subnet = rt_association['SubnetId']
                    except KeyError:
                        rt_association_subnet = ""
                    if rt_association_subnet == nacl_association['SubnetId']:
                        arrow_to_route_table = cell(
                            count=999,
                            xpos=30,
                            ypos=180,
                            width=440,
                            height=260,
                            target=route_table_cell['group']['id']
                            ).get()
                        nacl_cell.update({"arrow": arrow_to_route_table})
        updated_nacl_cells.append(nacl_cell)
    return updated_nacl_cells


def describe_routes(**kwargs):
    """Describe routes provided a VPC id"""
    response = ec2_client.describe_route_tables(
        **kwargs,
        DryRun=False
    )
    return response['RouteTables']


def generage_route_table_cells(route_tables):
    """Generate the RouteTable Cells."""
    count = 0
    xpos = 0
    ypos = 0
    route_table_cells = []

    for route in route_tables:

        group_cell = cell(
            count=count,
            value="",
            xpos=xpos,
            ypos=ypos,
            width=710,
            height=390
        ).get()

        container_cell = cell(
                count=count,
                value="",
                width=group_cell['width'],
                height=390
                ).get()

        description_text_cell = cell(
            count=count,
            value=route,
            xpos=30,
            ypos=40,
            width=710,
            height=110,
            template_path='Route_Description.html',
            additional_data=route
            ).get()

        route_table_cell = cell(
            count=count,
            value=route,
            xpos=30,
            ypos=180,
            width=440,
            height=260,
            template_path='RouteTable.html'
            ).get()

        route_table_cell = {
            "group": group_cell,
            "container": container_cell,
            "description_text": description_text_cell,
            "routes": route_table_cell
        }
        route_table_cells.append(route_table_cell)

    return route_table_cells


def describe_subnets(**kwargs):
    """Describe subnets provided a VPC id"""
    response = ec2_client.describe_subnets(
        **kwargs,
        DryRun=False
    )
    return response['Subnets']


def generate_subnet_cells(subnets):
    """Generate subnet cells."""
    count = 0
    xpos = 0
    ypos = 0
    subnet_cells = []

    for subnet in subnets:

        group_cell = cell(
            count=count,
            value="",
            xpos=xpos,
            ypos=ypos,
            width=710,
            height=390
        ).get()

        container_cell = cell(
                count=count,
                value="",
                width=group_cell['width'],
                height=390
                ).get()

        description_text_cell = cell(
            count=count,
            value=subnet,
            xpos=30,
            ypos=40,
            width=710,
            height=110,
            template_path='Subnet_Description.html',
            additional_data=subnet
            ).get()

        subnet_cell = {
            "group": group_cell,
            "container": container_cell,
            "description_text": description_text_cell
        }
        subnet_cells.append(subnet_cell)

    return subnet_cells


def get_subnet_to_nacl_association(subnet_cells, nacl_cells):
    """Creates an arrow between Subnets and NACLs."""
    updated_subnet_cells = []

    for subnet_cell in subnet_cells:
        subnet_id = subnet_cell['description_text']['additional_data']['SubnetId']
        for nacl_cell in nacl_cells:
            for association in nacl_cell['description_text']['additional_data']['Associations']:
                if association['SubnetId'] == subnet_id:
                    arrow_to_nacl = cell(
                        count=999,
                        xpos=30,
                        ypos=180,
                        width=440,
                        height=260,
                        target=nacl_cell['group']['id']
                        ).get()
                    subnet_cell.update({"arrow": arrow_to_nacl})
        updated_subnet_cells.append(subnet_cell)
    return updated_subnet_cells


def render_drawing(**kwargs):
    """Renders Completed Drawing."""

    security_group_cells = wrap_cells(generate_sgs_cells(
        describe_security_groups(**kwargs)))

    nacl_cells = generate_nacl_cells(describe_network_acls(**kwargs))

    route_table_cells = generage_route_table_cells(describe_routes(**kwargs))

    subnet_cells = generate_subnet_cells(describe_subnets(**kwargs))

    associated_subnet_cells = (
        get_subnet_to_nacl_association(subnet_cells, nacl_cells))
    associated_nacl_cells = (
        get_nacl_to_route_table_association(nacl_cells, route_table_cells))

    template = render_template(
        'DrawioTemplate.xml',
        security_group_cells=security_group_cells,
        nacl_cells=associated_nacl_cells,
        route_table_cells=route_table_cells,
        subnet_cells=associated_subnet_cells
        )
    return template


# render_drawing()

@click.command()
@click.option("--vpc", prompt="Id of the Target VPC",
              help="Id of the Target VPC.")
@click.option("--path", default="",
              help="Path of the rendered template.")
def render(vpc, path):
    """Simple program that creates a draw.io diagram provided a targeted VPC id."""
    Filters = [
            {
                'Name': 'vpc-id',
                'Values': [
                    vpc,
                ]
            },
        ]
    if path:
        f = open("{}/ddant-{}.xml".format(path, vpc), "w+")
    else:
        f = open("ddant-{}.xml".format(vpc), "w+")
    f.write(render_drawing(Filters=Filters))


if __name__ == '__main__':
    render()

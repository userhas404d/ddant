import boto3
import click
import html
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


class cell:
    def __init__(
        self,
        count=0,
        value="",
        xpos=0,
        ypos=0,
        height=0,
        width=0,
        template_path=""
    ):
        self.id = "{}-{}".format(randomStringDigits(), count)
        self.value = self.render_value(value, template_path)
        self.xpos = xpos
        self.ypos = ypos
        self.height = height
        self.width = width
        self.template_path = template_path

    def get(self):
        return {
            "id": self.id,
            "value": self.value,
            "xpos": self.xpos,
            "ypos": self.ypos,
            "height": self.height,
            "width": self.width
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
            template_path='SG_Description.html'
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
            template_path='NACL_Description.html'
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
            template_path='Route_Description.html'
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
            "routes": route_table_cell,
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
            template_path='Subnet_Description.html'
            ).get()

        subnet_cell = {
            "group": group_cell,
            "container": container_cell,
            "description_text": description_text_cell
        }
        subnet_cells.append(subnet_cell)

    return subnet_cells

def render_drawing(**kwargs):
    """Renders Completed Drawing."""

    template = render_template(

        'DrawioTemplate.xml',

        security_group_cells=wrap_cells(generate_sgs_cells(
        describe_security_groups(**kwargs))),

        nacl_cells=generate_nacl_cells(describe_network_acls(**kwargs)),

        route_table_cells=generage_route_table_cells(describe_routes(**kwargs)),

        subnet_cells=generate_subnet_cells(describe_subnets(**kwargs))
        )
    return template


# render_drawing()

@click.command()
@click.option("--vpc", prompt="Id of the Target VPC",
              help="Number of greetings.")
@click.option("--path", default="",
              help="Path of the rendered template.")
def render(vpc, path):
    """Simple program that greets NAME for a total of COUNT times."""
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

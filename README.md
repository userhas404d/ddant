# DDANDT

Dynamic Draw.io AWS Network Diagramming Tool

## What is it

Some python, Jinja, html, and xml all ~~rolled~~ hacked together to create a quick and dirty VPC drawing.

## What you get

Draw.io cell groups with the following resources associated with the target VPC:

- Routes
- Security Groups
- NACLs

## Requirements

- Read access to the target AWS resources
- python 3.x+

## How to use it

1. Configure your [aws cli](https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html#cli-quick-configuration) env
2. Run `ddant.py` against your target VPC

```bash
python3 ddant.py --vpc vpc-1234abcd
```

1. Open the resulting xml document (`vpc-1234abcd.xml`) in draw.io. The default path is the `ddant` directory
2. Move the drawing's content around to your hearts content

## Who is it for

Anyone who needs a quick and dirty VPC drawing (targets a single vpc for now), or anyone else who wants to take this project and build on it.

## But why

I wrote this because I needed a way to map a large AWS project and didn't want to have to bother with manual entry. That and the csv import capability of draw.io just wasn't cutting it for what I needed.

There are other tools like [cloudcraft](https://cloudcraft.co/) that will do this (and way more efficiently) but SaaS just wasn't an option for the project this was originally intended for.

## References

- [AWS VPC Security Diagram](https://docs.aws.amazon.com/vpc/latest/userguide/images/security-diagram.png)
- [mxgraph tutorial](https://jgraph.github.io/mxgraph/docs/tutorial.html)
- [mxgraph layout docs](https://jgraph.github.io/mxgraph/docs/js-api/files/layout/mxStackLayout-js.html)
- [url-encode-decode.com](https://www.url-encode-decode.com/)

## ToDo

- [ ] dynamically size container and group cells based on cell content (ie. long sg lists)
- [ ] proper positioning
- [ ] build test env
- [ ] build in targeting by vpc id

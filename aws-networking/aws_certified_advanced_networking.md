## Table of Contents
- [Section 1 - Introduction](#Section-1---Introduction)

### Section 1 - Introduction

Skip.

### Section 2 - AWS Private Link Architecture

#### VPC Endpoint

Assume we have an EC2 that needs to upload to S3. We don't want to send traffic across the internet due to latency issues. If EC2 and S3 are in the same region then data can be sent through the AWS internal private link via VPC endpoints.

Example:
- EC2 instance in private subnet
- Create S3 VPC endpoint associated with the EC2 instance's route table
- We can now use `aws s3` commands on the EC2 instance

Without VPC endpoints, EC2 would have to go through the internet OR NAT gateway.

#### VPC Endpoints - Architectural Perspective

Goes through same example for DynamoDB rather than S3. Important note that `aws s3 ls` will return all buckets in all regions, but connecting to buckets outside the EC2 region will not.

#### Gateway VPC Endpoints - Access Control

We want to set up access control policies to VPC endpoints which by default is wide open. We can restrict actions (e.g., `GetObject`, `PutObject`) to specific buckets for certain principals.

```
{
  "Statement": [
    {
      "Sid": "Access-to-specific-bucket-only",
      "Principal": "*",
      "Action": [
        "s3:GetObject",
        "s3:List*",
        "s3:PutObject"
      ],
      "Effect": "Allow",
      "Resource": ["arn:aws:s3:::output-kplabs",
                   "arn:aws:s3:::output-kplabs/*"]
    }
  ]
}
```

#### Understanding Interface VPC Endpoints

There are two types of VPC endpoints: Gateway and Interface. We already discussed Gateway endpoints which have the following properties:
- Created outside your VPC with traffic routed via the route table.
- Cannot use the VPC endpoints directly from VPN or Direct Connect.
- Access policy controlled through IAM-like JSON documents.

Interface VPC endpoints are next-generation VPC endpoints. Interface VPC endpoints have the following properties:
- Created within your VPC.
- Have ENI and private IP.
- Access control through security groups.

#### Implementing Interface Endpoints

Example:
- EC2 instance in private subnet with no internet or NAT gateway.
- Go to Endpoints, create EC2 interface endpoint in private subnet with default security group
- On the EC2 instance `nslookup ec2.us-east-1.amazonaws.com` will resolve to the interface IP
- Run `tcpdump dst port 443` on the EC2 instance, and run `aws ec2 <command>` will show the calls are going to the interface IP

#### Understanding VPC Endpoint Services

VPC endpoint services allow service providers (e.g., New Relic) to create their own app which consumers can use via Private Link. VPC peering is not desired because:
- Service provider and consumer VPCs cannot have overlapping IP ranges.
- VPC peering between many customers can be problematic.

The solution is to create an endpoint service which contains a network load balancer (NLB) distributing requests to service provicer instances. On the consumer side, EC2 instances will upload data via VPC endpoint interface which sends it to the NLB through the VPC endpoint service.

#### Implementing End-to-End VPC Endpoint Service

We first configure the service provider side:
- Create the two instances running NGINX.
- Create NLB with target group pointing to the two instances.
- Go to VPC, Endpoint Services, Create Endpoint Service, select the NLB

Next we configure the consumer side:
- Go to VPC, Create Endpoint, Find Service by Name.
- Search for VPC Endpoint Service we created on the server provider side.
- Now we have to go to server provider side to accept the endpoint connection request.
- On consumer EC2, we can `curl <VPC endpoint>` to hit the NLB and get the NGINX webpage.
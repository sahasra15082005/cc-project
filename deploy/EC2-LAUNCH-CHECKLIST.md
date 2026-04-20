# EC2 Launch Checklist

Use this checklist when creating the AWS infrastructure for this project.

## Recommended defaults

- Region: `ap-south-1`
- AMI: `Amazon Linux 2023`
- Architecture: `64-bit x86`
- Instance type: `t3.micro` for testing or `t3.small` for smoother usage
- Storage: `8 GB gp3`
- Public IP: `Enabled`

## Security group

Create one security group, for example `expense-analyzer-sg`.

Inbound rules:

- `SSH`, `TCP`, port `22`, source `your-public-ip/32`
- `HTTP`, `TCP`, port `80`, source `0.0.0.0/0`
- `Custom TCP`, port `8501`, source `your-public-ip/32` only if you want to test Streamlit directly before Nginx

Outbound rules:

- Keep the default `All traffic` outbound rule

## IAM role

Create an EC2 role, for example `expense-analyzer-ec2-role`, and attach:

- the custom S3 policy from `deploy/iam-policy-s3-template.json`

Replace `YOUR_BUCKET_NAME` before creating the policy.

## S3 bucket

Recommended bucket settings:

- Bucket type: `General purpose`
- Object ownership: `ACLs disabled`
- Block public access: `Enabled`
- Versioning: `Enabled`
- Default encryption: `SSE-S3` or `SSE-KMS`

## User data option

If you want EC2 to install the app automatically on first boot, paste the contents of `deploy/ec2-bootstrap.sh` into EC2 user data.

## After instance launch

Run or verify these on the instance:

```bash
sudo systemctl status expense-analyzer
cat /etc/expense-analyzer.env
curl http://127.0.0.1:8501
```

If Nginx is installed:

```bash
sudo systemctl status nginx
curl http://127.0.0.1
```

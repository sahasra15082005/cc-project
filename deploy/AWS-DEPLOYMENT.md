# AWS Deployment Guide

This project runs as a Streamlit app on an EC2 instance and can archive uploaded CSV files plus generated insight reports to Amazon S3.

## Architecture

- `EC2` runs the Streamlit application
- `S3` stores uploaded CSV files and generated report text files
- `IAM role` lets EC2 access S3 without storing AWS keys in the app

## 1. Create an S3 bucket

Create a private S3 bucket in the same region as your EC2 instance, for example `ap-south-1`.

Recommended settings:

- Keep `Block all public access` enabled
- Enable bucket versioning
- Use default encryption with SSE-S3 or SSE-KMS

## 2. Create an IAM role for EC2

Create an IAM role trusted by `EC2` and attach it to your instance.

Ready-to-edit policy template:

- `deploy/iam-policy-s3-template.json`

Minimum S3 permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::YOUR_BUCKET_NAME",
        "arn:aws:s3:::YOUR_BUCKET_NAME/*"
      ]
    }
  ]
}
```

## 3. Launch the EC2 instance

Recommended starting point:

- AMI: `Amazon Linux 2023`
- Instance type: `t3.small` or `t3.micro` for low traffic
- Storage: `8 GB` or more
- Public IP: `Enabled`
- Security group inbound:
- `22` from your IP only
- `80` from `0.0.0.0/0`
- `8501` from your IP only if you want to test Streamlit directly
- `443` from `0.0.0.0/0` if you later add TLS

Attach the IAM role from step 2 to this instance.

You can also follow:

- `deploy/EC2-LAUNCH-CHECKLIST.md`

## 4. Bootstrap the app on EC2

SSH into the instance and run:

```bash
sudo dnf install -y git
git clone https://github.com/sahasra15082005/cc-project.git
cd cc-project
sudo bash deploy/ec2-bootstrap.sh
```

The bootstrap script:

- clones or updates the app in `/opt/expense-analyzer`
- creates a Python virtual environment
- installs dependencies
- installs a `systemd` service
- starts the Streamlit app on port `8501`

## 5. Configure S3 bucket name

Edit the environment file on the instance:

```bash
sudo vi /etc/expense-analyzer.env
```

Set the real values:

```bash
ENABLE_S3_ARCHIVE=true
S3_BUCKET_NAME=your-real-bucket-name
AWS_REGION=ap-south-1
S3_UPLOAD_PREFIX=uploads
S3_REPORT_PREFIX=reports
```

Then restart the app:

```bash
sudo systemctl restart expense-analyzer
```

An example file is included at:

- `deploy/expense-analyzer.env.example`

## 6. Optional: Put Nginx in front of Streamlit

Install Nginx:

```bash
sudo dnf install -y nginx
sudo cp /opt/expense-analyzer/deploy/nginx-expense-analyzer.conf /etc/nginx/conf.d/expense-analyzer.conf
sudo nginx -t
sudo systemctl enable nginx
sudo systemctl restart nginx
```

This exposes the app on port `80` and proxies traffic to Streamlit on `8501`.

## 7. Verify deployment

Check service health:

```bash
sudo systemctl status expense-analyzer
sudo journalctl -u expense-analyzer -n 100 --no-pager
```

Open in a browser:

```text
http://YOUR_EC2_PUBLIC_IP
```

If you did not install Nginx, use:

```text
http://YOUR_EC2_PUBLIC_IP:8501
```

## 8. Update the app later

On the instance:

```bash
cd /opt/expense-analyzer
sudo git pull --ff-only
sudo /opt/expense-analyzer/.venv/bin/pip install -r requirements.txt
sudo systemctl restart expense-analyzer
```

## Notes

- The app uses the EC2 instance role automatically through `boto3`
- No AWS access keys are needed in source code or environment files
- If `ENABLE_S3_ARCHIVE=false`, the app still works normally without S3

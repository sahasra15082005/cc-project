#!/bin/bash
set -euo pipefail

APP_DIR="/opt/expense-analyzer"
REPO_URL="${REPO_URL:-https://github.com/sahasra15082005/cc-project.git}"

dnf update -y
dnf install -y git python3.11 python3.11-pip

mkdir -p "${APP_DIR}"
if [ ! -d "${APP_DIR}/.git" ]; then
  git clone "${REPO_URL}" "${APP_DIR}"
else
  git -C "${APP_DIR}" pull --ff-only
fi

python3.11 -m venv "${APP_DIR}/.venv"
"${APP_DIR}/.venv/bin/pip" install --upgrade pip
"${APP_DIR}/.venv/bin/pip" install -r "${APP_DIR}/requirements.txt"

install -m 644 "${APP_DIR}/deploy/expense-analyzer.service" /etc/systemd/system/expense-analyzer.service

if [ ! -f /etc/expense-analyzer.env ]; then
  cat <<'EOF' >/etc/expense-analyzer.env
ENABLE_S3_ARCHIVE=true
S3_BUCKET_NAME=replace-with-your-bucket-name
AWS_REGION=ap-south-1
S3_UPLOAD_PREFIX=uploads
S3_REPORT_PREFIX=reports
EOF
fi

systemctl daemon-reload
systemctl enable expense-analyzer
systemctl restart expense-analyzer

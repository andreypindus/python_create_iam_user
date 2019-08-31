# python_create_iam_user
Python3 script for AWS IAM user creation, activates MFA and saves the file with credentials in ./credentials/ path.

Usage:
"create_users.py $username $password $group" (IMPORTANT: only one user can be created during the execution)

Fase1: Script verifies if the user exists, if not, creates a new user. The credentials of a new users will be stored in the path "credentials/credential_username.txt"
Fase2: Verifies if Virtual MFA device exists (for the current user), if not, creates the deviece and enables it. The QR code will be stored in a path "credentials/qr_username.png"

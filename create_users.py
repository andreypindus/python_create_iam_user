import argparse
import boto3
import time
import pyotp
import pathlib


parser = argparse.ArgumentParser()
parser.add_argument("user_name", help="user_name argument is requiered")
parser.add_argument("password", help="password argument is requiered")
parser.add_argument("group", help="group argument is requiered")
args = parser.parse_args()
user_name=args.user_name
temp_pass=args.password
group=args.group

client = boto3.client('iam')

def create_user(user):
    try:
        client.get_user(
            UserName=user
        )
        print("User %s already exists" %user_name)
        pass
    except:
        client.create_user(
            UserName=user
        )
        create_key = client.create_access_key(
            UserName=user
        )
        client.add_user_to_group(
            GroupName=group,
            UserName=user
        )
        client.create_login_profile(
            UserName=user,
            Password=temp_pass,
            PasswordResetRequired=True
        )
        print("User %s created" %user)
        #Get credential values
        access_key = create_key['AccessKey']['AccessKeyId']
        secret_key = create_key['AccessKey']['SecretAccessKey']
        credentials = "AccessKey = %s, SecretKey = %s, Username = %s, Password = %s" %(access_key,secret_key,user_name,temp_pass)
        
        credential_file = "credentials/credentials_%s.txt" %user
        with open(credential_file, 'w') as f:
            f.write(credentials)
        print("Credential file created")

def create_mfa(user):
    try:
        created_device = client.create_virtual_mfa_device(
            VirtualMFADeviceName=user
        )
        print("Virtual MFA created for user %s" %user)

    except:
        print("Virtual MFA device exists")
        exit(0)

    # Serial number
    value_serial=created_device['VirtualMFADevice']['SerialNumber']
    
    # Base32 number
    value_base=created_device['VirtualMFADevice']['Base32StringSeed']
    str_value_base=(str(value_base)).replace("b'", "")
    str_value_base_new = str_value_base.replace("'", "")
    base_32_code = "base_32_code = %s" %str_value_base_new
    # QR code
    qr_code_value = created_device['VirtualMFADevice']['QRCodePNG']
    
    qr_file = 'credentials/qr_%s.png' %user
    with open(qr_file, 'wb') as f:
          f.write(qr_code_value)
    print("QR file created")
    
    credential_file = "credentials/credentials_%s.txt" %user
    with open(credential_file, 'a') as f:
        f.write("\n" + base_32_code)
    print("BASE_CODE added to credential file")

    totp = pyotp.TOTP(value_base)
    command = totp.now()
    print(command)
    command2 = totp.now()
    while command == command2:
        print("Waiting for the next code....")
        time.sleep(5)
        command2 = totp.now()
    print(command2)
    client.enable_mfa_device(
        UserName=user,
        SerialNumber=value_serial,
        AuthenticationCode1=command,
        AuthenticationCode2=command2
    )
    print("Virtual MFA attached to user %s" %user)



def main():
    pathlib.Path('credentials').mkdir(exist_ok=True) 
    create_user(user_name)
    create_mfa(user_name)

if __name__ == "__main__":
    main()
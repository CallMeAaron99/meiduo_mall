from fdfs_client.client import Fdfs_client

client = Fdfs_client('client.conf')

result = client.upload_by_filename('/home/python/Desktop/upload_Images/02.jpeg')

print(result)
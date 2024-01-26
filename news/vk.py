import requests
token="vk1.a.QG6IKCYi17wbV1JtEq_NHHhCyMXz_enHlBOMqgpfCHKd7WhACXk_Bhr7XVqD_6Txjf_Zf4AwsJE0cA-K8K2rwk0KXc6A5r-klyeFITGPQE-bnSunUnmWVtiGRwMbXLk9uv8FouyRCjzb6Kbyn_qph4oK3hEhyujb3Lrn0ExL_55hY_MeQZh5Ntrwwx5qnC6W3tTgcF_dCfdarqgF91i2sw"
ownerid = -50679937
from_group = 1
version_vk = "5.133"

url = "https://api.vk.com/method/wall.post"#https://dev.vk.com/ru/method/wall.post

response = requests.post(
    url = url,
    params= {
        'access_token': token,
        'from_group': from_group,
        'owner_id': ownerid,
        'message': 'hello',
        'v': version_vk,
    }
)

print(response.json())
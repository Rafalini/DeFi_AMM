import json


s =  b'{"Miner":"192.168.10.5:44708","Hash":"AJ8JclsKxA2R/xO1Ox/9JtDRrvIcEZHG7M0tjIS0Jao=","PreviousHash":"ACAAjuevkDQwvWK/Z0cppTmOuHAGIvpCcrUkk0HqIEk=","Nonce":6412,"Transactions":[{"Sender":"192.168.10.6","Reciever":"0xAMM","Amount":"","Token":"ECR17","Sender_signature":"a5f5d547ded956050e883e91f444cc4c60c249cec5fa05ef15f3a9f30e897497"},{"Sender":"0xAMM","Reciever":"192.168.10.6","Amount":"","Token":"ECR3","Sender_signature":"93d8f10c9e5df1498c272eea1510750d6a516e90714424624ff56e4202903f4e"},{"Sender":"192.168.10.6","Reciever":"0xAMM","Amount":"","Token":"ECR17","Sender_signature":"d3afad3057e29cc425bff45bd8e9d5b1f5da63b68810b9a71df5c6b2ee0b8c11"}]}'
a =  b'{"Miner":"192.168.10.5:44708","Hash":"AJ8JclsKxA2R/xO1Ox/9JtDRrvIcEZHG7M0tjIS0Jao=","PreviousHash":"ACAAjuevkDQwvWK/Z0cppTmOuHAGIvpCcrUkk0HqIEk=","Nonce":6412,"Transactions":[{"Sender":"192.168.10.6","Reciever":"0xAMM","Amount":"","Token":"ECR17","Sender_signature":"a5f5d547ded956050e883e91f444cc4c60c249cec5fa05ef15f3a9f30e897497"},{"Sender":"0xAMM","Reciever":"192.168.10.6","Amount":"","Token":"ECR3","Sender_signature":"93d8f10c9e5df1498c272eea1510750d6a516e90714424624ff56e4202903f4e"},{"Sender":"192.168.10.6","Reciever":"0xAMM","Amount":"","Token":"ECR17","Sender_signature":"d3afad3057e29cc425bff45bd8e9d5b1f5da63b68810b9a71df5c6b2ee0b8c11"}]}'

js = json.loads(s)

ar = []
ar += js["Transactions"]

print(len(js["Transactions"]))

js = json.loads(a)
ar += js["Transactions"]

print(len(ar))
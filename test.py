import json

def lambda_handler(event, context):
    #print("Received event: " + json.dumps(event, indent=2))
    res = "test complete !! your value = " + event['key'] + "\n"
    return res  # Echo back the first key value


import json
from pywebpush import webpush, WebPushException

VAPID_CLAIMS = {"sub": "mailto:you@example.com"}

def send_push(subscription_info, title, body):
    try:
        webpush(
            subscription_info=subscription_info,
            data=json.dumps({"title": title, "body": body}),
            vapid_private_key="private_key.pem",
            vapid_claims=VAPID_CLAIMS.copy(),
        )
        return True
    except WebPushException as e:
        print(f"Push failed: {e}")
        return False
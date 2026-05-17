import uuid
def onboard(company, subdomain):
    schema = f"tenant_{uuid.uuid4().hex[:8]}"
    print(f"Creating {schema} for {company}")
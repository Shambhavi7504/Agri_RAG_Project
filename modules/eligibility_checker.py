# modules/eligibility_checker.py
def check_eligibility(user_details, policies):
    """
    user_details: dict with keys like {"state": "Karnataka", "farmer_type": "small", "land_holding": 1}
    policies: list of dicts with eligibility rules
    """

    eligible = []
    for policy in policies:
        rules = policy.get("eligibility", {})

        # State check
        if rules.get("state") not in ["all", user_details["state"]]:
            continue

        # Farmer type check
        if rules.get("farmer_type") not in ["all", user_details["farmer_type"]]:
            continue

        # Landholding check (if given)
        if "land_holding" in rules:
            if not (user_details["land_holding"] <= rules["land_holding"]):
                continue

        eligible.append(policy["policy"])

    return eligible

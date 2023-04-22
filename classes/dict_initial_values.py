#Initialization dictionaries
providers_init = {
    #Other providers
    "Other": {
        "Total Non-Validator Nodes": 0, 
        "Total Validators": 0, 
        "Total Nodes": 0, 
        "Total Stake": 0
        },
    # Other errors
    "Unidentified": {
        "Total Non-Validator Nodes": 0,
        "Total Validators": 0,
        "Total Nodes": 0,
        "Total Stake": 0
    },
    # Private IP addresses, home, or network masks
    "Invalid": {
        "Total Non-Validator Nodes": 0,
        "Total Validators": 0,
        "Total Nodes": 0,
        "Total Stake": 0
    }
}

#Note: There is no other, tracking all continents
location_init = {
    # Other errors
    "Unidentified": {
        "Total Non-Validator Nodes": 0,
        "Total Validators": 0,
        "Total Nodes": 0,
        "Total Stake": 0,
        "Countries": {
            "Unidentified": {
                "Total Non-Validator Nodes": 0,
                "Total Validators": 0,
                "Total Nodes": 0,
                "Total Stake": 0
                }
            }
        },
    # Private IP addresses, home, or network masks
    "Invalid": {
        "Total Non-Validator Nodes": 0,
        "Total Validators": 0,
        "Total Nodes": 0,
        "Total Stake": 0,
        "Countries": {
            "Unidentified": {
                "Total Non-Validator Nodes": 0,
                "Total Validators": 0,
                "Total Nodes": 0,
                "Total Stake": 0
                }
            }
        }
    }

#Flow-Specific Initialization dictionaries
flow_total_stake = {
    "execution": {"active": 0, "total": 0},
    "consensus": {"active": 0, "total": 0},
    "collection": {"active": 0, "total": 0}, 
    "verification": {"active": 0, "total": 0}, 
    "access": {"active": 0, "total": 0}
}

providers_init_flow = {
    "Other": {
        "Execution Nodes": {"active": 0, "total": 0},
        "Consensus Nodes": {"active": 0, "total": 0},
        "Collection Nodes": {"active": 0, "total": 0},
        "Verification Nodes": {"active": 0, "total": 0},
        "Access Nodes": {"active": 0, "total": 0},
        "Total Stake": flow_total_stake,
        "Total Nodes": 0,
        "Total Inactive Nodes": 0
        },
    "Unidentified": {
        "Execution Nodes": {"active": 0, "total": 0},
        "Consensus Nodes": {"active": 0, "total": 0},
        "Collection Nodes": {"active": 0, "total": 0},
        "Verification Nodes": {"active": 0, "total": 0},
        "Access Nodes": {"active": 0, "total": 0},
        "Total Stake": flow_total_stake,
        "Total Nodes": 0,
        "Total Inactive Nodes": 0
    },
    "Invalid": {
        "Execution Nodes": {"active": 0, "total": 0},
        "Consensus Nodes": {"active": 0, "total": 0},
        "Collection Nodes": {"active": 0, "total": 0},
        "Verification Nodes": {"active": 0, "total": 0},
        "Access Nodes": {"active": 0, "total": 0},
        "Total Stake": flow_total_stake,
        "Total Nodes": 0,
        "Total Inactive Nodes": 0
    }
}

#Note: There is no other, tracking all continents
location_init_flow = {
    "Unidentified": {
        "Execution Nodes": {"active": 0, "total": 0},
        "Consensus Nodes": {"active": 0, "total": 0},
        "Collection Nodes": {"active": 0, "total": 0},
        "Verification Nodes": {"active": 0, "total": 0},
        "Access Nodes": {"active": 0, "total": 0},
        "Total Stake": flow_total_stake,
        "Total Nodes": 0,
        "Total Inactive Nodes": 0,
        "Countries": {
            "Unidentified": {
                "Execution Nodes": {"active": 0, "total": 0},
                "Consensus Nodes": {"active": 0, "total": 0},
                "Collection Nodes": {"active": 0, "total": 0},
                "Verification Nodes": {"active": 0, "total": 0},
                "Access Nodes": {"active": 0, "total": 0},
                "Total Stake": flow_total_stake,
                "Total Nodes": 0,
                "Total Inactive Nodes": 0
                }
            }
        },
    "Invalid": {
        "Execution Nodes": {"active": 0, "total": 0},
        "Consensus Nodes": {"active": 0, "total": 0},
        "Collection Nodes": {"active": 0, "total": 0},
        "Verification Nodes": {"active": 0, "total": 0},
        "Access Nodes": {"active": 0, "total": 0},
        "Total Stake": flow_total_stake,
        "Total Nodes": 0,
        "Total Inactive Nodes": 0,
        "Countries": {
            "Unidentified": {
                "Execution Nodes": {"active": 0, "total": 0},
                "Consensus Nodes": {"active": 0, "total": 0},
                "Collection Nodes": {"active": 0, "total": 0},
                "Verification Nodes": {"active": 0, "total": 0},
                "Access Nodes": {"active": 0, "total": 0},
                "Total Stake": flow_total_stake,
                "Total Nodes": 0,
                "Total Inactive Nodes": 0
                }
            }
        }
    }
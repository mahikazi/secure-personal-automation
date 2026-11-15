def request_approval(action_count):
    if action_count == 0:
        print("No permitted actions to approve.")
        return False

    while True:
        response = input(
            f"\nApprove {action_count} permitted file action(s)? (y/n):"
        ).strip().lower()

        if response in ("y","yes"):
            return True

        if response in ("n", "no"):
            return False

        print("Invalid input. Please enter y or no.")
import time
from database import humans_db
from database.schemas import Human

from stripe_api import stripe_api
import stripe

from mongoengine.errors import NotUniqueError


# TODO run this in PROD


def add_stripe_ids_to_all_humans():
    all_humans = Human.objects()  # Retrieve all Human objects from the database

    for human in all_humans:
        try:
            # Skip if the human already has a stripe_customer_id
            if human.stripe_customer_id:
                continue

            # Create a Stripe customer for each human
            customer = stripe_api.create_customer(human.email)
            stripe_customer_id = customer["id"]

            # Update the human's stripe_customer_id in the database
            humans_db.update_human(
                human_id=human.id, update={"stripe_customer_id": stripe_customer_id}
            )
        except stripe.error.RateLimitError:
            # Handle rate limit errors by sleeping for 60 seconds
            time.sleep(10)
        except NotUniqueError:
            # Handle the case where the stripe_customer_id is already in use
            print(f"Stripe customer ID for {human.email} already exists.")
        except Exception as e:
            # Handle other exceptions
            print(f"An error occurred: {e}")


# Run the script
if __name__ == "__main__":
    add_stripe_ids_to_all_humans()

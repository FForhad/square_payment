from django.shortcuts import render
import uuid
from square.client import Client
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .square_config import client
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

@api_view(['POST'])
def process_payment(request):
    try:
        # Extract data from request
        amount = int(request.data.get("amount"))  # Amount in cents (e.g., 1000 for $10.00)
        nonce = request.data.get("nonce")  # Card nonce from Square
        username = request.data.get("username")

        if not nonce or not amount:
            return Response({"error": "Missing 'nonce' or 'amount' in request."}, status=400)

        # Prepare the API request
        payments_api = client.payments
        idempotency_key = str(uuid.uuid4())  # Generate a unique idempotency key to ensure only one transaction is processed

        body = {
            "source_id": nonce,  # Tokenized card information (nonce)
            "amount_money": {
                "amount": amount,  # Amount in cents
                "currency": "USD",  # Use your preferred currency
            },
            "idempotency_key": idempotency_key,  # Unique key for idempotency
            "username": username,
        }
        print(username)

        # Make API call to Square
        result = payments_api.create_payment(body)

        # Check if the payment was successful
        if result.is_success():
            return Response({"status": "success", "data": result.body}, status=status.HTTP_200_OK)
        else:
            # Log any errors returned by Square API
            logger.error(f"Square API Error: {result.errors}")
            return Response({"status": "error", "errors": result.errors}, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        # Catch and log any unexpected errors
        logger.error(f"Error occurred: {str(e)}")
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def test_payment_view(request):
    return render(request, 'test_payment.html')


@api_view(['GET'])
def get_payment_details(request, payment_id):
    """
    API to retrieve payment details using Square's Payment ID.
    """
    try:
        # Use the Payments API to fetch details by payment_id
        # payments_api = client.payments
        result = client.payments.get_payment(payment_id)


        if result.is_success():
            payment_details = result.body
            return Response({
                "status": "success",
                "payment_details": payment_details
            }, status=200)
        else:
            return Response({
                "status": "error",
                "errors": result.errors
            }, status=400)

    except Exception as e:
        return Response({
            "status": "error",
            "message": str(e)
        }, status=500)
    

@api_view(['GET'])
def list_all_payments(request):
    try:
        # Define the time range (e.g., all payments in the last 30 days)
        today = datetime.today()
        last_30_days = today - timedelta(days=30)
        end_date = today.isoformat()
        start_date = last_30_days.isoformat()

        payments = []
        cursor = None
        total_amount = 0  # Variable to hold the total amount

        # Paginate through the payments, fetching them in batches (if needed)
        while True:
            # Make the API call to list payments
            result = client.payments.list_payments(
                begin_time=start_date,
                end_time=end_date,
                cursor=cursor,  # Use cursor to fetch next page
                limit=50  # Adjust this number based on your needs
            )

            if result.is_success():
                payments.extend(result.body.get("payments", []))

                # Add the amount of each payment to the total
                for payment in result.body.get("payments", []):
                    total_amount += payment.get("amount_money", {}).get("amount", 0)

                # If the response contains a cursor, fetch next page
                cursor = result.body.get("cursor")
                if not cursor:
                    break  # No more pages, exit the loop
            else:
                return Response({"status": "error", "errors": result.errors}, status=status.HTTP_400_BAD_REQUEST)

        # Extract payment details
        payment_details = []
        for payment in payments:
            payment_details.append({
                "payment_id": payment.get("id"),
                "username": payment.get("username"),
                "amount_paid": payment.get("amount_money", {}).get("amount"),
                "currency": payment.get("amount_money", {}).get("currency"),
                "payment_status": payment.get("status"),
                "payment_time": payment.get("created_at"),
                "payment_method": payment.get("card_details", {}).get("card", {}).get("brand"),
            })

        return Response({
            "status": "success",
            "data": payment_details,
            "total_amount": total_amount  # Include total amount in the response
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
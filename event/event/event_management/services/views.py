

from django.shortcuts import render
import qrcode
from io import BytesIO
import base64

def services_page(request):
    return render(request, 'services.html')


def book_event(request):
    if request.method == "POST":
        event_name = request.POST.get("event_name")
        payment_method = request.POST.get("payment")

        # Cash on Delivery
        if payment_method == "cod":
            return render(request, 'services/success.html', {
                'event_name': event_name
            })

        # QR Code Payment
        if payment_method == "qr":
            qr_data = f"Payment for {event_name}"

            qr = qrcode.make(qr_data)
            buffer = BytesIO()
            qr.save(buffer, format="PNG")
            qr_base64 = base64.b64encode(buffer.getvalue()).decode()

            return render(request, 'services/qr_payment.html', {
                'qr_code': qr_base64,
                'event_name': event_name
            })

    return render(request, 'services/book_event.html')

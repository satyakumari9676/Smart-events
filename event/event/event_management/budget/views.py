from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pickle
import os
from django.conf import settings
import json

# ✅ Load trained ML model once when server starts
model_path = os.path.join(settings.BASE_DIR, 'budget', 'ml', 'budget_model.pkl')
with open(model_path, 'rb') as f:
    model = pickle.load(f)

def estimate(request):
    prediction = None

    if request.method == "POST":
        guests = int(request.POST['guests'])
        location = int(request.POST['location'])
        catering = int(request.POST['catering'])
        decoration = int(request.POST['decoration'])

        prediction = model.predict([[guests, location, catering, decoration]])
        prediction = round(float(prediction[0]), 2)

    return render(request, 'budget/estimator.html', {'prediction': prediction})


# ✅ API for your JS fetch("/budget/api/predict-budget/")
@csrf_exempt
def predict_budget(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body.decode("utf-8"))

        guests = int(data.get("guests", 0))

        # ✅ location mapping (MUST match training encoding)
        loc_key = data.get("location", "tier2")
        loc_map = {"rural": 0, "tier2": 1, "metro": 2, "premium": 3}
        location = int(loc_map.get(loc_key, 1))

        # ✅ decoration derived from package (MUST match training encoding)
        pkg = data.get("package", "simple")
        pkg_map = {"simple": 0, "basic": 1, "luxury": 2}
        decoration = int(pkg_map.get(pkg, 0))

        # ✅ services list from frontend (example: "bridegroom|food|photo")
        selected_services = data.get("selected_services", "")
        selected_set = set([s for s in selected_services.split("|") if s])

        # ✅ catering derived properly (THIS makes ML change when services change)
        # 0 = no catering, 1 = snack/light, 2 = full catering
        if "food" in selected_set:
            catering = 2
        elif len(selected_set) > 0:
            catering = 1
        else:
            catering = 0

        # ✅ optional: use services_count as extra influence by adjusting catering slightly
        services_count = int(data.get("services_count", len(selected_set)))
        if catering > 0 and services_count >= 6:
            catering = min(2, catering + 0)  # keep 2 max

        # ✅ Predict (model expects 4 features)
        pred = model.predict([[guests, location, catering, decoration]])
        predicted_total = round(float(pred[0]), 2)

        return JsonResponse({
            "predicted_total": predicted_total,
            "debug": {
                "guests": guests,
                "location": location,
                "catering": catering,
                "decoration": decoration,
                "services_count": services_count,
                "selected_services": selected_services
            }
        })

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)

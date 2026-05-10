import os
import glob
import re

FILES = [
    'baby_budget.html',
    'birthday_budget.html',
    'corporate_budget.html',
    'engage_budget.html',
    'festival_budget.html',
    'school_budget.html',
    'shows_budget.html',
    'wedding_budget.html'
]

fetch_injection = """
      // INJECTED BACKEND CALL
      const _guests = parseInt(document.getElementById("guests")?.value || document.getElementById("guestCount")?.value || "50");
      const _totalText = document.getElementById("sumRuleTotal")?.textContent || document.getElementById("grandTotal")?.textContent || "0";
      const _total = parseInt(_totalText.replace(/\D/g, '')) || 0;
      const _eventDate = document.getElementById("eventDate")?.value || new Date().toISOString().split('T')[0];
      const _custName = document.getElementById("custName")?.value || "Customer";
      
      fetch('/api/create-budget-booking/', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
              event_name: document.title.split(' ')[0] + ' Event For ' + _custName,
              event_date: _eventDate,
              guest_count: _guests,
              budget_estimate: _total
          })
      });
"""

def patch_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if "/api/create-budget-booking/" in content:
        print(f"Skipping {path}, already patched")
        return

    # For confirmBooking (alert style)
    if 'setTimeout(() => {\n        alert(' in content:
        content = content.replace(
            'setTimeout(() => {\n        alert(',
            fetch_injection + '\n      setTimeout(() => {\n        alert('
        )
    # For bookEvent (bookingMsg style)
    elif 'bookingMsg.innerHTML = `' in content:
        content = content.replace(
            'bookingMsg.innerHTML = `',
            fetch_injection + '\n      bookingMsg.innerHTML = `'
        )
    else:
        print(f"Warning: could not patch {path}")

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Patched {path}")

base = 'd:/event/event/event_management/templates/'
for file in FILES:
    patch_file(os.path.join(base, file))

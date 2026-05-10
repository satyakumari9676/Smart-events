import os, glob, re

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

replacement = '''
  function confirmBooking(){ _apiBookEvent(); }
  function bookEvent(){ _apiBookEvent(); }
  
  function _apiBookEvent() {
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
      }).then(r => r.json()).then(d => {
          if(d.success) {
              window.location.href = '/checkout/' + d.booking_id + '/';
          } else {
              alert("Error: " + d.error);
          }
      });
  }
'''

base = 'd:/event/event/event_management/templates/'
for file in FILES:
    path = os.path.join(base, file)
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # We will simply find "function confirmBooking(){...}" using regex block replacement
    # Or replace "function confirmBooking()" with "function old_cb()"
    content = re.sub(r'function confirmBooking\(\)\{.*?(?=\n\s*function|\n\s*setTomorrowMinDate|\n\s*render|\n\s*</script>)', 'function old_confirmBooking(){}', content, flags=re.DOTALL)
    content = re.sub(r'function bookEvent\(\)\{.*?(?=\n\s*function|\n\s*resetAll|\n\s*render|\n\s*</script>)', 'function old_bookEvent(){}', content, flags=re.DOTALL)
    
    # Also find and remove the old INJECTED BACKEND CALL if exists
    content = re.sub(r'// INJECTED BACKEND CALL.*?\}\);', '', content, flags=re.DOTALL)
    
    # Prepend replacement to script
    content = content.replace('<script>', '<script>'+replacement)
    
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
        print("Fixed", path)


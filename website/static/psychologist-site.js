// psychologist-site.js

document.addEventListener("DOMContentLoaded", () => {
 
  document.querySelectorAll("a.nav-link").forEach((link) => {
    link.addEventListener("click", function (e) {
      const href = this.getAttribute("href") || "";

      if (href.startsWith("#")) {
        const target = document.querySelector(href);
        if (target) {
          e.preventDefault();
          target.scrollIntoView({ behavior: "smooth" });
        }
      }
    });
  });

  
  const nav = document.querySelector("nav");
  if (nav) {
    const toggleShadow = () => {
      if (window.scrollY > 50) nav.classList.add("shadow");
      else nav.classList.remove("shadow");
    };
    toggleShadow();
    window.addEventListener("scroll", toggleShadow);
  }


  const dateInput = document.getElementById("date");
  const timeSelect = document.getElementById("time");
  const slotsScript = document.getElementById("slots-data");

  if (dateInput && timeSelect && slotsScript) {
    let slotsByDate = {};
    try {
      slotsByDate = JSON.parse(slotsScript.textContent || "{}");
    } catch (e) {
      console.error("Invalid slots JSON:", e);
    }

    const setTimeOptions = (dateStr) => {
      timeSelect.innerHTML = `<option value="">Select time</option>`;

      const slots = slotsByDate[dateStr] || [];

      if (!Array.isArray(slots) || slots.length === 0) {
        const opt = document.createElement("option");
        opt.value = "";
        opt.textContent = "No slots available";
        opt.disabled = true;
        timeSelect.appendChild(opt);
        timeSelect.disabled = true;
        return;
      }

      timeSelect.disabled = false;
      slots.forEach((t) => {
        const opt = document.createElement("option");
        opt.value = t;         
        opt.textContent = t;   
        timeSelect.appendChild(opt);
      });
    };

    dateInput.addEventListener("change", () => setTimeOptions(dateInput.value));

    if (dateInput.value) setTimeOptions(dateInput.value);
  }


  const bookingForm = document.getElementById("bookingForm");
  if (bookingForm) {
    bookingForm.addEventListener("submit", function () {
      const nameField = document.getElementById("fullname");
      const name = nameField ? nameField.value.trim() : "there";

      alert(`Thank you, ${name}! Your appointment request has been received.`);
    });
  }
});
// psychologist-site.js

document.querySelectorAll('a.nav-link').forEach(link => {
  link.addEventListener('click', function(e) {
    const href = this.getAttribute('href');
    if (href && href.startsWith('#')) {
      e.preventDefault();
      const target = document.querySelector(href);
    if (target) {
      target.scrollIntoView({ behavior: 'smooth' });
    }
  }
  });
});

const form = document.getElementById('bookingForm');
if (bookingForm) {
  form.addEventListener('submit', function(e) {
    const name = document.getElementById('fullname');
    const email = document.getElementById('email');
    const date = document.getElementById('date');
    const message = document.getElementById('message');

      if (!fullname?.value.trim() || !email?.value.trim() || !date?.value) {
        e.preventDefault();
        alert("Please fill in name, email and date.");
        return;
      }

    alert("Thank you! Your appointment request has been submitted. Dr. Stellah will contact you soon.");
    
  });
}


window.addEventListener('scroll', () => {
  const nav = document.querySelector('nav');
  if (nav) {
    if (window.scrollY > 50) {
      nav.classList.add('shadow');
    } else {
      nav.classList.remove('shadow');
    }
  }
});
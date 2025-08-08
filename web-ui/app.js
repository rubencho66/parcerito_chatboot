document.addEventListener("DOMContentLoaded", () => {
  // Registro
  const registerForm = document.getElementById("register-form");
  if (registerForm) {
    registerForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const name = document.getElementById("name").value;
      const email = document.getElementById("email").value;
      const password = document.getElementById("password").value;

      try {
        const response = await fetch("http://localhost:8000/users", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ name, email, password }),
        });

        if (response.ok) {
          alert("Registro exitoso");
          window.location.href = "index.html";
        } else {
          const error = await response.json();
          alert("Error en el registro: " + (error.detail || response.statusText));
        }
      } catch (error) {
        alert("Error en la conexión: " + error.message);
      }
    });
  }

  // Login
  const loginForm = document.getElementById("login-form");
  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const email = document.getElementById("login-email").value;
      const password = document.getElementById("login-password").value;

      try {
        const response = await fetch("http://localhost:8000/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({ email, password }),
        });

        const data = await response.json();

        if (response.ok) {
          localStorage.setItem("token", data.access_token || "");
          window.location.href = "chat.html";
        } else {
          alert("Error en el login: " + (data.detail || response.statusText));
        }
      } catch (error) {
        alert("Error en la conexión: " + error.message);
      }
    });
  }

  // Chat
  const chatForm = document.getElementById("chat-form");
  if (chatForm) {
    chatForm.addEventListener("submit", async (e) => {
      e.preventDefault();

      const message = document.getElementById("message").value;
      const token = localStorage.getItem("token");

      try {
        const response = await fetch("http://localhost:8000/chat", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token,
          },
          body: JSON.stringify({ message }),
        });

        const data = await response.json();

        if (response.ok) {
          document.getElementById("chat-output").innerHTML += `<p><strong>Tú:</strong> ${message}</p>`;
          document.getElementById("chat-output").innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
          document.getElementById("message").value = "";
        } else {
          alert("Error en el chat: " + (data.detail || response.statusText));
        }
      } catch (error) {
        alert("Error en la conexión: " + error.message);
      }
    });
  }
});